from browsercoin.src import blockchain, node, params
from flask import Flask, request, Response
import threading, atexit
import json
import jsonpickle
import rsa
import sys
import os

# Multithreading implementation borrowed from this SO post:
# https://stackoverflow.com/questions/14384739/how-can-i-add-a-background-thread-to-flask

PROCESSING_TIME = 1 #Process one tx every second
dataLock = threading.Lock()
masternode_address = 'http://localhost:3000' #THIS WILL BE STORED IN ENVIRONMENT

#Create Node, threads for transaction processing and adding blocks
local_node = node.Node()
thread = threading.Thread()

#Take port number as a command line argument - default to 5000
PORT = 5000
if len(sys.argv) > 1:
    PORT = sys.argv[1]

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
        
        local_node.include_transaction(tx)
        return Response('Request accepted - Transaction added to mempool', status=202, mimetype='application/json')
    
    #Used for MasterNode to request a block if this node won the lottery
    #Requires a valid MAC signed by the MasterNode
    @app.route('/node/request_block', methods=['POST'])
    def request_block():

        #Verify the MAC
        try:
            MAC = jsonpickle.decode(request.json)
            msg = os.getenv('MAC_MSG').encode()
            rsa.verify(msg, MAC, params.MASTERNODE_PK)
        except:
            return Response('Request rejected - MAC failed authentication', status=400, mimetype='application/json')
        
        #Send block and output address if MAC checks out
        blockdata = local_node.next_blockdata.to_JSON()
        output_address = jsonpickle.encode(local_node.address)
        
        response_data = {
            'blockdata'    : blockdata,
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
            msg = os.getenv('MAC_MSG').encode()
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
    @app.route('/api/balance/<address>', methods=['GET'])
    def balance(address):
        key = rsa.PublicKey(int(address), 65537)
        return Response(str(local_node.chain.get_balance(key)), status=200, mimetype='application/json')
    
    @app.route('/node/mempool', methods=['GET'])
    def mempool():
        if not len(local_node.mempool):
            return 'Mempool empty'
        
        result = ''
        for tx in local_node.mempool:
            result += str(tx) + '\n'
        return result

    @app.route('/node/valid', methods=['GET'])
    def valid():
        return str(local_node.next_blockdata.is_valid())

    @app.route('/node/block', methods=['GET'])
    def block():
        return str(local_node.next_blockdata)
    
    @app.route('/node/chain', methods=['GET'])
    def chain():
        return str(local_node.chain)

    @app.route('/node/nth_block/<n>', methods=['GET'])
    def nth(n):
        return str(local_node.chain.nth_block(int(n)))
    
    @app.route('/node/nth_block/<n>/transactions', methods=['GET'])
    def transactions(n):
        block = local_node.chain.nth_block(int(n))
        if block is None:
            return Response('Block does not exist', status=400, mimetype='application/json')
        
        txs = block.get_transactions()

        if txs is None:
            txs_str = str(None)
        else:
            txs_str = map(str, txs)
        return Response(txs_str, status=200, mimetype='application/json')

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
    return app

app = start_node()

#Run with dev server when called directly
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=PORT, use_reloader=False)
