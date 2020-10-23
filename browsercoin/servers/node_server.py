from browsercoin.src import node
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
   
   #Add tx to node
   # -- Implementation -- #

   return Response('Request accepted - Transaction added to mempool', status=202, mimetype='application/json')

if __name__ == '__main__':
    print('Starting Node')
    app.run(debug=True)
