from blockchain import *

#Create a chain for testing
chain = Blockchain()

block1 = BlockData()
t1 = Transaction(5, 'Me', 'You')
block1.add_transaction(t1)
print(block1)
chain.add_block(block1)
chain.add_block(BlockData())

print(chain.nth_block(0))
print(chain.nth_block(1))
print(chain.nth_block(2))
print('\nChain has {} block{}'.format(len(chain), 's' if len(chain) > 1 else ''))

print('Head is block #{}'.format(chain.get_head().idx))
