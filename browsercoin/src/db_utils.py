from pymongo import MongoClient
from dotenv import load_dotenv
import os

def connect_db():
    #Connect to DB using connection string from environment
    load_dotenv()
    mongo_connection_str = os.getenv('MONGO_STRING')

    client = MongoClient(mongo_connection_str)
    db = client.chain.blocks
    return db
