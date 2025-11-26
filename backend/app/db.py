from pymongo import MongoClient
import os

client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
db = client["medibot_db"]

users = db["users"]
chats = db["chats"]
