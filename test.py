from blockchain import *

#Create a chain for testing
chain = Blockchain()

block1 = BlockData()
block1.add_transaction(Transaction())
block1.add_transaction(Transaction())
print(block1)
chain.add_block(block1)
chain.add_block(BlockData())

print(chain.nth_block(0))
print(chain.nth_block(1))
print(chain.nth_block(2))
print('Chain has {} block{}'.format(len(chain), 's' if len(chain) > 1 else ''))
