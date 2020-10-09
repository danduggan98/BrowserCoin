from src.blockchain import *
from src.crypto import *

def test_blockchain():
    #Create transactions
    chain = Blockchain()
    t_00 = Transaction(500, None, 'Me', None, None, None)
    t_01 = Transaction(1500, None, 'You', None, None, None)
    t_02 = Transaction(200, None, 'Alice', None, None, None)
    t_03 = Transaction(600, None, 'Bob', None, None, None)
    t1 = Transaction(50, 'Me', 'You', t_00, t_01, None)
    t2 = Transaction(300, 'You', 'Me', t1, t1, None)
    t3 = Transaction(10, 'Me', 'You', t2, t2, None)
    t4 = Transaction(0, 'Me', 'You', t3, t3, None)
    t5 = Transaction(50, 'Alice', 'Bob', t_02, t_03, None)
    t6 = Transaction(300, 'Bob', 'Alice', t5, t5, None)

    assert t1 == t1, 'Same transactions equal?'
    assert t1 != t2, 'Different transactions equal?'

    #Create and tamper with a block
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

    #Add three blocks, then tamper with the second
    assert BlockData() != block1data, 'Different BlockDatas equal?'
    assert BlockData() == BlockData(), 'Same BlockDatas equal?'

    chain.add_block(block1data)
    chain.add_block(block2data)
    chain.add_block(block3data)

    assert chain.nth_block(3).prev_was_tampered() == False, 'Unmodified block not tampered?'
    chain.nth_block(2).data = BlockData().add_transaction(t4)
    assert chain.nth_block(3).prev_was_tampered() == True, 'Modified block tampered?'

    assert chain.nth_block(1) != chain.nth_block(2), 'Different blocks equal?'
    assert chain.nth_block(1) == chain.nth_block(1), 'Same blocks equal?'

    #Check the balance of each address
    assert chain.get_balance('Me') == 740, 'get_balance works?'
    assert chain.get_balance('You') == 1260, 'get_balance works?'
    assert chain.get_balance('Alice') == 450, 'get_balance works?'
    assert chain.get_balance('Bob') == 350, 'get_balance works?'
    assert chain.get_balance('Somebody else') == None, 'get_balance works?'
    assert chain.latest_address_activity('Me') == chain.latest_address_activity('You')
    assert chain.latest_address_activity('Alice') is t6
    assert chain.latest_address_activity('Bob') is t6

    #Check new transactions for validity
    valid_tx = Transaction(10, 'Bob', 'Alice', t5, t5, None)
    invalid_tx = Transaction(1000000, 'Bob', 'Alice', t6, t6, None) #Invalid
    assert chain.transaction_is_valid(valid_tx) == True, 'Valid transaction?'
    assert chain.transaction_is_valid(invalid_tx) == False, 'Valid transaction?'

    #Check the final state of the chain
    assert len(chain) == 4, 'Proper chain length?'
    assert chain.get_genesis_block().idx == 0, 'get_genesis_block works?'
    assert chain.get_head().idx == 3, 'get_head works?'
    assert chain.get_head_hash() == HashBlock(chain.get_head()), 'head_hash works?'
    assert chain.was_tampered() == True, 'chain tampered?'
