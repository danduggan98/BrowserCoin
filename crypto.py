import hashlib

def Hash(data):
    return hashlib.sha256(data.encode()).hexdigest()

def HashBlock(block):
    if block is None:
        return None
    
    stringified_block = ''.join(map(str, block.transactions))
    return Hash(stringified_block)

def HashTransaction(transaction):
    if transaction is None:
        return None
    
    stringified_transaction = (
        str(transaction.id) +
        transaction.timestamp +
        str(transaction.transfer_amount) +
        transaction.sender +
        transaction.recipient
    )
    return Hash(str(stringified_transaction))
