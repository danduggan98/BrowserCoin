from browsercoin.src import blockchain, masternode, params
from flask import Flask, request, Response
import requests
import threading, atexit
import json
import jsonpickle
import rsa

BLOCK_TIME = 10 #params.BLOCK_SPACING
dataLock = threading.Lock()

master = masternode.MasterNode()
block_thread = threading.Thread()
PORT = 3000 #GET THIS FROM ENVIRONMENT

def start_masternode():
    app = Flask(__name__)
    
    # //////// API Handlers \\\\\\\\ #
    @app.route('/masternode/transaction', methods=['POST'])
    def recieve_tx():
        if not request.json:
            return Response('Request rejected - transaction data required', status=400, mimetype='application/json')

        tx: blockchain.Transaction = jsonpickle.decode(request.json)

        if None in (tx.timestamp, tx.transfer_amount, tx.sender, tx.recipient, tx.hash):
            return Response('Request rejected - at least one parameter is missing', status=400, mimetype='application/json')
        
        if tx.signature is None:
            return Response('Request rejected - signature is missing or invalid', status=400, mimetype='application/json')
        
        #Pass request to all nodes, track how many accept it
        num_accepted = 0

        for node in master.nodes:
            node_route = node + '/node/transaction'
            response = requests.post(node_route, json=request.json)

            if response.status_code == 202:
                num_accepted += 1
        
        response_msg = f'Request accepted - Transaction added to mempool in ({num_accepted}/{len(master.nodes)}) nodes'
        return Response(response_msg, status=200, mimetype='application/json')
    
    # //////// Methods to run the block selection lottery \\\\\\\\ #

    def stop_adding_blocks():
        global block_thread
        block_thread.cancel()
    
    def add_block():
        global master
        global block_thread

        with dataLock:
            master.run_lottery()

        block_thread = threading.Timer(BLOCK_TIME, add_block, ())
        block_thread.start()

    def begin_adding_blocks():
        global block_thread
        block_thread = threading.Timer(BLOCK_TIME, add_block, ())
        block_thread.start()
    
    begin_adding_blocks()
    atexit.register(stop_adding_blocks) #Stop processing when server ends
    return app.run(debug=True, port=PORT, use_reloader=False)

app = start_masternode()
