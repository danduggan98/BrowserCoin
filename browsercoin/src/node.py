import src.blockchain as blockchain
import src.params as params
import rsa

#Load the master node's RSA keys
with open('bc_masternode_pk.pem', mode='rb') as public_key_file:
    pk = public_key_file.read()
    masternode_pk = rsa.PublicKey.load_pkcs1_openssl_pem(pk)

with open('bc_masternode_sk.pem', mode='rb') as secret_key_file:
    sk = secret_key_file.read()
    masternode_sk = rsa.PrivateKey.load_pkcs1(sk)

class Node:
    def __init__(self):
        self.pending_transactions = []
        self.blockchain = blockchain.Blockchain()

class MasterNode(Node):
    def add_coinbase(self, block_data, output_address):
        #Create a transaction sending the block reward from
        # the master node's public key to the output address
        output_prev_tx = self.blockchain.latest_address_activity(output_address) #THIS HAS TO RUN ON THE BLOCKDATA, NOT THE CHAIN!!!
        
        coinbase = (
            blockchain.Transaction(params.BLOCK_REWARD, masternode_pk, output_address, None, output_prev_tx)
            .sign(masternode_sk)
        )
        block_data.transactions.append(coinbase)
