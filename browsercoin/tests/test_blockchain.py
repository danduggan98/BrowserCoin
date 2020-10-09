from src.blockchain import *

def test_blockchain():
    #Create a chain for testing
    chain = Blockchain()

    #Create transactions
    t_00 = Transaction(500, None, 'Me', None, None)
    t_01 = Transaction(500, None, 'You', None, None)
    t1 = Transaction(50, 'Me', 'You', t_00, None)
    t2 = Transaction(300, 'You', 'Me', t_01, None)
    t3 = Transaction(11, 'Me', 'You', t2, None)

    assert t1 == t1, 'Same transactions equal?'
    assert t1 != t2, 'Different transactions equal?'

    #Create and tamper with a block
    block1data = BlockData()
    block1data.add_transaction(t_00)
    block1data.add_transaction(t_01)
    print(block1data)

    block2data = BlockData()
    block2data.add_transaction(t1)
    block2data.add_transaction(t2)
    print(block2data)

    #Add the blocks, then tamper with the first
    print('Different BlockDatas equal?', BlockData() == block1data)
    print('Same BlockDatas equal?', BlockData() == BlockData(), '\n')
    chain.add_block(block1data)
    chain.add_block(block2data)
    chain.add_block(BlockData().add_transaction(t3))
    #chain.nth_block(2).data = BlockData().add_transaction(t2)
    print('Block tampered?', chain.nth_block(3).prev_was_tampered(), '\n')
    print('Different blocks equal?', chain.nth_block(1) == chain.nth_block(2))
    print('Same blocks equal?', chain.nth_block(1) == chain.nth_block(1), '\n')

    #Check the balance of each address
    #print('"ME" has a balance of', chain.get_balance('Me'))
    #print('"You" has a balance of', chain.get_balance('You'))

    #Print the final state of each block
    print(chain.nth_block(0))
    print(chain.nth_block(1))
    print(chain.nth_block(2))
    print(chain.nth_block(3))
    print('\nChain has {} block{}'.format(len(chain), 's' if len(chain) > 1 else ''))

    print('Genesis is block #{}'.format(chain.get_genesis_block().idx))
    print('Head is block #{}'.format(chain.get_head().idx))
    print('Head Hash: {}'.format(chain.get_head_hash()))
    print('Has chain been tampered?', chain.was_tampered())
