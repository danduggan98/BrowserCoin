from django.shortcuts import render
import requests

api_server = 'http://localhost:5000/node/transaction'

# Create your views here.
def wallet(request):
    if req := request.POST:
        print(req)
        amount    = req['amount']
        sender    = req['sender']
        recipient = req['recipient']

        response = requests.post(api_server)
        print(response)
    
    return render(request, 'wallet.html')

def process_tx(request):
    print('Inside process_tx method')
    
    response = requests.post(api_server)

    #return 'ACCESSED PROCESS_TX METHOD'
    return render(request, 'wallet.html')
