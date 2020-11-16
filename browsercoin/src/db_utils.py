from pymongo import MongoClient
from dotenv import load_dotenv
import os

#Get the database client
def connect_db():
    load_dotenv()
    mongo_connection_str = os.getenv('MONGO_STRING')
    
    try:
        client = MongoClient(mongo_connection_str, serverSelectionTimeoutMS=3000)
        client.server_info() #This errors out if connection failed
    except:
        raise ConnectionError('Database connection failed')
    return client
