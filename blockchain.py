import datetime
import hashlib

class Blockchain():
    def __init__(self):
        self.head = Block()
        self.chain = []

class Block():
    def __init__(self):
        self.prev_block = None
        self.prev_hash  = None
        self.time_stamp = None
        self.data = BlockData()

class BlockData():
    def __init__(self):
        self.data = None

print('Success!')
