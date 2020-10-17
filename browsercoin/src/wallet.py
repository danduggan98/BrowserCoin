import rsa
import requests

class Wallet:
    def __init__(self):
        self.addresses = []
    
    def create_new_address(self):
        self.addresses.append(rsa.newkeys(512)[0])
    
    def broadcast_transaction(self, tx):
        # --- Implementation --- #
        return
