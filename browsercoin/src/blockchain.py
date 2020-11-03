from browsercoin.src import crypto, params
import jsonpickle
import datetime as dt
import rsa

class Blockchain:
    def __init__(self):
        #Construct the genesis block
        genesis_block = Block(None)
        genesis_block.idx = 0

        self.chain     = [genesis_block]
        self.head_hash = None
    
    def get_genesis_block(self):
        return self.chain[0]
    
    def get_head(self):
        return self.chain[-1]
    
    def get_head_hash(self):
        return self.head_hash
    
    def add_block(self, block):
        idx = len(self.chain)
        prev_idx = idx - 1
        prev = self.chain[prev_idx]

        block.idx = idx
        block.prev_block = prev_idx #Manually setting this prevents double-spends
        block.prev_hash  = prev.hash if prev is not None else None
        block.hash = crypto.HashBlock(block)

        self.chain.append(block)
        self.head_hash = crypto.HashBlock(block)
        return block
    
    def nth_block(self, n):
        if n >= 0 and n < len(self.chain):
            return self.chain[n]
        return None
    
    def was_tampered(self):
        if self.head_hash != crypto.HashBlock(self.get_head()):
            return True
        
        for block in self.chain[1:]:
            if block.was_tampered():
                return True
            
            prev = self.nth_block(block.prev_block)
            if block.prev_hash != crypto.HashBlock(prev):
                return True
        return False
    
    #Add up the transactions involving this address
    # If a BlockData is given, check that first, then search the chain
    def get_balance(self, address, blockdata=None):
        current_tx = self.latest_address_activity(address, blockdata)
        if current_tx is None:
            return 0
        
        balance = 0

        while current_tx is not None:
            amt = current_tx.transfer_amount

            if current_tx.sender == address:
                balance -= amt
                current_tx = self.find_tx(current_tx.sender_prev_tx)
            else:
                balance += amt
                current_tx = self.find_tx(current_tx.recipient_prev_tx)
        return balance
    
    #Finds the most recent transaction involving the given address
    # If a BlockData is given, check that first, then search the chain
    def latest_address_activity(self, address, blockdata=None):
        latest_tx = blockdata.latest_transaction(address) if blockdata is not None else None
        
        if latest_tx is None:
            for block in reversed(self.chain[1:]):
                latest_tx = block.latest_transaction(address)

                if latest_tx is not None:
                    return latest_tx
            return None
        return latest_tx
    
    def add_tx_to_blockdata(self, tx, blockdata):
        self.add_pointers(tx, blockdata)
        blockdata.add_transaction(tx)
        return blockdata
    
    #Store the block # + idx of this block and its previous transaction pointers
    def add_pointers(self, tx, blockdata):
        tx.add_ptr(len(self), len(blockdata))
        sender_prev    = self.latest_address_activity(tx.sender, blockdata)
        recipient_prev = self.latest_address_activity(tx.recipient, blockdata)

        tx.sender_prev_tx    = sender_prev.ptr if sender_prev is not None else None
        tx.recipient_prev_tx = recipient_prev.ptr if recipient_prev is not None else None
        return tx
    
    #Retrieve a transaction given a transaction pointer
    def find_tx(self, ptr):
        if ptr is None:
            return None
        
        next_block = self.nth_block(ptr.block_idx)
        if next_block is None:
            return None
        
        next_block_txs = next_block.get_transactions()
        if next_block_txs is None:
            return None
        
        if ptr.tx_idx < 0 or ptr.tx_idx >= len(next_block_txs):
            return None
        return next_block_txs[ptr.tx_idx]

    #Checks if a transaction can be added to the chain
    # Not meant to determine if transactions already on the chain are valid - for that it has undefined behavior
    def transaction_is_valid(self, tx, blockdata=None):
        if not tx.is_valid():
            return False
        
        #Masternode public key only needs a valid signature - its balance won't be checked
        if tx.sender == params.MASTERNODE_PK:
            return True
        
        #All other transactions must have a sufficient balance
        sender_balance = self.get_balance(tx.sender, blockdata)
        return tx.transfer_amount <= sender_balance
    
    #Checks if a block can be added to the chain
    # Not meant to determine if blocks already on the chain are valid - for that it has undefined behavior
    def block_is_valid(self, block):
        txs = block.get_transactions()

        if txs is None:
            return True
        
        temp_blockdata = BlockData()
        
        for tx in txs:
            if not self.transaction_is_valid(tx, temp_blockdata):
                return False
            temp_blockdata.add_transaction(tx)
        return True
    
    def __len__(self):
        return len(self.chain)
    
    def __str__(self):
        info = 'Chain Properties\n- Block Height: {}\n- Head Hash: {}\n- Chain Tampered?: {}\n'
        return info.format(len(self), self.head_hash, self.was_tampered())

class Block:
    def __init__(self, data):
        self.idx        = None
        self.timestamp  = str(dt.datetime.now())
        self.prev_block = None
        self.prev_hash  = None
        self.data       = data
        self.hash       = None
    
    def was_tampered(self):
        return self.hash != crypto.HashBlock(self)
    
    def get_transactions(self):
        if self.data is None or self.data.is_empty():
            return None
        return self.data.transactions
    
    def get_coinbase_tx(self):
        txs = self.get_transactions()

        if txs is None:
            return None
        return txs[-1]
    
    def contains_transaction(self, tx):
        return self.data.contains_transaction(tx)

    #Scan the block for transactions with this address
    def latest_transaction(self, address):
        return self.data.latest_transaction(address)
    
    def is_valid(self):
        return self.data.is_valid() and not self.was_tampered()
    
    def to_JSON(self):
        return jsonpickle.encode(self)
    
    def __len__(self):
        return len(self.data)
    
    def __str__(self):
        info = 'Block #{}:\n- Timestamp: {}\n- Hash: {}\n- Previous Block: #{}\n- Previous Hash: {}'
        return info.format(self.idx, self.timestamp, self.hash, self.prev_block, self.prev_hash)
    
    def __eq__(self, other):
        if type(self) != Block or type(other) != Block:
            return False
        return self.data == other.data

class BlockData:
    def __init__(self):
        self.timestamp    = str(dt.datetime.now())
        self.transactions = []
    
    def add_transaction(self, tx):
        if len(self.transactions) <= params.MAX_BLOCK_SIZE:
            self.transactions.append(tx)
        return self
    
    def contains_transaction(self, tx):
        return tx in self.transactions
    
    def latest_transaction(self, address):
        if self.is_empty():
            return None
        
        for tx in reversed(self.transactions):
            if tx.sender == address or tx.recipient == address:
                return tx
        return None
    
    def is_valid(self):
        for tx in self.transactions:
            if not tx.is_valid():
                return False
        return True
    
    def is_empty(self):
        return not len(self.transactions)
    
    def to_JSON(self):
        return jsonpickle.encode(self)
    
    def __len__(self):
        return len(self.transactions)
    
    def __str__(self):
        info = ''
        for idx, tx in enumerate(self.transactions, start=1):
            info += 'Transaction #{}:\n'.format(idx)
            info += str(tx) + '\n'
        return info
    
    def __eq__(self, other):
        if type(self) != BlockData or type(other) != BlockData:
            return False
        return self.transactions == other.transactions

class Transaction:
    def __init__(self, transfer_amount, sender, recipient, sender_prev_tx=None, recipient_prev_tx=None):
        self.timestamp         = str(dt.datetime.now())
        self.transfer_amount   = transfer_amount
        self.sender            = sender
        self.recipient         = recipient
        self.sender_prev_tx    = sender_prev_tx
        self.recipient_prev_tx = recipient_prev_tx
        self.signature         = None
        self.ptr               = None
        self.hash              = crypto.HashTransaction(self)
    
    def was_tampered(self):
        return self.hash != crypto.HashTransaction(self)
    
    def sign(self, secret_key):
        encoded_tx = self.hash.encode()
        
        try:
            sig = rsa.sign(encoded_tx, secret_key, 'SHA-256')
        except:
            return self

        self.signature = sig
        return self
    
    #Tx is valid if it's unmodified, has positive transfer amount, and the signatures check out
    def is_valid(self):
        if self.transfer_amount <= 0 or self.was_tampered():
            return False
        
        if self.signature is None or not self.contains_valid_keys():
            return False
        
        try:
            encoded_tx = self.hash.encode()
            rsa.verify(encoded_tx, self.signature, self.sender) #sender == public key
        except:
            return False
        return True
    
    def add_ptr(self, block_idx, tx_idx):
        self.ptr = TxPointer(block_idx, tx_idx)
        return self
    
    def to_JSON(self):
        return jsonpickle.encode(self)
    
    def contains_valid_keys(self):
        return type(self.sender) is rsa.PublicKey and type(self.recipient) is rsa.PublicKey
    
    def __str__(self):
        info = '- Timestamp: {}\n- Amount: {}\n- Sender: {}\n- Recipient: {}\n'\
               '- Sender Prev Tx: {}\n- Recipient Prev Tx: {}\n- Signature: {}\n- Ptr: {}\n- Hash: {}\n'
        return info.format(
            self.timestamp, self.transfer_amount, self.sender.n, self.recipient.n, str(self.sender_prev_tx),
            str(self.recipient_prev_tx), str(self.signature), str(self.ptr), self.hash
        )
    
    def __eq__(self, other):
        if type(self) != Transaction or type(other) != Transaction:
            return False
        
        cmp_timestamp       = self.timestamp == other.timestamp
        cmp_transfer_amount = self.transfer_amount == other.transfer_amount
        cmp_sender          = self.sender == other.sender
        cmp_recipient       = self.recipient == other.recipient
        return cmp_timestamp and cmp_transfer_amount and cmp_sender and cmp_recipient
    
class TxPointer:
    def __init__(self, block_idx, tx_idx):
        self.block_idx = block_idx
        self.tx_idx    = tx_idx
    
    def __str__(self):
        return 'Block #{}, Tx #{}'.format(self.block_idx, self.tx_idx)
    
    def __eq__(self, other):
        cmp_block_idx = self.block_idx == other.block_idx
        cmp_tx_idx    = self.tx_idx == other.tx_idx
        return cmp_block_idx and cmp_tx_idx
