from src.blockchain import Blockchain, Transaction
import src.params as params

class Node:
    def __init__(self):
        self.pending_transactions = []
        self.blockchain = Blockchain()

class MasterNode(Node):
    def add_coinbase(self, block, output_address):

        #Create a transaction sending the block reward from 
        # the master node's public key to the output address
        master_node_pk = None #LOAD FROM ENVIRONMENT
        master_node_sk = None #LOAD FROM ENVIRONMENT
        output_prev_tx = self.blockchain.latest_address_activity(output_address)

        coinbase = (
            Transaction(params.BLOCK_REWARD, master_node_pk, output_address, None, output_prev_tx)
            .sign(master_node_sk)
        )
        block.data.transactions.append(coinbase)
