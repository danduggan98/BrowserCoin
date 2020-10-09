from src.blockchain import *
from src.crypto import *

def test_blockchain():
    #Create transactions
    chain = Blockchain()
    t_00 = Transaction(500, None, 'Me', None, None)
    t_01 = Transaction(500, None, 'You', None, None)
    t1 = Transaction(50, 'Me', 'You', t_00, None)
    t2 = Transaction(300, 'You', 'Me', t1, None)
    t3 = Transaction(10, 'Me', 'You', t2, None)
    t4 = Transaction(0, 'Me', 'You', t3, None)

    assert t1 == t1, 'Same transactions equal?'
    assert t1 != t2, 'Different transactions equal?'

    #Create and tamper with a block
    block1data = BlockData()
    block1data.add_transaction(t_00)
    block1data.add_transaction(t_01)

    block2data = BlockData()
    block2data.add_transaction(t1)
    block2data.add_transaction(t2)

    block3data = BlockData()
    block3data.add_transaction(t3)

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
    assert chain.get_balance('You') == 260, 'get_balance works?'
    assert chain.get_balance('Somebody else') == None, 'get_balance works?'

    #Print the final state of each block
    print(chain.nth_block(0))
    print(chain.nth_block(1))
    print(chain.nth_block(2))
    print(chain.nth_block(3))
    
    assert len(chain) == 4, 'Proper chain length?'
    assert chain.get_genesis_block().idx == 0, 'get_genesis_block works?'
    assert chain.get_head().idx == 3, 'get_head works?'
    assert chain.get_head_hash() == HashBlock(chain.get_head()), 'head_hash works?'
    assert chain.was_tampered() == True, 'chain tampered?'
