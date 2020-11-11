from browsercoin.src import blockchain, masternode, params
from flask import Flask, request, Response
import requests
import threading, atexit
import json
import jsonpickle
import rsa

BLOCK_TIME = params.BLOCK_SPACING
dataLock = threading.Lock()

master = masternode.MasterNode()
block_thread = threading.Thread()
PORT = 3000 #GET THIS FROM ENVIRONMENT

def start_masternode():
    app = Flask(__name__)
    
    # //////// API Handlers \\\\\\\\ #

    #Receive a transaction and pass it to the nodes
    @app.route('/masternode/transaction', methods=['POST'])
    def recieve_tx():
        if not request.json:
            return Response('Request rejected - Transaction data required', status=400, mimetype='application/json')

        try:
            tx: blockchain.Transaction = jsonpickle.decode(request.json)
        except:
            return Response('Request rejected - Transaction data required', status=400, mimetype='application/json')

        if None in (tx.timestamp, tx.transfer_amount, tx.sender, tx.recipient, tx.hash):
            return Response('Request rejected - At least one parameter is missing', status=400, mimetype='application/json')
        
        if tx.signature is None:
            return Response('Request rejected - Signature is missing or invalid', status=400, mimetype='application/json')
        
        #Pass request to all nodes, track how many accept it
        num_accepted = 0
        num_online = 0

        for node in master.nodes:
            node_route = node + '/node/transaction'
            
            try:
                response = requests.post(node_route, json=request.json)
            except:
                continue

            num_online += 1

            if response.status_code == 202:
                num_accepted += 1
        
        response_msg = f'Request completed - Transaction added to mempool in ({num_accepted}/{num_online}) active nodes'
        return Response(response_msg, status=200, mimetype='application/json')
    
    #Get a particular address' balance
    @app.route('/api/balance/<address>', methods=['GET'])
    def balance(address):
        key = rsa.PublicKey(int(address), 65537)
        balance = str(master.chain.get_balance(key))
        return Response(balance, status=200, mimetype='application/json')
    
    @app.route('/api/nth_block/<n>', methods=['GET'])
    def nth_block(n):
        block_info = str(master.chain.nth_block(int(n)))
        return Response(block_info, status=200, mimetype='application/json')
    
    @app.route('/api/nth_block/<n>/transactions', methods=['GET'])
    def transactions(n):
        block = master.chain.nth_block(int(n))
        if block is None:
            return Response('Block does not exist', status=400, mimetype='application/json')
        
        txs = block.get_transactions()

        if txs is None:
            txs_str = str(None)
        else:
            txs_str = map(str, txs)
        return Response(txs_str, status=200, mimetype='application/json')
    
    @app.route('/api/chain', methods=['GET'])
    def chain():
        chain = str(master.chain)
        return Response(chain, status=200, mimetype='application/json')
    
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
    return app.run(host='0.0.0.0', debug=True, port=PORT, use_reloader=False)

app = start_masternode()
