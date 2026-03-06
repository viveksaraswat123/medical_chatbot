import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables (works locally)
load_dotenv()

# Get Mongo URI from environment
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MONGO_URI not found in environment variables!")

# Connect to MongoDB Atlas
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)

    # Test connection
    client.admin.command("ping")
    print("MongoDB Atlas connection successful!")

except Exception as e:
    print("MongoDB connection failed:", str(e))
    raise

# Access database and collections
db = client["medibot_db"]

users = db["users"]
chats = db["chats"]