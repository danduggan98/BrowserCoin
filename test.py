from blockchain import *

#Create a chain for testing
chain = Blockchain()

#Create transactions
t1 = Transaction(5, 'Me', 'You')
t2 = Transaction(100, 'You', 'Me')

#Create and tamper with a block
block1data = BlockData()
block1data.add_transaction(t1)
print(block1data)

#Add the blocks, then tamper with the first
chain.add_block(BlockData())
chain.add_block(block1data)
chain.add_block(BlockData())
chain.nth_block(2).data = BlockData().add_transaction(t2)
print("Block tampered?", chain.nth_block(3).prev_was_tampered())

#Print the final state of each block
print(chain.nth_block(0))
print(chain.nth_block(1))
print(chain.nth_block(2))
print(chain.nth_block(3))
print('\nChain has {} block{}'.format(len(chain), 's' if len(chain) > 1 else ''))

print('Genesis is block #{}'.format(chain.get_genesis_block().idx))
print('Head is block #{}'.format(chain.get_head().idx))
