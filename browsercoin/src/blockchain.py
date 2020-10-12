import datetime as dt
import rsa
import src.params as params
from src.crypto import Hash, HashBlock, HashBlockData, HashTransaction

class Blockchain:
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
    
    #Add up the transactions involving this address
    def get_balance(self, address):
        current_tx = self.latest_address_activity(address)
        if current_tx is None:
            return None
        
        balance = 0

        while (current_tx is not None):
            amt = current_tx.transfer_amount

            if (current_tx.sender == address):
                balance -= amt
                current_tx = current_tx.sender_prev_tx
            else:
                balance += amt
                current_tx = current_tx.recipient_prev_tx
                    
        return balance
    
    #Finds the most recent transaction involving the given address
    def latest_address_activity(self, address):
        address_found = False
        current_block = self.get_head()
        current_tx = None

        #Start from the head and move backward
        # until a transaction including the address is found
        while (current_block is not self.get_genesis_block()):
            txs = current_block.get_transactions()

            if txs is None:
                current_block = current_block.prev_block
                continue
            
            for tx in reversed(txs):
                if (tx.sender == address or tx.recipient == address):
                    current_tx = tx
                    address_found = True
                    break
            else:
                current_block = current_block.prev_block
                continue
            break

        if (address_found == False):
            return None
        
        return current_tx
    
    #Checks if a transaction can be added to the chain
    """
    - Not meant to determine if transactions already on the chain are valid:
        for that purpose its behavior is essentially undefined
    - Existing transactions must have been valid to add them initially, so 
        we know they are genuine by virtue of their presence on the chain
    """
    def transaction_is_valid(self, tx):
        sender_balance = self.get_balance(tx.sender)

        if (not tx.is_valid() or sender_balance is None):
            return False
        
        return tx.transfer_amount <= sender_balance

class Block:
    def __init__(self, idx, prev_block, data):
        self.idx        = idx
        self.timestamp  = str(dt.datetime.now())
        self.prev_block = prev_block
        self.prev_hash  = prev_block.hash if prev_block is not None else None
        self.data       = data
        self.hash       = HashBlockData(data)
    
    def was_tampered(self):
        return self.hash != HashBlockData(self.data)
    
    def prev_was_tampered(self):
        return self.prev_hash != HashBlock(self.prev_block)
    
    def get_transactions(self):
        if self.data is None or len(self.data.transactions) == 0:
            return None
        
        return self.data.transactions
    
    def is_valid(self):
        if self.get_transactions() is None or self.was_tampered():
            return False
        
        return self.data.is_valid()
    
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
    
    def add_transaction(self, tx):
        if (len(self.transactions) < params.MAX_BLOCK_SIZE):
            self.transactions.append(tx)
    
    def is_valid(self):
        if len(self.transactions) == 0:
            return False
         
        for tx in self.transactions:
            if not tx.is_valid():
                return False
        
        return True
    
    def __str__(self):
        info = ''
        for idx, tx in enumerate(self.transactions, start=1):
            info += 'Transaction #{}:\n'.format(idx)
            info += str(tx) + '\n'
        return info
    
    def __eq__(self, other):
        if (type(self) != BlockData or type(other) != BlockData):
            return False
        
        return self.transactions == other.transactions

class Transaction:
    def __init__(self, transfer_amount, sender, recipient, sender_prev_tx, recipient_prev_tx):
        self.timestamp         = str(dt.datetime.now())
        self.transfer_amount   = transfer_amount
        self.sender            = sender
        self.recipient         = recipient
        self.sender_prev_tx    = sender_prev_tx
        self.recipient_prev_tx = recipient_prev_tx
        self.signature         = None
        self.hash              = HashTransaction(self)
    
    def was_tampered(self):
        return self.hash != HashTransaction(self)
    
    def sign(self, secret_key):
        encoded_tx = self.hash.encode('utf8')
        self.signature = rsa.sign(encoded_tx, secret_key, 'SHA-256')
        return self
    
    #Returns true only if the transaction is unmodified and the signatures check out
    def is_valid(self):
        if self.signature is None or self.was_tampered():
            return False
        
        encoded_tx = self.hash.encode('utf8')
        try:
            valid = rsa.verify(encoded_tx, self.signature, self.sender) #sender == public key
        except:
            return False
        
        return True
    
    def __str__(self):
        info = '- Timestamp: {}\n- Amount: {}\n- Sender: {}\n- Recipient: {}\n- Hash: {}'
        return info.format(self.timestamp, self.transfer_amount, self.sender, self.recipient, self.hash)
    
    def __eq__(self, other):
        if (type(self) != Transaction or type(other) != Transaction):
            return False
        
        cmp_transfer_amount = self.transfer_amount == other.transfer_amount
        cmp_sender          = self.sender == other.sender
        cmp_recipient       = self.recipient == other.recipient

        return cmp_transfer_amount and cmp_sender and cmp_recipient
