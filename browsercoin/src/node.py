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
        print('VALIDATING NEXT TRANSACTION')
        print('#TX:', len(self.mempool))

        if len(self.mempool):
            next_tx = self.mempool.pop()

            if (self.blockchain.transaction_is_valid(next_tx, self.next_block_data)):
                self.next_block_data.add_transaction(next_tx)
                print('Transaction added!')
            else:
                print('INVALID TX')
        else:
            print('NO TRANSACTIONS')
    
    def generate_block(self):
        next_block = blockchain.Block(self.next_block_data)
        return next_block
    
    def populate_for_testing(self):
        (master_pk, master_sk) = crypto.LoadMasterNodeKeys()
        test_address = rsa.PublicKey(7161922208794318767066040964677151258135328116297453912399841954187218432874044281389802556719562490446551106872007824711395555942314587736696196163246911, 65537)

        self.blockchain.add_block(blockchain.Block(blockchain.BlockData().add_coinbase(test_address, self.blockchain.latest_address_activity(master_pk), self.blockchain.latest_address_activity(test_address))))
        self.blockchain.add_block(blockchain.Block(blockchain.BlockData().add_coinbase(test_address, self.blockchain.latest_address_activity(master_pk), self.blockchain.latest_address_activity(test_address))))
        self.blockchain.add_block(blockchain.Block(blockchain.BlockData().add_coinbase(test_address, self.blockchain.latest_address_activity(master_pk), self.blockchain.latest_address_activity(test_address))))
        self.blockchain.add_block(blockchain.Block(blockchain.BlockData().add_coinbase(test_address, self.blockchain.latest_address_activity(master_pk), self.blockchain.latest_address_activity(test_address))))
        self.blockchain.add_block(blockchain.Block(blockchain.BlockData().add_coinbase(test_address, self.blockchain.latest_address_activity(master_pk), self.blockchain.latest_address_activity(test_address))))
        self.blockchain.add_block(blockchain.Block(blockchain.BlockData().add_coinbase(test_address, self.blockchain.latest_address_activity(master_pk), self.blockchain.latest_address_activity(test_address))))
        self.blockchain.add_block(blockchain.Block(blockchain.BlockData().add_coinbase(test_address, self.blockchain.latest_address_activity(master_pk), self.blockchain.latest_address_activity(test_address))))
        self.blockchain.add_block(blockchain.Block(blockchain.BlockData().add_coinbase(test_address, self.blockchain.latest_address_activity(master_pk), self.blockchain.latest_address_activity(test_address))))
        self.blockchain.add_block(blockchain.Block(blockchain.BlockData().add_coinbase(test_address, self.blockchain.latest_address_activity(master_pk), self.blockchain.latest_address_activity(test_address))))
        self.blockchain.add_block(blockchain.Block(blockchain.BlockData().add_coinbase(test_address, self.blockchain.latest_address_activity(master_pk), self.blockchain.latest_address_activity(test_address))))
