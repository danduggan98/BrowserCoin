from browsercoin.src import node
from flask import Flask, request, jsonify
import json

app = Flask(__name__)
local_node = node.Node()

@app.route('/node/transaction', methods=['POST'])
def recieve_tx():
   if not request.json:
      return 'Request rejected - transaction data required'

   amount    = request.json.get('amount')
   sender    = request.json.get('sender')
   recipient = request.json.get('recipient')
   signature = request.json.get('signature')

   if None in (amount, sender, recipient, signature):
      return 'Request rejected - at least one parameter is missing'
   
   #Add tx to node
   # -- Implementation -- #

   return 'Request accepted - Transaction added to mempool'

if __name__ == '__main__':
    print('Starting Node')
    app.run(debug=True)
