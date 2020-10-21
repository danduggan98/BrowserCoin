from browsercoin.src import blockchain, crypto
import rsa

def test_node():
    Block = blockchain.Block
    BlockData = blockchain.BlockData

    (masternode_pk, masternode_sk) = crypto.LoadMasterNodeKeys()
    (testpub, testpriv) = rsa.newkeys(512)
    chain = blockchain.Blockchain()
    
    block1data = BlockData()
    prev_coinbase_tx = chain.latest_address_activity(masternode_pk)
    output_prev_tx = chain.latest_address_activity(testpub) #testpub recieves first block reward
    block1data.add_coinbase(testpub, prev_coinbase_tx, output_prev_tx)

    new_block = Block(block1data)
    chain.add_block(new_block)
    assert chain.get_balance(testpub) == 50
    assert chain.nth_block(1).is_valid()
