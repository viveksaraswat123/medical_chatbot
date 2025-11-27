import os
import uvicorn
import logging
from logging.config import dictConfig
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi import Depends
from .auth import signup, login, verify_token
from .chat_storage import start_chat, save_msg, get_chat_history, list_user_chats
from .chatbot_logic import get_chatbot_response, generate_chat_title
from .db import chats

ENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(ENV_PATH)

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FILE = os.getenv("LOG_FILE", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "logs", "medibot.log")))
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

DICT_LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "level": LOG_LEVEL, "formatter": "default"},
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
    "root": {"handlers": ["console", "file"], "level": LOG_LEVEL}
}
dictConfig(DICT_LOG_CONFIG)
logger = logging.getLogger("medibot")

app = FastAPI(title="MediBot API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# FRONTEND / STATIC
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")
FRONTEND_STATIC_DIR = os.path.join(FRONTEND_DIR, "static")
STATIC_SERVE_DIR = FRONTEND_STATIC_DIR if os.path.isdir(FRONTEND_STATIC_DIR) else FRONTEND_DIR
app.mount("/static", StaticFiles(directory=STATIC_SERVE_DIR), name="static")


@app.get("/", include_in_schema=False)
async def read_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "login_page.html"))


@app.get("/login", include_in_schema=False)
async def read_login():
    # file is named login_page.html in repo
    login_path = os.path.join(FRONTEND_DIR, "login_page.html")
    if os.path.exists(login_path):
        return FileResponse(login_path)
    return FileResponse(os.path.join(FRONTEND_DIR, "login_page.html"))


@app.get("/signup", include_in_schema=False)
async def read_signup():
    return FileResponse(os.path.join(FRONTEND_DIR, "signup.html"))


@app.get("/chat", include_in_schema=False)
async def read_chat():
    return FileResponse(os.path.join(FRONTEND_DIR, "chat.html"))

class SignupRequest(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class ChatRequest(BaseModel):
    conversation_id: str
    message: str


def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid Authorization header")
    token = parts[1]
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload


#signup
@app.post("/api/signup")
def register(req: SignupRequest):
    return signup(req.name, req.email, req.password)

#login api
@app.post("/api/login")
def user_login(req: LoginRequest):
    return login(req.email, req.password)

#new_chat api
@app.post("/api/new_chat")
def new_chat(current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("user_id")
    chat_id = start_chat(user_id)
    logger.info("New chat created %s for user %s", chat_id, user_id)
    return {"chat_id": chat_id}


#api for chat
@app.post("/api/chat")
def chat(req: ChatRequest, current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user.get("user_id")
        chat = get_chat_history(req.conversation_id, user_id)

        if not chat.get("title"): 
            title = generate_chat_title(req.message)

            chats.update_one(
                {"chat_id": req.conversation_id},
                {"$set": {"title": title}}
            )
        else:
            title = chat["title"]

        response = get_chatbot_response(req.conversation_id, req.message)
        if isinstance(response, tuple): response = response[0]

        save_msg(req.conversation_id, "user", req.message)
        save_msg(req.conversation_id, "assistant", response)

        return {
            "chat_id": req.conversation_id,
            "title": title,
            "response": response
        }

    except Exception as e:
        logger.exception(f"Chat failure: {e}")
        raise HTTPException(status_code=500, detail="Chat Failure")

@app.get("/api/chat_list")
def get_chat_list(current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("user_id")
    return list_user_chats(user_id)


@app.get("/api/chat_history/{chat_id}")
def api_chat_history(chat_id: str, current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("user_id")
    chat = get_chat_history(chat_id, user_id)
    return chat  # <-- return entire chat, not just messages


@app.delete("/api/delete_chat/{chat_id}")
def delete_chat(chat_id: str, current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("user_id")

    result = chats.delete_one({"chat_id": chat_id, "user_id": user_id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Chat not found")

    return {"status": "success", "message": "Chat deleted successfully"}

@app.get("/api/health")
def health_check():
    return {"status": "ok"}
