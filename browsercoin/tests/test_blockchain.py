import src.blockchain as blockchain
import src.crypto as crypto
import src.node as node
import rsa

def test_blockchain():
    #Create identities
    (Me_public, Me_secret) = rsa.newkeys(512)
    (You_public, You_secret) = rsa.newkeys(512)
    (Alice_public, Alice_secret) = rsa.newkeys(512)
    (Bob_public, Bob_secret) = rsa.newkeys(512)

    #Create transactions
    chain = blockchain.Blockchain()
    master = node.MasterNode()

    t_00 = blockchain.Transaction(500, node.masternode_pk, Me_public, None, None).sign(node.masternode_sk)
    t_01 = blockchain.Transaction(1500, node.masternode_pk, You_public, None, None).sign(node.masternode_sk)
    t_02 = blockchain.Transaction(200, node.masternode_pk, Alice_public, None, None).sign(node.masternode_sk)
    t_03 = blockchain.Transaction(600, node.masternode_pk, Bob_public, None, None).sign(node.masternode_sk)
    t1 = blockchain.Transaction(50, Me_public, You_public, t_00, t_01).sign(Me_secret)
    t2 = blockchain.Transaction(300, You_public, Me_public, t1, t1).sign(You_secret)
    t3 = blockchain.Transaction(10, Me_public, You_public, t2, t2).sign(Me_secret)
    t4 = blockchain.Transaction(0, Me_public, You_public, t3, t3).sign(Me_secret)
    t5 = blockchain.Transaction(50, Alice_public, Bob_public, t_02, t_03).sign(Alice_secret)
    t6 = blockchain.Transaction(300, Bob_public, Alice_public, t5, t5).sign(Bob_secret)

    assert t1 == t1, 'Same transactions equal?'
    assert t1 != t2, 'Different transactions equal?'

    #Add three blocks, then tamper with the second
    block1data = blockchain.BlockData()
    block1data.add_transaction(t_00)
    block1data.add_transaction(t_01)
    block1data.add_transaction(t_02)
    block1data.add_transaction(t_03)

    block2data = blockchain.BlockData()
    block2data.add_transaction(t1)
    block2data.add_transaction(t2)

    block3data = blockchain.BlockData()
    block3data.add_transaction(t3)
    block3data.add_transaction(t5)
    block3data.add_transaction(t6)

    assert blockchain.BlockData() != block1data, 'Different BlockDatas equal?'
    assert blockchain.BlockData() == blockchain.BlockData(), 'Same BlockDatas equal?'
    assert blockchain.BlockData().is_valid() == True, 'Empty BlockData valid?'
    assert block1data.is_valid(), 'BlockData valid?'
    assert block2data.is_valid(), 'BlockData valid?'
    assert block3data.is_valid(), 'BlockData valid?'

    chain.add_block(block1data)
    chain.add_block(block2data)
    chain.add_block(block3data)

    assert chain.nth_block(1).is_valid(), 'Block valid?'
    assert chain.nth_block(2).is_valid(), 'Block valid?'
    assert chain.nth_block(3).is_valid(), 'Block valid?'

    assert chain.nth_block(3).prev_was_tampered() == False, 'Unmodified block not tampered?'
    chain.nth_block(2).data = blockchain.BlockData().add_transaction(t4) #Tamper with the block
    assert chain.nth_block(2).is_valid() == False, 'Tampered block valid?'
    assert chain.nth_block(3).prev_was_tampered() == True, 'Modified block tampered?'
    
    assert chain.nth_block(1) != chain.nth_block(2), 'Different blocks equal?'
    assert chain.nth_block(1) == chain.nth_block(1), 'Same blocks equal?'

    #Check the balance of each address
    assert chain.get_balance(Me_public) == 740, 'get_balance works?'
    assert chain.get_balance(You_public) == 1260, 'get_balance works?'
    assert chain.get_balance(Alice_public) == 450, 'get_balance works?'
    assert chain.get_balance(Bob_public) == 350, 'get_balance works?'
    assert chain.get_balance('Somebody else') == None, 'get_balance works?'
    assert chain.latest_address_activity(Me_public) == chain.latest_address_activity(You_public)
    assert chain.latest_address_activity(Alice_public) is t6
    assert chain.latest_address_activity(Bob_public) is t6

    #Check new transactions for validity
    valid_tx = blockchain.Transaction(10, Bob_public, Alice_public, t5, t5).sign(Bob_secret)
    invalid_tx = blockchain.Transaction(1000000, Bob_public, Alice_public, t6, t6).sign(Bob_secret) #Invalid amount
    invalid_tx2 = blockchain.Transaction(10, Bob_public, Alice_public, t5, t5).sign(Alice_secret) #Signed w/ wrong secret
    invalid_tx3 = blockchain.Transaction(10, Bob_public, Alice_public, t5, t5).sign(Bob_secret) #Tamper with otherwise valid tx
    invalid_tx3.transfer_amount = 50
    invalid_tx4 = blockchain.Transaction(10, Bob_public, Alice_public, t5, t5) #No signature but otherwise valid

    assert chain.transaction_is_valid(valid_tx) == True, 'Valid transaction?'
    assert chain.transaction_is_valid(invalid_tx) == False, 'Valid transaction?'
    assert chain.transaction_is_valid(invalid_tx2) == False, 'Valid transaction?'
    assert chain.transaction_is_valid(invalid_tx3) == False, 'Valid transaction?'
    assert chain.transaction_is_valid(invalid_tx4) == False, 'Valid transaction?'
    assert chain.transaction_is_valid(t_00) == True, 'Masternode transaction valid?'

    #Check the final state of the chain
    assert len(chain) == 4, 'Proper chain length?'
    assert chain.get_genesis_block().idx == 0, 'get_genesis_block works?'
    assert chain.get_head().idx == 3, 'get_head works?'
    assert chain.get_head_hash() == crypto.HashBlock(chain.get_head()), 'head_hash works?'
    assert chain.was_tampered() == True, 'chain tampered?'
