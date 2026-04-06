import os
import uvicorn
import logging
from logging.config import dictConfig
from dotenv import load_dotenv

ENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(ENV_PATH)

from fastapi import FastAPI, HTTPException, Header, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, field_validator, EmailStr, Field

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.extension import _rate_limit_exceeded_handler

from .auth import signup, login, verify_token
from .chat_storage import (
    start_chat,
    save_msg,
    get_chat_history,
    list_user_chats,
    set_chat_title
)
from .chatbot_logic import get_chatbot_response, generate_chat_title
from .db import chats, client

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

LOG_FILE = os.getenv(
    "LOG_FILE",
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "logs", "medibot.log")
    )
)

os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

dictConfig({
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": LOG_LEVEL,
            "formatter": "default",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": LOG_LEVEL,
            "formatter": "default",
            "filename": LOG_FILE,
            "maxBytes": 10485760,
            "backupCount": 5,
            "encoding": "utf8",
        },
    },
    "root": {"handlers": ["console", "file"], "level": LOG_LEVEL},
})

logger = logging.getLogger("medibot")

app = FastAPI(title="MediBot API", version="1.0.0")

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "https://medical-chatbot-new-978r.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
static_dir = os.path.join(FRONTEND_DIR, "static")

if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", include_in_schema=False)
async def read_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.get("/login", include_in_schema=False)
async def read_login():
    return FileResponse(os.path.join(FRONTEND_DIR, "login_page.html"))

@app.get("/signup", include_in_schema=False)
async def read_signup():
    return FileResponse(os.path.join(FRONTEND_DIR, "signup.html"))

@app.get("/chat", include_in_schema=False)
async def read_chat():
    return FileResponse(os.path.join(FRONTEND_DIR, "chat.html"))

BLOCKED_PATTERNS = [
    "i want to kill myself",
    "i want to end my life",
    "i am going to kill myself",
    "how to commit suicide",
    "how to hurt myself",
    "how to cut myself",
]

def is_safe_message(message: str) -> bool:
    msg = message.lower()
    for pattern in BLOCKED_PATTERNS:
        if pattern in msg:
            return False
    return True


class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Name cannot be empty")
        if len(v) > 100:
            raise ValueError("Name too long")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ChatRequest(BaseModel):
    conversation_id: str
    message: str

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Message cannot be empty")
        if len(v) > 2000:
            raise ValueError("Message too long")
        return v


def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Unauthorized")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Unauthorized")
    payload = verify_token(parts[1])
    if not payload:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return payload


@app.post("/api/signup")
@limiter.limit("5/minute")
def register(request: Request, req: SignupRequest):
    logger.info("Signup attempt email=%s", req.email)
    return signup(req.name, req.email, req.password)


@app.post("/api/login")
@limiter.limit("5/minute")
def user_login(request: Request, req: LoginRequest):
    logger.info("Login attempt email=%s", req.email)
    return login(req.email, req.password)


@app.post("/api/new_chat")
def new_chat(current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    chat_id = start_chat(user_id)
    logger.info("New chat created chat_id=%s user_id=%s", chat_id, user_id)
    return {"chat_id": chat_id}


@app.post("/api/chat")
@limiter.limit("10/minute")
def chat(request: Request, req: ChatRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]

    if not is_safe_message(req.message):
        return {"response": "Please consult a medical professional or a mental health helpline for serious concerns."}

    chat_doc = get_chat_history(req.conversation_id, user_id)

    if not chat_doc:
        raise HTTPException(status_code=404, detail="Chat not found")

    if not chat_doc.get("title"):
        title = generate_chat_title(req.message)
        set_chat_title(req.conversation_id, title)
    else:
        title = chat_doc["title"]

    history = chat_doc.get("messages", [])[-10:]
    formatted_history = "\n".join(
        f"{m['role']}: {m['content']}" for m in history
    )

    save_msg(req.conversation_id, "user", req.message)

    try:
        response = get_chatbot_response(
            req.conversation_id,
            req.message,
            formatted_history
        )
        if not isinstance(response, str):
            response = str(response)
    except Exception:
        logger.exception("LLM call failed conversation_id=%s", req.conversation_id)
        raise HTTPException(status_code=500, detail="Failed to generate response")

    save_msg(req.conversation_id, "assistant", response)

    logger.info(
        "Chat response sent conversation_id=%s user_id=%s",
        req.conversation_id,
        user_id
    )

    return {
        "chat_id": req.conversation_id,
        "title": title,
        "response": response
    }


@app.get("/api/chat_list")
def get_chat_list(current_user: dict = Depends(get_current_user)):
    return list_user_chats(current_user["user_id"])


@app.get("/api/chat_history/{chat_id}")
def api_chat_history(chat_id: str, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    chat_doc = get_chat_history(chat_id, user_id)
    if not chat_doc:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat_doc


@app.delete("/api/delete_chat/{chat_id}")
def delete_chat(chat_id: str, current_user: dict = Depends(get_current_user)):
    result = chats.delete_one({
        "chat_id": chat_id,
        "user_id": current_user["user_id"]
    })
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Chat not found")
    return {"status": "success", "message": "Chat deleted successfully"}


@app.get("/api/health")
def health_check():
    try:
        client.admin.command("ping")
        return {"status": "ok", "db": "connected"}
    except Exception:
        logger.exception("Database health check failed")
        raise HTTPException(status_code=503, detail="Database unavailable")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)