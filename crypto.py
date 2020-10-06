import hashlib

def Hash(data):
    return hashlib.sha256(data.encode()).hexdigest()

def HashBlock(block):
    if block is None:
        return None
    
    stringified_block = ''.join(block.transactions)
    return Hash(stringified_block)
