from browsercoin.src import blockchain, crypto, masternode
import rsa

def test_node():
    master = masternode.MasterNode()
    Block = blockchain.Block
    BlockData = blockchain.BlockData

    (testpub, testpriv) = rsa.newkeys(512)
    chain = blockchain.Blockchain()
    
    block1data = BlockData()
    prev_coinbase_tx = chain.latest_address_activity(master.public_key)
    output_prev_tx = chain.latest_address_activity(testpub) #testpub recieves first block reward
    master.add_coinbase(block1data, testpub, prev_coinbase_tx, output_prev_tx)

    new_block = Block(block1data)
    assert chain.block_is_valid(new_block)
    chain.add_block(new_block)
    assert chain.get_balance(testpub) == 100
    assert chain.nth_block(1).is_valid()
