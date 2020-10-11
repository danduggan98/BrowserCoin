from src.blockchain import *
from src.crypto import *

def test_blockchain():
    #Create identities
    (Me_public, Me_secret) = rsa.newkeys(512)
    (You_public, You_secret) = rsa.newkeys(512)
    (Alice_public, Alice_secret) = rsa.newkeys(512)
    (Bob_public, Bob_secret) = rsa.newkeys(512)

    #Create transactions
    chain = Blockchain()
    t_00 = Transaction(500, None, Me_public, None, None)
    t_01 = Transaction(1500, None, You_public, None, None)
    t_02 = Transaction(200, None, Alice_public, None, None)
    t_03 = Transaction(600, None, Bob_public, None, None)
    t1 = Transaction(50, Me_public, You_public, t_00, t_01)
    t2 = Transaction(300, You_public, Me_public, t1, t1)
    t3 = Transaction(10, Me_public, You_public, t2, t2)
    t4 = Transaction(0, Me_public, You_public, t3, t3)
    t5 = Transaction(50, Alice_public, Bob_public, t_02, t_03)
    t6 = Transaction(300, Bob_public, Alice_public, t5, t5)

    assert t1 == t1, 'Same transactions equal?'
    assert t1 != t2, 'Different transactions equal?'

    #Add three blocks, then tamper with the second
    block1data = BlockData()
    block1data.add_transaction(t_00)
    block1data.add_transaction(t_01)
    block1data.add_transaction(t_02)
    block1data.add_transaction(t_03)

    block2data = BlockData()
    block2data.add_transaction(t1)
    block2data.add_transaction(t2)

    block3data = BlockData()
    block3data.add_transaction(t3)
    block3data.add_transaction(t5)
    block3data.add_transaction(t6)

    assert BlockData() != block1data, 'Different BlockDatas equal?'
    assert BlockData() == BlockData(), 'Same BlockDatas equal?'

    chain.add_block(block1data)
    chain.add_block(block2data)
    chain.add_block(block3data)

    assert chain.nth_block(3).prev_was_tampered() == False, 'Unmodified block not tampered?'
    chain.nth_block(2).data = BlockData().add_transaction(t4) #Tamper with the block
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
    valid_tx = Transaction(10, Bob_public, Alice_public, t5, t5).sign(Bob_secret)
    invalid_tx = Transaction(1000000, Bob_public, Alice_public, t6, t6) #Invalid
    invalid_tx2 = Transaction(10, Bob_public, Alice_public, t5, t5).sign(Alice_secret) #Signed w/ wrong secret
    assert chain.transaction_is_valid(valid_tx) == True, 'Valid transaction?'
    assert chain.transaction_is_valid(invalid_tx) == False, 'Valid transaction?'
    assert chain.transaction_is_valid(invalid_tx2) == False, 'Valid transaction?'

    #Check the final state of the chain
    assert len(chain) == 4, 'Proper chain length?'
    assert chain.get_genesis_block().idx == 0, 'get_genesis_block works?'
    assert chain.get_head().idx == 3, 'get_head works?'
    assert chain.get_head_hash() == HashBlock(chain.get_head()), 'head_hash works?'
    assert chain.was_tampered() == True, 'chain tampered?'
