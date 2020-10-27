from browsercoin.src import blockchain, params
from definitions import ROOT_DIR
import os
import rsa

class MasterNode:
    def __init__(self):
        (pk, sk) = self.load_keys()

        self.public_key = pk
        self.secret_key = sk
        self.nodes = []
    
    def verify_block(self):
        pass

    #Create a transaction sending the block reward from
    # the master node's public key to the output address
    def add_coinbase(self, block_data, output_address, prev_coinbase_tx, output_prev_tx):
        coinbase = (
            blockchain.Transaction(params.BLOCK_REWARD, self.public_key, output_address, prev_coinbase_tx, output_prev_tx)
            .sign(self.secret_key)
        )
        
        block_data.transactions.append(coinbase)
        return block_data

    #Load the master node's RSA keys
    def load_keys(self):
        pk_path = os.path.join(ROOT_DIR, 'browsercoin/bc_masternode_pk.pem')
        with open(pk_path, mode='rb') as public_key_file:
            pk = public_key_file.read()
            masternode_pk = rsa.PublicKey.load_pkcs1_openssl_pem(pk)

        sk_path = os.path.join(ROOT_DIR, 'browsercoin/bc_masternode_sk.pem')
        with open(sk_path, mode='rb') as secret_key_file:
            sk = secret_key_file.read()
            masternode_sk = rsa.PrivateKey.load_pkcs1(sk)
        
        return (masternode_pk, masternode_sk)
