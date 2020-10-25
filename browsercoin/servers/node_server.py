from browsercoin.src import blockchain, node
from flask import Flask, request, jsonify, Response
import json
import jsonpickle
import rsa

app = Flask(__name__)
local_node = node.Node()

@app.route('/node/transaction', methods=['POST'])
def recieve_tx():
   if not request.json:
      return Response('Request rejected - transaction data required', status=400, mimetype='application/json')

   tx: blockchain.Transaction = jsonpickle.decode(request.json)

   if None in (tx.timestamp, tx.transfer_amount, tx.sender, tx.recipient, tx.signature, tx.hash):
      return Response('Request rejected - at least one parameter is missing', status=400, mimetype='application/json')
   
   #Add transaction to node
   tx.sender_prev_tx    = local_node.blockchain.latest_address_activity(tx.sender)
   tx.recipient_prev_tx = local_node.blockchain.latest_address_activity(tx.recipient)

   local_node.include_transaction(tx)

   return Response('Request accepted - Transaction added to mempool', status=202, mimetype='application/json')

#ROUTES FOR CHECKING RESULTS
#NOT INTENDED FOR LONG TERM USE
#------------------------------------------
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
#------------------------------------------

if __name__ == '__main__':
   print('Starting Node')
   app.run(debug=True)
