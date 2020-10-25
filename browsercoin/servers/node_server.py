from browsercoin.src import blockchain, node
from flask import Flask, request, jsonify, Response
import json

app = Flask(__name__)
local_node = node.Node()

@app.route('/node/transaction', methods=['POST'])
def recieve_tx():
   if not request.json:
      return Response('Request rejected - transaction data required', status=400, mimetype='application/json')

   amount    = request.json.get('amount')
   sender    = request.json.get('sender')
   recipient = request.json.get('recipient')
   signature = request.json.get('signature')

   if None in (amount, sender, recipient, signature):
      return Response('Request rejected - at least one parameter is missing', status=400, mimetype='application/json')
   
   #Add transaction to node
   sender_prev_tx = local_node.blockchain.latest_address_activity(sender)
   recipient_prev_tx = local_node.blockchain.latest_address_activity(recipient)

   tx = blockchain.Transaction(amount, sender, recipient, sender_prev_tx, recipient_prev_tx)
   tx.signature = signature
   
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
   return result
#------------------------------------------

if __name__ == '__main__':
   print('Starting Node')
   app.run(debug=True)
