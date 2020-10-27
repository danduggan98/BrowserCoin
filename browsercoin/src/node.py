from browsercoin.src import blockchain, crypto, params
from collections import deque
import datetime
import rsa

class Node:
    def __init__(self):
        self.mempool = deque()
        self.blockchain = blockchain.Blockchain()
        self.next_block_data = blockchain.BlockData()
        self.address = rsa.PublicKey( #FOR TESTING
            7161922208794318767066040964677151258135328116297453912399841954187218432874044281389802556719562490446551106872007824711395555942314587736696196163246911,
            65537
        )

    def include_transaction(self, tx: blockchain.Transaction):
        self.mempool.append(tx)
    
    #Check the next transaction, and add it to the Block if valid
    def validate_next_transaction(self):
        if len(self.mempool):
            print('Popping next transaction from mempool ( 1 /', len(self.mempool), ')')
            next_tx = self.mempool.pop()

            if self.next_block_data.contains_transaction(next_tx):
                print('Transaction already present in block')
                return
            
            if self.blockchain.transaction_is_valid(next_tx, self.next_block_data):
                self.next_block_data.add_transaction(next_tx)
                print('Transaction added!')
            else:
                print('Failed to add invalid transaction')
    
    def generate_block(self):
        #The coinbase will eventually be added by the master node, not here
        (master_pk, master_sk) = crypto.LoadMasterNodeKeys()
        prev_coinbase_tx = self.blockchain.latest_address_activity(master_pk)
        prev_output_tx = self.blockchain.latest_address_activity(self.address)

        self.next_block_data.add_coinbase(self.address, prev_coinbase_tx, prev_output_tx)
        return blockchain.Block(self.next_block_data)
    
    def add_next_block(self):
        next_block = self.generate_block()
        self.blockchain.add_block(next_block)
        self.next_block_data = blockchain.BlockData()
        print('Added next block')
