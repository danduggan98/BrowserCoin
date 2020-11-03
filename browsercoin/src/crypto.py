from browsercoin.src import blockchain
import hashlib

def Hash(data):
    return hashlib.sha256(data.encode()).hexdigest()

def HashBlock(block):
    if block is None or type(block) is not blockchain.Block:
        return None
    
    stringified_block = (
        str(block.idx) +
        block.timestamp +
        str(block.prev_block) +
        str(block.prev_hash) +
        str(HashBlockData(block.data))
    )
    return Hash(stringified_block)

def HashBlockData(blockdata):
    if blockdata is None or type(blockdata) is not blockchain.BlockData:
        return None
    
    stringified_block = blockdata.timestamp + ''.join(map(str, blockdata.transactions))
    return Hash(stringified_block)

def HashTransaction(transaction):
    if transaction is None or type(transaction) is not blockchain.Transaction:
        return None
    
    stringified_transaction = (
        transaction.timestamp +
        str(transaction.transfer_amount) +
        str(transaction.sender.n) +
        str(transaction.recipient.n)
    )
    return Hash(stringified_transaction)
