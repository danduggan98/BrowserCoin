from browsercoin.src import blockchain, crypto, masternode
import rsa

def test_blockchain():
    Transaction = blockchain.Transaction
    BlockData = blockchain.BlockData
    Block = blockchain.Block

    #Create identities
    master = masternode.MasterNode()
    (Me_public, Me_secret)       = rsa.newkeys(512)
    (You_public, You_secret)     = rsa.newkeys(512)
    (Alice_public, Alice_secret) = rsa.newkeys(512)
    (Bob_public, Bob_secret)     = rsa.newkeys(512)

    #Add three blocks, then tamper with the second
    chain = blockchain.Blockchain()
    
    #Block 1
    block1data = BlockData()
    t_00 = Transaction(500, master.public_key, Me_public)   .sign(master.secret_key)
    t_01 = Transaction(1500, master.public_key, You_public) .sign(master.secret_key)
    t_02 = Transaction(200, master.public_key, Alice_public).sign(master.secret_key)
    t_03 = Transaction(600, master.public_key, Bob_public)  .sign(master.secret_key)
    t_04 = Transaction(600, master.public_key, Bob_public)  .sign(Bob_secret) #Wrong secret key

    assert chain.transaction_is_valid(t_00, block1data), 'Valid transaction?'
    assert chain.transaction_is_valid(t_01, block1data), 'Valid transaction?'
    assert chain.transaction_is_valid(t_02, block1data), 'Valid transaction?'
    assert chain.transaction_is_valid(t_03, block1data), 'Valid transaction?'
    assert chain.transaction_is_valid(t_04, block1data) == False, 'Valid transaction?'

    chain.add_tx_to_blockdata(t_00, block1data)
    chain.add_tx_to_blockdata(t_01, block1data)
    chain.add_tx_to_blockdata(t_02, block1data)
    chain.add_tx_to_blockdata(t_03, block1data)

    #Block 1 Coinbase
    master.add_coinbase(Me_public, block1data)
    block1 = Block(block1data)

    print(block1data)
    assert chain.block_is_valid(block1)
    assert len(chain) == 1
    chain.add_block(block1)
    assert len(chain) == 2

    #Block 2
    block2data = BlockData()
    assert chain.get_balance(Me_public, block2data) == 600, 'get_balance works with a blockdata?'
    t1 = Transaction(50, Me_public, You_public).sign(Me_secret)
    assert chain.get_balance(Me_public, block2data) == 600, 'get_balance works with a blockdata?'
    assert chain.transaction_is_valid(t1, block2data), 'Valid transaction?'

    chain.add_tx_to_blockdata(t1, block2data)
    assert chain.get_balance(Me_public, block2data) == 550, 'get_balance works with a blockdata?'

    t1_0 = Transaction(551, Me_public, You_public).sign(Me_secret)
    assert chain.transaction_is_valid(t1_0, block2data) == False, 'Valid transaction?'

    t2 = Transaction(300, You_public, Me_public, t1, t1).sign(You_secret)
    assert chain.transaction_is_valid(t2, block2data), 'Valid transaction?'
    chain.add_tx_to_blockdata(t2, block2data)

    assert t1 == t1, 'Same transactions equal?'
    assert t1 != t2, 'Different transactions equal?'

    #Block 2 Coinbase
    master.add_coinbase(You_public, block2data)
    block2 = Block(block2data)

    print(block2data)
    assert chain.block_is_valid(block2)
    chain.add_block(block2)

    #Block 3
    block3data = BlockData()
    t3 = Transaction(10, Me_public, You_public).sign(Me_secret)
    t4 = Transaction(0, Me_public, You_public).sign(Me_secret)
    t4_0 = Transaction(-100, Me_public, You_public).sign(Me_secret)
    t5 = Transaction(50, Alice_public, Bob_public).sign(Alice_secret)
    t6 = Transaction(300, Bob_public, Alice_public).sign(Bob_secret)

    assert chain.transaction_is_valid(t3, block3data), 'Valid transaction?'
    assert chain.transaction_is_valid(t4, block3data) == False, 'Non-positive transaction valid?'
    assert chain.transaction_is_valid(t4_0, block3data) == False, 'Non-positive transaction valid?'
    assert chain.transaction_is_valid(t5, block3data), 'Valid transaction?'
    assert chain.transaction_is_valid(t6, block3data), 'Valid transaction?'

    chain.add_tx_to_blockdata(t3, block3data)
    chain.add_tx_to_blockdata(t5, block3data)
    chain.add_tx_to_blockdata(t6, block3data)

    master.add_coinbase(Alice_public, block3data)
    block3 = Block(block3data)

    print(block3data)
    assert chain.block_is_valid(block3)
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

    assert chain.nth_block(2).was_tampered() == False, 'Unmodified block not tampered?'
    chain.add_pointers(t4, block3data)
    chain.nth_block(2).data.add_transaction(t4) #Tamper with the block
    assert chain.nth_block(2).is_valid() == False, 'Tampered block valid?'
    assert chain.block_is_valid(chain.nth_block(2)) == False
    assert chain.nth_block(2).was_tampered(), 'Modified block tampered?'
    
    assert chain.nth_block(1) != chain.nth_block(2), 'Different blocks equal?'
    assert chain.nth_block(1) == chain.nth_block(1), 'Same blocks equal?'

    #Check the balance of each address
    assert chain.get_balance(Me_public) == 840, 'get_balance works?'
    assert chain.get_balance(You_public) == 1360, 'get_balance works?'
    assert chain.get_balance(Alice_public) == 550, 'get_balance works?'
    assert chain.get_balance(Bob_public) == 350, 'get_balance works?'
    assert chain.get_balance('Somebody else') == 0, 'get_balance works?'
    assert chain.latest_address_activity(Me_public) == chain.latest_address_activity(You_public)
    assert chain.latest_address_activity(Alice_public) is not t6
    assert chain.latest_address_activity(Bob_public) is t6
    assert chain.nth_block(3).contains_transaction(t6)
    assert chain.nth_block(3).contains_transaction(t1) == False

    #Check new transactions for validity
    valid_tx = Transaction(10, Bob_public, Alice_public).sign(Bob_secret)
    invalid_tx = Transaction(1000000, Bob_public, Alice_public).sign(Bob_secret) #Invalid amount
    invalid_tx2 = Transaction(10, Bob_public, Alice_public).sign(Alice_secret) #Signed w/ wrong secret
    invalid_tx3 = Transaction(10, Bob_public, Alice_public).sign(Bob_secret) #Tamper with otherwise valid tx
    invalid_tx3.transfer_amount = 5000
    invalid_tx4 = Transaction(10, Bob_public, Alice_public) #No signature but otherwise valid

    assert chain.transaction_is_valid(valid_tx), 'Valid transaction?'
    assert chain.transaction_is_valid(invalid_tx) == False, 'Valid transaction?'
    assert chain.transaction_is_valid(invalid_tx2) == False, 'Valid transaction?'
    assert chain.transaction_is_valid(invalid_tx3) == False, 'Valid transaction?'
    assert chain.transaction_is_valid(invalid_tx4) == False, 'Valid transaction?'
    assert chain.transaction_is_valid(t_00), 'Masternode transaction valid?'

    invalid_block_data = BlockData()
    invalid_block_data.add_transaction(invalid_tx)
    invalid_block_data.add_transaction(invalid_tx2)
    invalid_block_data.add_transaction(invalid_tx3)
    invalid_block_data.add_transaction(invalid_tx4)
    master.add_coinbase(Alice_public, invalid_block_data)
    invalid_block = Block(invalid_block_data)
    assert chain.block_is_valid(invalid_block) == False

    t_04 = Transaction(500, master.public_key, Me_public)
    assert chain.transaction_is_valid(t_04) == False, 'Can anybody give themselves money?'

    #Check the final state of the chain
    assert len(chain) == 4, 'Proper chain length?'
    assert chain.get_genesis_block().idx == 0, 'get_genesis_block works?'
    assert chain.get_head().idx == 3, 'get_head works?'
    assert chain.get_head_hash() == crypto.HashBlock(chain.get_head()), 'head_hash works?'
    assert chain.was_tampered(), 'chain tampered?'
