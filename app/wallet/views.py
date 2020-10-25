from django.shortcuts import render
from browsercoin.src.blockchain import Transaction
import requests
import json
import rsa

api_server = 'http://localhost:5000/node/transaction'
(pk, sk) = rsa.newkeys(512) #KEYSET FOR TESTING ONLY

def wallet(request):
    if req := request.POST:
        amount    = req['amount']
        recipient = req['recipient']
        errs = []

        if not amount:
            errs.append('Please enter the amount to send')

        if not recipient:
            errs.append('Please enter the recipient')
        
        if errs:
            return render(request, 'wallet.html', {'errs': errs})
        
        #Convert the inputs to numbers
        amount = float(amount)
        recipient = int(recipient)

        #Create a transaction, then sign it with the user's secret key
        recipient_as_key = rsa.PublicKey(recipient, 65537)
        tx = Transaction(amount, pk, recipient_as_key).sign(sk)

        data = {
            'amount': amount,
            'sender': pk.n,
            'recipient': recipient,
            'signature': tx.signature.decode('utf8', 'ignore')
        }

        response = requests.post(api_server, json=data)
        return render(request, 'wallet.html', {'response': response.text})

    return render(request, 'wallet.html')
