import src.blockchain as blockchain
import hashlib
import rsa

def Hash(data):
    return hashlib.sha256(data.encode()).hexdigest()

def HashBlock(block):
    if block is None or type(block) is not blockchain.Block:
        return None
    
    return HashBlockData(block.data)

def HashBlockData(block_data):
    if block_data is None or type(block_data) is not blockchain.BlockData:
        return None
    
    stringified_block = block_data.timestamp + ''.join(map(str, block_data.transactions))
    return Hash(stringified_block)

def HashTransaction(transaction):
    if transaction is None or type(transaction) is not blockchain.Transaction:
        return None
    
    stringified_transaction = (
        transaction.timestamp +
        str(transaction.transfer_amount) +
        str(transaction.sender) +
        str(transaction.recipient)
    )
    return Hash(stringified_transaction)

#Load the master node's RSA keys
def LoadMasterNodeKeys():
    with open('bc_masternode_pk.pem', mode='rb') as public_key_file:
        pk = public_key_file.read()
        masternode_pk = rsa.PublicKey.load_pkcs1_openssl_pem(pk)

    with open('bc_masternode_sk.pem', mode='rb') as secret_key_file:
        sk = secret_key_file.read()
        masternode_sk = rsa.PrivateKey.load_pkcs1(sk)
    
    return (masternode_pk, masternode_sk)
