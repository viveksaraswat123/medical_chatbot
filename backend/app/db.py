import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load .env file
ENV_PATH = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(ENV_PATH)

# Get Mongo URI
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI not found in environment variables!")


# Connect to MongoDB Atlas
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
   
    print("MongoDB Atlas connection successful!")
except Exception as e:
    print("MongoDB connection failed:", e)
    exit(1)

# Access database and collections
db = client["medibot_db"]
users = db["users"]
chats = db["chats"]
