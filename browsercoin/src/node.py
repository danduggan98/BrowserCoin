from browsercoin.src import blockchain, crypto, params
from collections import deque
import rsa

class Node:
    def __init__(self):
        self.mempool = deque()
        self.blockchain = blockchain.Blockchain()
        self.next_block_data = blockchain.BlockData()

    def include_transaction(self, tx: blockchain.Transaction):
        self.mempool.append(tx)
    
    #Check the next transaction, and add it to the Block if valid
    def validate_next_transaction(self):
        next_tx = self.mempool.pop()

        if (blockchain.transaction_is_valid(next_tx, self.next_block_data)):
            self.next_block_data.add_transaction(next_tx)
    
    def generate_block(self):
        next_block = blockchain.Block(self.next_block_data)
        return next_block

