from django.shortcuts import render
from browsercoin.src.blockchain import Transaction
import requests
import rsa

api_server = 'http://localhost:5000/node/transaction'

#CREATE KEYSET FOR TESTING ONLY

(pk, sk) = rsa.newkeys(512)

# Create your views here.
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
        
        #CREATE TX + SIGN

        data = {
            'amount': amount,
            'sender': pk,
            'recipient': recipient
        }
        response = requests.post(api_server, data=data)
        return render(request, 'wallet.html', {'errs': response})

    return render(request, 'wallet.html')
