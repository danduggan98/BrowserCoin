from pymongo import MongoClient
from dotenv import load_dotenv
import os

#Get the database client
def connect_db():
    load_dotenv()
    mongo_connection_str = os.getenv('MONGO_STRING')

    client = MongoClient(mongo_connection_str)
    return client
