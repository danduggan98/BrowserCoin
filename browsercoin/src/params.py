MAX_BLOCK_SIZE = 49 #Max of 50 transactions per block, including the coinbase
BLOCK_REWARD = 100 #Lottery winner gets 100 BrowserCoins
MAX_COINS = 42000000 #All the coins there will ever be - 42 million
BLOCK_SPACING = 5 * 60 #5 minutes between blocks

#Public key used as sender for all coinbase transactions
import rsa
MASTERNODE_PK = rsa.PublicKey(
    11513732540767447483113846044949414508250476572103904091204725969474987927023222988757177509658862669795147117094430349552679859291864922660132748483441101,
    65537
)
