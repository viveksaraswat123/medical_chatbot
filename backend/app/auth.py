import os
import uuid
import bcrypt
from datetime import datetime, timedelta
from jose import jwt, JWTError
from .db import users

# Load secret from environment (set in backend/.env)
SECRET = os.getenv("SECRET_KEY", "SUPER_SECRET_KEY")
ALGO = os.getenv("JWT_ALGORITHM", "HS256")

def create_access_token(data: dict, expires_mins=60*24*7):  # 7 days valid
    data = data.copy()
    data["exp"] = datetime.utcnow() + timedelta(minutes=expires_mins)
    return jwt.encode(data, SECRET, algorithm=ALGO)


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGO])
        return payload
    except JWTError:
        return None

def signup(name, email, password):
    if users.find_one({"email": email}):
        return {"error": "Email already registered"}

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    user_id = str(uuid.uuid4())
    users.insert_one({
        "user_id": user_id,
        "name": name,
        "email": email,
        "password_hash": hashed,
        "created_at": datetime.utcnow()
    })

    token = create_access_token({"user_id": user_id, "email": email})
    return {"user_id": user_id, "token": token}

def login(email, password):
    user = users.find_one({"email": email})
    if not user: return {"error": "Invalid email or password"}

    if not bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        return {"error": "Invalid password"}

    token = create_access_token({"user_id": user["user_id"], "email": email})
    return {"token": token, "user_id": user["user_id"]}
