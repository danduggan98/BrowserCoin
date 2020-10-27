from django.shortcuts import render
from browsercoin.src.blockchain import Transaction
import requests
import json
import rsa

api_server = 'http://localhost:5000/node/transaction'

#KEYSET FOR TESTING ONLY
pk = rsa.PublicKey(7161922208794318767066040964677151258135328116297453912399841954187218432874044281389802556719562490446551106872007824711395555942314587736696196163246911, 65537)
sk = rsa.PrivateKey(7161922208794318767066040964677151258135328116297453912399841954187218432874044281389802556719562490446551106872007824711395555942314587736696196163246911, 65537, 2529190039219612029006156096349970073672643452150514569610783865415093509052011354053137419362907638688931802391026966838758386073633005506610348316211073, 4653267054194771887549018316602424354365855132197431641653737290104096205640373191, 1539116952752168874986689683144731402948127915839403158249316098473118921)

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
