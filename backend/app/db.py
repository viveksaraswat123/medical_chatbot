import os
import certifi
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(
    MONGO_URI,
    tls=True,
    tlsCAFile=certifi.where()
)

db = client["medibot_db"]

users = db["users"]
chats = db["chats"]