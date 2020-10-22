from browsercoin.src import blockchain
import rsa
import requests

class Wallet:
    def __init__(self):
        self.addresses = []
    
    def create_new_address(self):
        self.addresses.append(rsa.newkeys(512))
    
    def create_transaction(self, amount, sender, recipient):
        new_tx = blockchain.Transaction(amount, sender, recipient)
        signed_tx = new_tx.sign() #where to get sk?
        return signed_tx
    
    def broadcast_transaction(self, tx):
        # --- Implementation --- #
        return
    
    def find_sk(self, pk):
        pass
