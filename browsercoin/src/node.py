from browsercoin.src import blockchain, crypto, params, db_utils
from collections import deque
import datetime
import rsa

class Node:
    def __init__(self):
        self.mempool = deque()
        self.chain = blockchain.Blockchain()
        self.next_blockdata = blockchain.BlockData()
        self.address = rsa.PublicKey( #FOR TESTING
            7161922208794318767066040964677151258135328116297453912399841954187218432874044281389802556719562490446551106872007824711395555942314587736696196163246911,
            65537
        )

        #Connect to DB using connection string from environment
        try:
            self.db = db_utils.connect_db()
            print(' ! Successfully connected to Mongo cluster')
        except:
            print(' !!! Failed connection to Mongo Cluster - Terminating !!!')
            raise ConnectionError
        
        self.chain.populate_from_db(self.db) #Load existing chain

    def include_transaction(self, tx):
        self.mempool.append(tx)
    
    #Check the next transaction, and add it to the Block if valid
    def validate_next_transaction(self):
        if len(self.mempool):
            print(f'- Validating next transaction from mempool (1/{len(self.mempool)})')
            next_tx = self.mempool.pop()

            if self.next_blockdata.contains_transaction(next_tx):
                print('- Transaction already present in block')
                return
            
            if self.chain.transaction_is_valid(next_tx, self.next_blockdata):
                self.chain.add_tx_to_blockdata(next_tx, self.next_blockdata)
                print('- Transaction added!')
            else:
                print('- Failed to add invalid transaction')
    
    def add_next_block(self, next_block):
        self.chain.add_block(next_block)
        self.next_blockdata = blockchain.BlockData()
        print('- Added next block')
