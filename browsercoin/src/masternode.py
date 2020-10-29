from browsercoin.src import blockchain, params
from definitions import ROOT_DIR
import os
import rsa
import json
import random
import requests
import jsonpickle

class MasterNode:
    def __init__(self):
        (pk, sk) = self.load_keys()

        self.public_key = pk
        self.secret_key = sk

        self.chain = blockchain.Blockchain()
        self.nodes = ['http://localhost:5000'] #Start with one for testing

    #Create a transaction sending the block reward from
    # the master node's public key to the output address
    def add_coinbase(self, block_data, output_address, prev_coinbase_tx, output_prev_tx):
        coinbase = (
            blockchain.Transaction(
                params.BLOCK_REWARD,
                self.public_key,
                output_address,
                prev_coinbase_tx,
                output_prev_tx
            )
            .sign(self.secret_key)
        )
        
        block_data.transactions.append(coinbase)
        return block_data
    
    def run_lottery(self):
        print('- Running Lottery')

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

            response = requests.post(lottery_winner + '/node/request_block', json=MAC_JSON)
            response_data = json.loads(response.content)

            block_data: blockchain.BlockData = jsonpickle.decode(response_data['block_data'])
            output_address: rsa.PublicKey    = jsonpickle.decode(response_data['output_address'])

            if len(node_list_copy) == len(self.nodes):
                first_block = block_data
            
            #Validate the block
            if not block_data.is_valid():
                print(f'    * Invalid block received from {lottery_winner}')
                del node_list_copy[random_selection]
                continue
            
            valid_block_found = True
        
        #If no valid blocks were received, use the first one from the original lottery winner
        if not valid_block_found:
            block_data = first_block
            print('  > No valid blocks received - using first block')
        print(f'    * Success! Received valid block from {lottery_winner}')

        #Add the coinbase transaction
        prev_coinbase_tx = self.chain.latest_address_activity(self.public_key, block_data)
        prev_output_tx   = self.chain.latest_address_activity(output_address, block_data)
        self.add_coinbase(block_data, output_address, prev_coinbase_tx, prev_output_tx)

        #Create a block and generate a MAC to prove it's coming from the MasterNode
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
        num_accepted = 0

        for node in self.nodes:
            node_route = node + '/node/receive_block'
            response = requests.post(node_route, json=json.dumps(request_data))

            if response.status_code == 202:
                num_accepted += 1

        print(f'  > Request completed - block accepted by ({num_accepted}/{len(self.nodes)}) nodes')

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
