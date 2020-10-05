import datetime as dt
import hashlib

class Blockchain:
    def __init__(self):
        self.head = Block()
        self.chain = [self.head]
    
    def add_block(self):
        new_block = Block()
        new_block.idx = len(self.chain)
        new_block.timestamp = str(dt.datetime.now())
        self.chain.append(new_block)
    
    def nth_block(self, n):
        return self.chain[n]

class Block:
    def __init__(self):
        self.idx = 0
        self.timestamp  = None
        self.prev_block = None
        self.prev_hash  = None
        self.data = BlockData()
    
    def print(self):
        info = 'Block #{}:\n- Timestamp: {}\n- Previous Block: {}\n- Previous Hash: {}'
        print(info.format(self.idx, self.timestamp, self.prev_block, self.prev_hash))
    
class BlockData:
    def __init__(self):
        self.transactions = []

class Transaction:
    def __init__(self):
        self.id = None
        self.timestamp = None

#Create a chain for testing
chain = Blockchain()
chain.head.print()
chain.add_block()
chain.nth_block(1).print()
