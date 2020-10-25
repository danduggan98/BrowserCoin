from browsercoin.src import crypto, params
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
        block.idx = idx

        prev = self.chain[idx-1]
        block.prev_block = prev #Adding this pointer automatically prevents double-spends
        block.prev_hash  = prev.hash if prev is not None else None

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
        
        for block in self.chain:
            if block.prev_was_tampered():
                return True
        return False
    
    #Add up the transactions involving this address
    # If a BlockData is given, check that first, then search the chain
    def get_balance(self, address, blockData=None):
        current_tx = self.latest_address_activity(address, blockData)
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
    # If a BlockData is given, check that first, then search the chain
    def latest_address_activity(self, address, blockdata=None):
        prev_tx = blockdata.latest_transaction(address) if blockdata is not None else None

        if (prev_tx is None):
            prev_tx = self.get_head().latest_transaction(address)
        return prev_tx
    
    #Checks if a transaction can be added to the chain
    #Not meant to determine if transactions already on the chain are valid - for that it has undefined behavior
    def transaction_is_valid(self, tx, blockdata=None):
        if (tx.transfer_amount <= 0): #Transactions must have a positive balance
            return False
        
        #Masternode public key only needs a valid signature - its balance won't be checked
        if (tx.sender == crypto.LoadMasterNodeKeys()[0] and tx.is_valid()):
            return True
        
        #All other transactions must have a sufficient balance
        sender_balance = self.get_balance(tx.sender, blockdata)

        if (not tx.is_valid() or sender_balance is None):
            return False
        return tx.transfer_amount <= sender_balance
    
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
        self.hash       = crypto.HashBlockData(data)
    
    def was_tampered(self):
        return self.hash != crypto.HashBlockData(self.data)
    
    def prev_was_tampered(self):
        return self.prev_hash != crypto.HashBlock(self.prev_block)
    
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

    #Scan the chain, starting from this block, for transactions with this address
    def latest_transaction(self, address):
        address_found = False
        current_block = self
        current_tx = None

        #Start from this block and move backward, traversing all previous
        # blocks until a transaction including the address is found
        while (current_block.prev_block is not None):
            current_block_data = current_block.data

            if current_block_data.is_empty():
                current_block = current_block.prev_block
                continue
            
            current_tx = current_block_data.latest_transaction(address)

            if (current_tx is None):
                current_block = current_block.prev_block
            else:
                address_found = True
                break

        if (address_found == False):
            return None
        return current_tx
    
    def is_valid(self):
        return self.data.is_valid() and not self.was_tampered()
    
    def __len__(self):
        return len(self.data)
    
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
        return self
    
    #Create a transaction sending the block reward from
    # the master node's public key to the output address
    def add_coinbase(self, output_address, prev_coinbase_tx, output_prev_tx):
        (masternode_pk, masternode_sk) = crypto.LoadMasterNodeKeys()

        coinbase = (
            Transaction(params.BLOCK_REWARD, masternode_pk, output_address, prev_coinbase_tx, output_prev_tx)
            .sign(masternode_sk)
        )
        
        self.transactions.append(coinbase)
        return self
    
    def contains_transaction(self, tx):
        return tx in self.transactions
    
    def latest_transaction(self, address):
        for tx in reversed(self.transactions):
            if (tx.sender == address or tx.recipient == address):
                return tx
        return None
    
    def is_valid(self):
        for tx in self.transactions:
            if not tx.is_valid():
                return False
        return True
    
    def is_empty(self):
        return len(self.transactions) == 0
    
    def __len__(self):
        return len(self.transactions)
    
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
    def __init__(self, transfer_amount, sender, recipient, sender_prev_tx=None, recipient_prev_tx=None):
        self.timestamp         = str(dt.datetime.now())
        self.transfer_amount   = transfer_amount
        self.sender            = sender
        self.recipient         = recipient
        self.sender_prev_tx    = sender_prev_tx
        self.recipient_prev_tx = recipient_prev_tx
        self.signature         = None
        self.hash              = crypto.HashTransaction(self)
    
    def was_tampered(self):
        return self.hash != crypto.HashTransaction(self)
    
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
        info = '- Timestamp: {}\n- Amount: {}\n- Sender: {}\n- Recipient: {}\n- Signature: {}\n- Hash: {}\n'
        return info.format(self.timestamp, self.transfer_amount, self.sender.n, self.recipient.n, self.signature, self.hash)
    
    def __eq__(self, other):
        if (type(self) != Transaction or type(other) != Transaction):
            return False
        
        cmp_transfer_amount = self.transfer_amount == other.transfer_amount
        cmp_sender          = self.sender == other.sender
        cmp_recipient       = self.recipient == other.recipient
        return cmp_transfer_amount and cmp_sender and cmp_recipient
