from blockchain import *

#Create a chain for testing
chain = Blockchain()

#Create transactions
t1 = Transaction(5, 'Me', 'You')
t2 = Transaction(100, 'You', 'Me')
print('Different transactions equal?', t1 == t2)
print('Same transactions equal?', t1 == t1, '\n')

#Create and tamper with a block
block1data = BlockData()
block1data.add_transaction(t1)
block1data.add_transaction(t2)
print(block1data)

#Add the blocks, then tamper with the first
print('Different BlockDatas equal?', BlockData() == block1data)
print('Same BlockDatas equal?', BlockData() == BlockData(), '\n')
chain.add_block(BlockData())
chain.add_block(block1data)
chain.add_block(BlockData())
chain.nth_block(2).data = BlockData().add_transaction(t2)
print('Block tampered?', chain.nth_block(3).prev_was_tampered(), '\n')
print('Different blocks equal?', chain.nth_block(1) == chain.nth_block(2))
print('Same blocks equal?', chain.nth_block(1) == chain.nth_block(1), '\n')

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
