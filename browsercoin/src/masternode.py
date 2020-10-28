from browsercoin.src import blockchain, params
from definitions import ROOT_DIR
import os
import rsa
import random
import requests
import jsonpickle

class MasterNode:
    def __init__(self):
        (pk, sk) = self.load_keys()

        self.public_key = pk
        self.secret_key = sk

        self.blockchain = blockchain.Blockchain()
        self.nodes = ['http://localhost:5000'] #Start with one for testing
    
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
    
    def run_lottery(self):
        print('--- Running Lottery ---')

        #Randomly select a winner from all the nodes
        last_node_idx = len(self.nodes) - 1
        random_selection = random.randint(0, last_node_idx)
        lottery_winner = self.nodes[random_selection]

        #Request a block from the winner using a MAC to prove authenticity
        #Also return the address they would like their block reward sent to
        msg = 'request_block'.encode()
        MAC = rsa.sign(msg, self.secret_key, 'SHA-256')
        MAC_JSON = jsonpickle.encode(MAC)

        response = requests.post(lottery_winner + '/node/request_block', json=MAC_JSON)
        response_data = jsonpickle.decode(response.content)

        block_data = jsonpickle.decode(response_data['block_data'])
        output_address = jsonpickle.decode(response_data['output_address'])

        #---Validate---
        
        #Add the coinbase transaction if the block is valid
        #output_address = self.nodes[] #GET THIS FROM THE NODE
        #prev_coinbase_tx = self.blockchain.latest_address_activity(self.public_key)
        #prev_output_tx = self.blockchain.latest_address_activity(output_address)
        #self.add_coinbase(block_data, self.nodes[0].address, )
        #print('ZE BLOCK:', str(block_data))

        #Validate the block

        #Add the block to the chain, and send it to all nodes so they can add it

        print(f'SELECTING NODE #{random_selection}')

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
