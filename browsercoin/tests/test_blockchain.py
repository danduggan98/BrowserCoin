from browsercoin.src import blockchain, crypto, masternode
import rsa

def test_blockchain():
    Transaction = blockchain.Transaction
    BlockData = blockchain.BlockData
    Block = blockchain.Block

    #Create identities
    master = masternode.MasterNode()
    (Me_public, Me_secret) = rsa.newkeys(512)
    (You_public, You_secret) = rsa.newkeys(512)
    (Alice_public, Alice_secret) = rsa.newkeys(512)
    (Bob_public, Bob_secret) = rsa.newkeys(512)

    #Add three blocks, then tamper with the second
    chain = blockchain.Blockchain()
    
    #Block 1
    block1data = BlockData()
    t_00 = Transaction(500, master.public_key, Me_public, None, None).sign(master.secret_key)
    t_01 = Transaction(1500, master.public_key, You_public, t_00, None).sign(master.secret_key)
    t_02 = Transaction(200, master.public_key, Alice_public, t_01, None).sign(master.secret_key)
    t_03 = Transaction(600, master.public_key, Bob_public, t_02, None).sign(master.secret_key)
    t_04 = Transaction(600, master.public_key, Bob_public, t_02, None).sign(Bob_secret) #Wrong secret key

    assert chain.transaction_is_valid(t_00, block1data), 'Valid transaction?'
    assert chain.transaction_is_valid(t_01, block1data), 'Valid transaction?'
    assert chain.transaction_is_valid(t_02, block1data), 'Valid transaction?'
    assert chain.transaction_is_valid(t_03, block1data), 'Valid transaction?'
    assert chain.transaction_is_valid(t_04, block1data) == False, 'Valid transaction?'

    block1data.add_transaction(t_00)
    block1data.add_transaction(t_01)
    block1data.add_transaction(t_02)
    block1data.add_transaction(t_03)

    #Block 1 Coinbase
    prev_coinbase_tx = chain.latest_address_activity(master.public_key, block1data)
    output_prev_tx = chain.latest_address_activity(Me_public, block1data) #Me recieves first block reward
    master.add_coinbase(block1data, Me_public, prev_coinbase_tx, output_prev_tx)
    block1 = Block(block1data)
    chain.add_block(block1)

    #Block 2
    block2data = BlockData()
    assert chain.get_balance(Me_public, block2data) == 550, 'get_balance works with a blockdata?'
    t1 = Transaction(50, Me_public, You_public, chain.latest_address_activity(Me_public), t_01).sign(Me_secret)
    assert chain.get_balance(Me_public, block2data) == 550, 'get_balance works with a blockdata?'
    assert chain.transaction_is_valid(t1, block2data), 'Valid transaction?'

    block2data.add_transaction(t1)
    assert chain.get_balance(Me_public, block2data) == 500, 'get_balance works with a blockdata?'

    t1_0 = Transaction(501, Me_public, You_public, chain.latest_address_activity(Me_public, block2data), chain.latest_address_activity(You_public, block2data)).sign(Me_secret)
    assert chain.transaction_is_valid(t1_0, block2data) == False, 'Valid transaction?'

    t2 = Transaction(300, You_public, Me_public, t1, t1).sign(You_secret)
    assert chain.transaction_is_valid(t2, block2data), 'Valid transaction?'
    block2data.add_transaction(t2)

    assert t1 == t1, 'Same transactions equal?'
    assert t1 != t2, 'Different transactions equal?'

    #Block 2 Coinbase
    prev_coinbase_tx = chain.latest_address_activity(master.public_key, block2data)
    output_prev_tx = chain.latest_address_activity(You_public, block2data) #Me recieves first block reward
    master.add_coinbase(block2data, You_public, prev_coinbase_tx, output_prev_tx)
    block2 = Block(block2data)
    chain.add_block(block2)

    #Block 3
    block3data = BlockData()
    t3 = Transaction(10, Me_public, You_public, t2, chain.latest_address_activity(You_public)).sign(Me_secret)
    t4 = Transaction(0, Me_public, You_public, t3, t3).sign(Me_secret)
    t4_0 = Transaction(-100, Me_public, You_public, t3, t3).sign(Me_secret)
    t5 = Transaction(50, Alice_public, Bob_public, t_02, t_03).sign(Alice_secret)
    t6 = Transaction(300, Bob_public, Alice_public, t5, t5).sign(Bob_secret)

    assert chain.transaction_is_valid(t3, block3data), 'Valid transaction?'
    assert chain.transaction_is_valid(t4, block3data) == False, 'Non-positive transaction valid?'
    assert chain.transaction_is_valid(t4_0, block3data) == False, 'Non-positive transaction valid?'
    assert chain.transaction_is_valid(t5, block3data), 'Valid transaction?'
    assert chain.transaction_is_valid(t6, block3data), 'Valid transaction?'

    block3data.add_transaction(t3)
    block3data.add_transaction(t5)
    block3data.add_transaction(t6)

    prev_coinbase_tx = chain.latest_address_activity(master.public_key, block3data)
    output_prev_tx = chain.latest_address_activity(Alice_public, block3data) #Me recieves first block reward
    master.add_coinbase(block3data, Alice_public, prev_coinbase_tx, output_prev_tx)
    block3 = Block(block3data)
    chain.add_block(block3)

    assert BlockData() != block1data, 'Different BlockDatas equal?'
    assert BlockData() == BlockData(), 'Same BlockDatas equal?'
    assert BlockData().is_valid(), 'Empty BlockData valid?'
    assert block1data.is_valid(), 'BlockData valid?'
    assert block2data.is_valid(), 'BlockData valid?'
    assert block3data.is_valid(), 'BlockData valid?'

    assert chain.nth_block(1).is_valid(), 'Block valid?'
    assert chain.nth_block(2).is_valid(), 'Block valid?'
    assert chain.nth_block(3).is_valid(), 'Block valid?'

    assert chain.nth_block(3).prev_was_tampered() == False, 'Unmodified block not tampered?'
    chain.nth_block(2).data.add_transaction(t4) #Tamper with the block
    assert chain.nth_block(2).is_valid() == False, 'Tampered block valid?'
    assert chain.nth_block(3).prev_was_tampered() == True, 'Modified block tampered?'
    
    assert chain.nth_block(1) != chain.nth_block(2), 'Different blocks equal?'
    assert chain.nth_block(1) == chain.nth_block(1), 'Same blocks equal?'

    #Check the balance of each address
    assert chain.get_balance(Me_public) == 790, 'get_balance works?'
    assert chain.get_balance(You_public) == 1310, 'get_balance works?'
    assert chain.get_balance(Alice_public) == 500, 'get_balance works?'
    assert chain.get_balance(Bob_public) == 350, 'get_balance works?'
    assert chain.get_balance('Somebody else') == None, 'get_balance works?'
    assert chain.latest_address_activity(Me_public) == chain.latest_address_activity(You_public)
    assert (chain.latest_address_activity(Alice_public) is t6) == False
    assert chain.latest_address_activity(Bob_public) is t6
    assert chain.nth_block(3).contains_transaction(t6)
    assert chain.nth_block(3).contains_transaction(t1) == False

    #Check new transactions for validity
    valid_tx = Transaction(10, Bob_public, Alice_public, t5, t5).sign(Bob_secret)
    invalid_tx = Transaction(1000000, Bob_public, Alice_public, t6, t6).sign(Bob_secret) #Invalid amount
    invalid_tx2 = Transaction(10, Bob_public, Alice_public, t5, t5).sign(Alice_secret) #Signed w/ wrong secret
    invalid_tx3 = Transaction(10, Bob_public, Alice_public, t5, t5).sign(Bob_secret) #Tamper with otherwise valid tx
    invalid_tx3.transfer_amount = 5000
    invalid_tx4 = Transaction(10, Bob_public, Alice_public, t5, t5) #No signature but otherwise valid

    assert chain.transaction_is_valid(valid_tx) == True, 'Valid transaction?'
    assert chain.transaction_is_valid(invalid_tx) == False, 'Valid transaction?'
    assert chain.transaction_is_valid(invalid_tx2) == False, 'Valid transaction?'
    assert chain.transaction_is_valid(invalid_tx3) == False, 'Valid transaction?'
    assert chain.transaction_is_valid(invalid_tx4) == False, 'Valid transaction?'
    assert chain.transaction_is_valid(t_00) == True, 'Masternode transaction valid?'

    t_04 = Transaction(500, master.public_key, Me_public, None, None)
    assert chain.transaction_is_valid(t_04) == False, 'Can anybody give themselves money?'

    #Check the final state of the chain
    assert len(chain) == 4, 'Proper chain length?'
    assert chain.get_genesis_block().idx == 0, 'get_genesis_block works?'
    assert chain.get_head().idx == 3, 'get_head works?'
    assert chain.get_head_hash() == crypto.HashBlock(chain.get_head()), 'head_hash works?'
    assert chain.was_tampered() == True, 'chain tampered?'
