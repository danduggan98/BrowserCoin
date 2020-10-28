from browsercoin.src import blockchain, node, params
from flask import Flask, request, Response
import threading, atexit
import json
import jsonpickle
import rsa

# Multithreading implementation borrowed from this SO post:
# https://stackoverflow.com/questions/14384739/how-can-i-add-a-background-thread-to-flask

PROCESSING_TIME = 1 #Process one tx every second
dataLock = threading.Lock()
masternode_address = 'http://localhost:3000' #THIS WILL BE STORED IN ENVIRONMENT

#Create Node, threads for transaction processing and adding blocks
local_node = node.Node()
thread = threading.Thread()

#Run the server
def start_node():
    app = Flask(__name__)

    # //////// Routes to interface with MasterNode \\\\\\\\ #

    #Receive transaction from MasterNode
    @app.route('/node/transaction', methods=['POST'])
    def recieve_tx():

        #Add transaction to node's mempool
        try:
            tx: blockchain.Transaction = jsonpickle.decode(request.json)
        except:
            return Response('Request rejected - Malformed transaction', status=400, mimetype='application/json')
        
        tx.sender_prev_tx    = local_node.blockchain.latest_address_activity(tx.sender)
        tx.recipient_prev_tx = local_node.blockchain.latest_address_activity(tx.recipient)

        local_node.include_transaction(tx)
        return Response('Request accepted - Transaction added to mempool', status=202, mimetype='application/json')
    
    #Used for MasterNode to request a block if this node won the lottery
    #Requires a valid MAC signed by the MasterNode
    @app.route('/node/request_block', methods=['POST'])
    def request_block():

        #Verify the MAC
        try:
            MAC = jsonpickle.decode(request.json)
            msg = 'request_block'.encode()
            rsa.verify(msg, MAC, params.MASTERNODE_PK)
        except:
            return Response('Request rejected - MAC failed authentication', status=400, mimetype='application/json')
        
        #Send block and output address if MAC checks out
        block_data = local_node.next_block_data.to_JSON()
        output_address = jsonpickle.encode(local_node.address)
        
        response_data = {
            'block_data'    : block_data,
            'output_address': output_address
        }
        return json.dumps(response_data)
    
    #Receive a block and add it to the local chain
    #Requires a valid MAC signed by the MasterNode
    @app.route('/node/receive_block', methods=['POST'])
    def receive_block():
        #Check for malformed JSON
        try:
            request_data = json.loads(request.json)
        except:
            return Response('Request rejected - Malformed JSON', status=400, mimetype='application/json')
        
        #Verify the MAC
        try:
            MAC = jsonpickle.decode(request_data['MAC'])
            msg = 'receive_block'.encode()
            rsa.verify(msg, MAC, params.MASTERNODE_PK)
        except:
            return Response('Request rejected - MAC failed authentication', status=400, mimetype='application/json')
        
        #Check for malformed Block, then add the block
        try:
            block: blockchain.Block = jsonpickle.decode(request_data['block'])
        except:
            return Response('Request rejected - Malformed block', status=400, mimetype='application/json')
        
        local_node.add_next_block(block)
        return Response('Request accepted - Block added to local chain', status=202, mimetype='application/json')
    
    # //////// Test routes for checking results (TEMPORARY) \\\\\\\\ #
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

        thread = threading.Timer(PROCESSING_TIME, process_tx, ())
        thread.start()

    def begin_processing():
        global thread
        thread = threading.Timer(PROCESSING_TIME, process_tx, ())
        thread.start()
    
    #Start handling transactions
    begin_processing()
    atexit.register(stop_processing) #Stop processing when server ends
    return app.run(debug=True, use_reloader=False)

app = start_node()
