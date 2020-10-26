from browsercoin.src import blockchain, node, params
from flask import Flask, request, Response
import threading, atexit
import json
import jsonpickle
import rsa

# Multithreading implementation borrowed from this SO post:
# https://stackoverflow.com/questions/14384739/how-can-i-add-a-background-thread-to-flask

POOL_TIME = 1 #Process tx every second
BLOCK_TIME = params.BLOCK_SPACING
dataLock = threading.Lock()

#Create Node, populate temporarily for testing
local_node = node.Node()
local_node.populate_for_testing()

#Create threads for transaction processing and adding blocks
thread = threading.Thread()
block_thread = threading.Thread()

#Run the server
def start_node():
    app = Flask(__name__)

    # //////// API Handlers \\\\\\\\ #
    @app.route('/node/transaction', methods=['POST'])
    def recieve_tx():
        if not request.json:
            return Response('Request rejected - transaction data required', status=400, mimetype='application/json')

        tx: blockchain.Transaction = jsonpickle.decode(request.json)

        if None in (tx.timestamp, tx.transfer_amount, tx.sender, tx.recipient, tx.hash):
            return Response('Request rejected - at least one parameter is missing', status=400, mimetype='application/json')
        
        if tx.signature is None:
            return Response('Request rejected - signature is missing or invalid', status=400, mimetype='application/json')
        
        #Add transaction to node
        tx.sender_prev_tx    = local_node.blockchain.latest_address_activity(tx.sender)
        tx.recipient_prev_tx = local_node.blockchain.latest_address_activity(tx.recipient)

        local_node.include_transaction(tx)
        return Response('Request accepted - Transaction added to mempool', status=202, mimetype='application/json')
    
    # //////// Test routes for checking results (TEMPORARY) \\\\\\\\ #
    @app.route('/node/info', methods=['GET'])
    def info():
        return str(local_node.blockchain)

    @app.route('/node/mempool', methods=['GET'])
    def mempool():
        result = ''
        for tx in local_node.mempool:
            result += str(tx) + '\n'
        return result

    @app.route('/node/valid', methods=['GET'])
    def valid():
        return str(local_node.next_block_data.is_valid())

    @app.route('/node/block', methods=['GET'])
    def block():
        return str(local_node.next_block_data)
    
    @app.route('/node/chain', methods=['GET'])
    def chain():
        return str(local_node.blockchain)

    @app.route('/node/nth_block/<n>', methods=['GET'])
    def nth(n):
        return str(local_node.blockchain.nth_block(int(n)))

    # //////// Methods for multithreaded transaction processing \\\\\\\\ #
    def stop_processing():
        global thread
        thread.cancel()

    #Validate the next transaction in the mempool
    def process_tx():
        global local_node
        global thread

        with dataLock:
            local_node.validate_next_transaction()

        thread = threading.Timer(POOL_TIME, process_tx, ())
        thread.start()
    
    def add_block():
        global local_node
        global block_thread

        with dataLock:
            local_node.add_next_block()

        block_thread = threading.Timer(BLOCK_TIME, add_block, ())
        block_thread.start()

    def begin_processing():
        begin_adding_blocks()

        global thread
        thread = threading.Timer(POOL_TIME, process_tx, ())
        thread.start()
    
    def begin_adding_blocks():
        global block_thread
        block_thread = threading.Timer(BLOCK_TIME, add_block, ())
        block_thread.start()

    #Start handling transactions
    begin_processing()
    atexit.register(stop_processing) #Stop processing when server ends
    return app.run(debug=True, use_reloader=False)

app = start_node()
