import hashlib
import src.blockchain as blockchain

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
        transaction.recipient +
        str(transaction.signature)
    )
    return Hash(stringified_transaction)
