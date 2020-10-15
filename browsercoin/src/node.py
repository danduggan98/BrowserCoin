import src.blockchain as blockchain
import src.params as params
import src.crypto as crypto
import rsa

class Node:
    def __init__(self):
        self.pending_transactions = []
        self.blockchain = blockchain.Blockchain()

#class MasterNode(Node):
#    
