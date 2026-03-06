import os
import certifi
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MONGO_URI not found in environment variables!")

try:
    client = MongoClient(
        MONGO_URI,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=5000
    )

    # Test connection
    client.admin.command("ping")
    print("MongoDB Atlas connection successful!")

except Exception as e:
    print("MongoDB connection failed:", e)
    raise

db = client["medibot_db"]

users = db["users"]
chats = db["chats"]