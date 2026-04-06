import os
import uuid
import bcrypt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from jose import jwt, JWTError
from .db import users

SECRET = os.getenv("SECRET_KEY")
if not SECRET:
    raise RuntimeError("SECRET_KEY environment variable is not set")

ALGO = os.getenv("JWT_ALGORITHM", "HS256")


def create_access_token(data: dict, expires_mins: int = 90):
    data = data.copy()
    data["exp"] = datetime.now(timezone.utc) + timedelta(minutes=expires_mins)
    return jwt.encode(data, SECRET, algorithm=ALGO)


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGO])
        return payload
    except JWTError:
        return None


def signup(name: str, email: str, password: str):
    normalized_email = email.lower().strip()

    if users.find_one({"email": normalized_email}):
        raise HTTPException(status_code=409, detail="Email already registered")

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    user_id = str(uuid.uuid4())
    users.insert_one({
        "user_id": user_id,
        "name": name,
        "email": normalized_email,
        "password_hash": hashed,
        "created_at": datetime.now(timezone.utc)
    })

    token = create_access_token({"user_id": user_id, "email": normalized_email})
    return {"user_id": user_id, "token": token}


def login(email: str, password: str):
    normalized_email = email.lower().strip()

    user = users.find_one({"email": normalized_email})

    if not user or not bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"user_id": user["user_id"], "email": normalized_email})
    return {"token": token, "user_id": user["user_id"]}