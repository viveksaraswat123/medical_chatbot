import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from .utils import generate_unique_id
from .chatbot_logic import get_chatbot_response

# ───────────────────────────────────────────────
# Load .env from backend/.env
# ───────────────────────────────────────────────
ENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(ENV_PATH)
print("Loaded .env from:", ENV_PATH)

# ───────────────────────────────────────────────
# Path settings
# ───────────────────────────────────────────────
# __file__ = backend/app/main.py → go two levels up to reach repo root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")

# Check if /frontend/static exists
FRONTEND_STATIC_DIR = os.path.join(FRONTEND_DIR, "static")
if os.path.isdir(FRONTEND_STATIC_DIR):
    STATIC_SERVE_DIR = FRONTEND_STATIC_DIR
else:
    STATIC_SERVE_DIR = FRONTEND_DIR

# ───────────────────────────────────────────────
# FastAPI app
# ───────────────────────────────────────────────
app = FastAPI(
    title="MediBot API",
    description="API for the AI-powered medical information assistant.",
    version="1.0.0"
)

# ───────────────────────────────────────────────
# CORS Middleware
# ───────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ───────────────────────────────────────────────
# Request Model
# ───────────────────────────────────────────────
class ChatRequest(BaseModel):
    conversation_id: str
    message: str

# ───────────────────────────────────────────────
# Static files mounting
# ───────────────────────────────────────────────
app.mount("/static", StaticFiles(directory=STATIC_SERVE_DIR), name="static")

@app.get("/", include_in_schema=False)
async def read_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

# ───────────────────────────────────────────────
# API Endpoints
# ───────────────────────────────────────────────
@app.get("/api/start_conversation", tags=["Conversation"])
def start_conversation():
    conversation_id = generate_unique_id()
    return {"conversation_id": conversation_id}

@app.post("/api/chat", tags=["Conversation"])
def chat(request: ChatRequest):
    try:
        response = get_chatbot_response(request.conversation_id, request.message)
        return {"response": response}
    except Exception as e:
        import traceback
        print("FULL ERROR ↓↓↓")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health", tags=["Health"])
def health_check():
    return {"status": "ok"}

