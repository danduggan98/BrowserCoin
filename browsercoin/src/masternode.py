from browsercoin.src import blockchain, params
from definitions import ROOT_DIR
import requests
import json
import jsonpickle
import os
import rsa
import random
import datetime
from dotenv import load_dotenv
from pymongo import MongoClient

#Connect to DB using connection string from environment
load_dotenv()
mongo_connection_str = os.getenv('MONGO_STRING')

try:
    client = MongoClient(mongo_connection_str)
except:
    print('Failed connection to Mongo cluster. Unable to backup blockchain')

class MasterNode:
    def __init__(self):
        (pk, sk) = self.load_keys()

        self.public_key = pk
        self.secret_key = sk

        self.chain = blockchain.Blockchain()
        self.nodes = ['http://localhost:5000', 'http://localhost:7000', 'http://localhost:2000'] #Multiple ports for testing

    #Create a transaction sending the block reward from
    # the master node's public key to the output address
    def add_coinbase(self, output_address, block_data):
        coinbase = (
            blockchain.Transaction(
                params.BLOCK_REWARD,
                self.public_key,
                output_address
            )
            .sign(self.secret_key)
        )
        
        self.chain.add_tx_to_blockdata(coinbase, block_data)
        return block_data
    
    def run_lottery(self):
        print(f'- Running Lottery for block #{len(self.chain)} - {datetime.datetime.now()}')

        #Continually request blocks until a valid one is received
        node_list_copy = self.nodes[:]
        first_block = None
        valid_block_found = False
        
        while not valid_block_found and len(node_list_copy):

            #Randomly select a winner from all remaining nodes
            last_node_idx = len(node_list_copy) - 1
            random_selection = random.randint(0, last_node_idx)
            lottery_winner = node_list_copy[random_selection]
            print(f'  > Requesting block from {lottery_winner}')

            #Request a block from the winner using a MAC to prove authenticity
            #Also return the address they would like their block reward sent to
            msg = 'request_block'.encode()
            MAC = rsa.sign(msg, self.secret_key, 'SHA-256')
            MAC_JSON = jsonpickle.encode(MAC)

            try:
                response = requests.post(lottery_winner + '/node/request_block', json=MAC_JSON)
                response_data = json.loads(response.content)

                block_data: blockchain.BlockData = jsonpickle.decode(response_data['block_data'])
                output_address: rsa.PublicKey    = jsonpickle.decode(response_data['output_address'])

                if len(node_list_copy) == len(self.nodes):
                    first_block = block_data
            except:
                print(f'    * Unable to reach node at {lottery_winner}')
                node_list_copy.remove(lottery_winner)
                continue
            
            #Validate the block
            test_block = blockchain.Block(block_data)
            if not self.chain.block_is_valid(test_block):
                print(f'    * Invalid block received from {lottery_winner}')
                node_list_copy.remove(lottery_winner)
                continue
            
            valid_block_found = True
            print(f'    * Success! Received valid block from {lottery_winner}')
        
        #If no valid blocks were received, use the first one from the original lottery winner
        if not valid_block_found:
            block_data = first_block
            print('  > No valid blocks received - using first block')

        #Create a block and generate a MAC to prove it's coming from the MasterNode
        self.add_coinbase(output_address, block_data)
        new_block = blockchain.Block(block_data)

        msg = 'receive_block'.encode()
        MAC = rsa.sign(msg, self.secret_key, 'SHA-256')
        
        #Bundle the MAC and block together in one JSON object
        request_data = {
            'block': new_block.to_JSON(),
            'MAC'  : jsonpickle.encode(MAC)
        }
        
        #Add the block to the chain, then send it to all nodes so they can add it
        self.chain.add_block(new_block)
        self.save_block_to_db(new_block)

        num_accepted = 0
        num_online = 0

        for node in self.nodes:
            node_route = node + '/node/receive_block'

            try:
                response = requests.post(node_route, json=json.dumps(request_data))
            except:
                continue
            
            num_online += 1

            if response.status_code == 202:
                num_accepted += 1

        print(f'  > Request completed - block accepted by ({num_accepted}/{num_online}) active nodes\n')
    
    def save_block_to_db(self, block):
        print(block.to_JSON())

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
