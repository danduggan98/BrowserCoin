from browsercoin.src import blockchain, crypto, masternode
import rsa

def test_node():
    master = masternode.MasterNode()
    Block = blockchain.Block
    BlockData = blockchain.BlockData

    (testpub, testpriv) = rsa.newkeys(512)
    chain = blockchain.Blockchain()
    
    block1data = BlockData()
    empty_block = Block(block1data)
    assert not chain.block_is_valid(empty_block)

    master.add_coinbase(testpub, block1data)
    new_block = Block(block1data)
    assert chain.block_is_valid(new_block)
    
    chain.add_block(new_block)
    assert chain.get_balance(testpub) == 100
    assert chain.nth_block(1).is_valid()
