import datetime as dt
from crypto import *

class Blockchain:
    block_size = 50 # Max of 50 transactions per block

    def __init__(self):
        self.chain = [self.create_genesis_block()]
    
    def __len__(self):
        return len(self.chain)
    
    def create_genesis_block(self):
        return Block (0, dt.datetime(2020, 1, 1), None, None)
    
    def get_genesis_block(self):
        return self.chain[0]
    
    def get_head(self):
        return self.chain[-1]
    
    def add_block(self, data):
        idx  = len(self.chain)
        prev = self.chain[idx-1]

        new_block = Block(idx, str(dt.datetime.now()), prev, data)
        self.chain.append(new_block)
    
    def nth_block(self, n):
        return self.chain[n] if n < len(self.chain) and n >=0 else None

class Block:
    def __init__(self, idx, timestamp, prev_block, data):
        self.idx        = idx
        self.timestamp  = timestamp
        self.prev_block = prev_block
        self.prev_hash  = prev_block.hash if prev_block is not None else None
        self.data       = data
        self.hash       = HashBlock(data)
    
    def __str__(self):
        prev = self.prev_block
        prev_idx = ('#' + str(prev.idx)) if prev is not None else None

        info = 'Block #{}:\n- Timestamp: {}\n- Previous Block: {}\n- Previous Hash: {}'
        return info.format(self.idx, self.timestamp, prev_idx, self.prev_hash)
    
class BlockData:
    def __init__(self):
        self.transactions = []
    
    def add_transaction(self, transaction):
        if (len(self.transactions) < Blockchain.block_size):
            self.transactions.append(transaction)
        
    def __str__(self):
        info = ''
        for idx, transaction in enumerate(self.transactions, start=1):
            info += 'Transaction #{}:\n'.format(idx)
            info += str(transaction) + '\n'
        return info

class Transaction:
    def __init__(self, transfer_amount, sender, recipient):
        self.id = None
        self.timestamp = str(dt.datetime.now())
        self.transfer_amount = transfer_amount
        self.sender = sender
        self.recipient = recipient
        self.hash = HashTransaction(self)
    
    def __str__(self):
        info = '- ID: {}\n- Timestamp: {}\n- Amount: {}\n- Sender: {}\n- Recipient: {}\n- Hash: {}'
        return info.format(self.id, self.timestamp, self.transfer_amount, self.sender, self.recipient, self.hash)
