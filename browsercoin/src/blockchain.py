import datetime as dt
from src.crypto import Hash, HashBlock, HashBlockData, HashTransaction

class Blockchain:
    block_size = 50 # Max of 50 transactions per block

    def __init__(self):
        self.chain     = [Block (0, None, None)] #Genesis block
        self.head_hash = None
    
    def __len__(self):
        return len(self.chain)
    
    def get_genesis_block(self):
        return self.chain[0]
    
    def get_head(self):
        return self.chain[-1]
    
    def get_head_hash(self):
        return self.head_hash
    
    def add_block(self, data):
        idx  = len(self.chain)
        prev = self.chain[idx-1]

        new_block = Block(idx, prev, data)
        self.chain.append(new_block)
        self.head_hash = HashBlock(new_block)
    
    def nth_block(self, n):
        return self.chain[n] if n < len(self.chain) and n >=0 else None
    
    def was_tampered(self):
        if self.head_hash != HashBlock(self.get_head()):
            return True
        
        for block in self.chain:
            if block.prev_was_tampered():
                return True
        
        return False
    
    def get_balance(self, address, last_tx=None):
        current_tx = last_tx
        balance = 0
        
        #If no last_tx specified, start from the head and move backward
        # until a transaction including the address is found
        if current_tx is None:
            current_block = self.get_head()

            while (current_block is not self.get_genesis_block()):
                txs = current_block.get_transactions()
                
                for tx in txs:
                    if (tx.sender == address or tx.recipient == address):
                        current_tx = tx
                        break
                else:
                    current_block = current_block.prev_block
                    continue
                break
        
        #Once the last transaction is found, follow the chain backward
        # and add up the transactions from this address
        while (current_tx.sender is not None):
            amt = current_tx.transfer_amount

            if (current_tx.sender == address):
                balance -= current_tx.transfer_amount
            else:
                balance += current_tx.transfer_amount
            current_tx = current_tx.s
        
        return balance
    
    def transaction_is_valid(self, tx):
        if (not tx.is_valid()):
            return False
        
        return tx.transfer_amount <= get_balance(tx.sender)

class Block:
    def __init__(self, idx, prev_block, data):
        self.idx        = idx
        self.timestamp  = str(dt.datetime.now())
        self.prev_block = prev_block
        self.prev_hash  = prev_block.hash if prev_block is not None else None
        self.data       = data
        self.hash       = HashBlockData(data)
    
    def prev_was_tampered(self):
        return self.prev_hash != HashBlock(self.prev_block)
    
    def get_transactions(self):
        if self.data is None:
            return None
        
        return self.data.transactions
    
    def __str__(self):
        prev = self.prev_block
        prev_idx = ('#' + str(prev.idx)) if prev is not None else None

        info = 'Block #{}:\n- Timestamp: {}\n- Hash: {}\n- Previous Block: {}\n- Previous Hash: {}'
        return info.format(self.idx, self.timestamp, self.hash, prev_idx, self.prev_hash)
    
    def __eq__(self, other):
        if (type(self) != Block or type(other) != Block):
            return False
        
        return self.data == other.data

class BlockData:
    def __init__(self):
        self.timestamp    = str(dt.datetime.now())
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
    
    def __eq__(self, other):
        if (type(self) != BlockData or type(other) != BlockData):
            return False
        
        return self.transactions == other.transactions

class Transaction:
    def __init__(self, transfer_amount, sender, recipient, prev_tx, signature):
        self.id              = None
        self.timestamp       = str(dt.datetime.now())
        self.transfer_amount = transfer_amount
        self.sender          = sender
        self.recipient       = recipient
        self.prev_tx         = prev_tx
        self.signature       = signature
        self.hash            = HashTransaction(self)
    
    def was_tampered(self):
        return self.hash != HashTransaction(self)
    
    def sign(self, secret_key): #TODO
        return True
    
    def is_valid(self): #TODO - RUNS VERIFY FUNCTION ON THE GIVEN SIGNATURE USING THE GIVEN SENDER'S PK
        return True
    
    def __str__(self):
        info = '- ID: {}\n- Timestamp: {}\n- Amount: {}\n- Sender: {}\n- Recipient: {}\n- Hash: {}'
        return info.format(self.id, self.timestamp, self.transfer_amount, self.sender, self.recipient, self.hash)
    
    def __eq__(self, other):
        if (type(self) != Transaction or type(other) != Transaction):
            return False
        
        cmp_id              = self.id == other.id
        cmp_transfer_amount = self.transfer_amount == other.transfer_amount
        cmp_sender          = self.sender == other.sender
        cmp_recipient       = self.recipient == other.recipient

        return cmp_id and cmp_transfer_amount and cmp_sender and cmp_recipient
