from browsercoin.src import blockchain, node
from flask import Flask, request, Response
import threading, atexit
import json
import jsonpickle
import rsa

# Multithreading implementation borrowed from this SO post:
# https://stackoverflow.com/questions/14384739/how-can-i-add-a-background-thread-to-flask

POOL_TIME = 5 #5 seconds
dataLock = threading.Lock()

local_node = node.Node()
local_node.populate_for_testing() #TEMPORARILY ADD DATA
thread = threading.Thread()

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
            result += str(tx)
            result += '\n'
        return result

    @app.route('/node/valid', methods=['GET'])
    def valid():
        return str(local_node.mempool[0].is_valid())

    @app.route('/node/block', methods=['GET'])
    def block():
        return str(local_node.next_block_data)
    
    @app.route('/node/chain', methods=['GET'])
    def chain():
        return str(local_node.blockchain)

    @app.route('/node/add', methods=['GET'])
    def add():
        next_block = local_node.generate_block()
        local_node.blockchain.add_block(next_block)
        local_node.next_block_data = blockchain.BlockData()
        return 'OH YEAH'

    # //////// Methods for multithreaded transaction processing \\\\\\\\ #
    def stop_processing():
        global thread
        thread.cancel()

    #Validate the next transaction in the mempool
    def process_tx():
        global local_node
        global thread

        with dataLock:
            print('! ! ! DOING THE NEXT THING ! ! !')
            local_node.validate_next_transaction()

        thread = threading.Timer(POOL_TIME, process_tx, ())
        thread.start()   

    def begin_processing():
        global thread
        thread = threading.Timer(POOL_TIME, process_tx, ())
        thread.start()

    #Start handling transactions
    begin_processing()
    atexit.register(stop_processing) #Stop processing when server ends
    return app.run(debug=True, use_reloader=False)

app = start_node()
