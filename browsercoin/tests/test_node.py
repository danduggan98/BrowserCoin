from src.node import MasterNode
import src.blockchain as blockchain
import src.crypto as crypto
import rsa

def test_node():
    (testpub, testpriv) = rsa.newkeys(512)
    chain = blockchain.Blockchain()
    master = MasterNode()
    
    data = blockchain.BlockData()
    master.add_coinbase(data, testpub)
    chain.add_block(data)
    assert chain.get_balance(testpub) == 50
    assert chain.nth_block(1).is_valid()
