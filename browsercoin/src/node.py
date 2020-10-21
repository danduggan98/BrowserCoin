from browsercoin.src import blockchain, crypto, params
import queue
import rsa

class Node:
    def __init__(self):
        self.pending_transactions = queue.Queue()
        self.blockchain = blockchain.Blockchain()
        self.next_block_data = blockchain.BlockData()

    def include_transaction(self, tx: blockchain.Transaction):
        if (not blockchain.transaction_is_valid(tx.is_valid)):
            return
        
        self.next_block_data.add_transaction(tx)
    
    def create_block(self):
        next_block = blockchain.Block(self.next_block_data)
        return next_block
    
    #Run the server and begin accepting transactions
    def start(self):
        # --- Implementation --- #
        return
