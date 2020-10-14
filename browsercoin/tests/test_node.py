from src.node import *
from src.blockchain import *
from src.crypto import *

def test_node():
    (testpub, testpriv) = rsa.newkeys(512)
    chain = Blockchain()
    master = MasterNode()
    
    data = BlockData()
    master.add_coinbase(data, testpub)
    chain.add_block(data)
    assert chain.get_balance(testpub) == 50
    assert chain.nth_block(1).is_valid()
