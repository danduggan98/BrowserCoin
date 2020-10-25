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

        #Create a transaction, then sign it with the user's secret key
        recipient_key = rsa.PublicKey(int(recipient), 65537)
        tx = Transaction(float(amount), pk, recipient_key).sign(sk)

        response = requests.post(api_server, json=tx.to_JSON())
        return render(request, 'wallet.html', {'response': response.text})

    return render(request, 'wallet.html')
