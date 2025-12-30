import pymongo
import certifi
import os
from dotenv import load_dotenv

load_dotenv()

uri = os.getenv("MONGO_URI")
print(f"Connecting to: {uri}")

try:
    client = pymongo.MongoClient(uri, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=5000)
    print("Attempting to list databases...")
    print(client.list_database_names())
    print("Successfully connected to MongoDB!")
except Exception as e:
    print(f"Failed to connect: {e}")
