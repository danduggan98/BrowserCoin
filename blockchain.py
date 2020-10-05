import datetime as dt
import hashlib

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
    
    def __len__(self):
        return len(self.chain)
    
    def create_genesis_block(self):
        return Block (
            0, dt.datetime(2020, 1, 1), None, None, None
        )
    
    def add_block(self, data):
        idx  = len(self.chain)
        prev = self.chain[idx-1]

        new_block = Block(
            idx, str(dt.datetime.now()), prev, None, data #Update this to use the hash of prev as prev_block 
        )
        self.chain.append(new_block)
    
    def nth_block(self, n):
        return self.chain[n] if n < len(self.chain) and n >=0 else None

class Block:  
    def __init__(self, idx, timestamp, prev_block, prev_hash, data):
        self.idx = idx
        self.timestamp = timestamp
        self.prev_block = prev_block
        self.prev_hash  = prev_hash
        self.data = data
    
    def __str__(self):
        prev = self.prev_block
        prev_idx = ('#' + str(prev.idx)) if prev is not None else None

        info = 'Block #{}:\n- Timestamp: {}\n- Previous Block: {}\n- Previous Hash: {}'
        return info.format(self.idx, self.timestamp, prev_idx, self.prev_hash)
    
class BlockData:
    def __init__(self):
        self.transactions = []

class Transaction:
    def __init__(self):
        self.id = None
        self.timestamp = None

#Create a chain for testing
chain = Blockchain()
chain.add_block(None)
chain.add_block(None)
print(chain.nth_block(0))
print(chain.nth_block(1))
print(chain.nth_block(2))
print('Chain has {} block{}'.format(len(chain), 's' if len(chain) > 1 else ''))
