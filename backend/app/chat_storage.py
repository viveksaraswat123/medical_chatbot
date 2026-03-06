import uuid
from datetime import datetime
from fastapi import HTTPException
from .db import chats  

#function to create new chat
def start_chat(user_id: str) -> str:
    chat_id = str(uuid.uuid4())
    now = datetime.utcnow()
    chats.insert_one({
        "chat_id": chat_id,
        "user_id": user_id,
        "title": None,
        "messages": [],
        "created_at": now,
        "updated_at": now
    })
    return chat_id


#function to Save message to chat 
def save_msg(chat_id: str, role: str, content: str):
    msg = {
        "role": role,
        "content": content,
        "timestamp": datetime.utcnow()
    }

    result = chats.update_one(
        {"chat_id": chat_id},
        {
            "$push": {"messages": msg},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Chat not found")


# func to Get chat history
def get_chat_history(chat_id: str, user_id: str):
    chat = chats.find_one({"chat_id": chat_id, "user_id": user_id})
    if not chat:
        return None  # return None for access control in main.py

    messages = []
    for m in chat.get("messages", []):
        messages.append({
            "role": m.get("role", "user"),
            "content": m.get("content", ""),
            "timestamp": m.get("timestamp").isoformat() if m.get("timestamp") else None
        })

    return {
        "chat_id": chat["chat_id"],
        "title": chat.get("title"),
        "messages": messages,
        "created_at": chat["created_at"].isoformat(),
        "updated_at": chat["updated_at"].isoformat()
    }


#function to list all chats for a user 
def list_user_chats(user_id: str):
    chats_list = list(chats.find({"user_id": user_id}))
    for c in chats_list:
        c["_id"] = str(c["_id"])
        c["chat_id"] = str(c["chat_id"])
        c["title"] = c.get("title")
        if "messages" not in c:
            c["messages"] = []
    return chats_list


#function to delete a chat
def delete_chat(chat_id: str, user_id: str):
    deleted = chats.delete_one({"chat_id": chat_id, "user_id": user_id})
    if deleted.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Chat not found")
    return {"deleted": True}

def set_chat_title(chat_id: str, title: str):
    result = chats.update_one(
        {"chat_id": chat_id},
        {"$set": {"title": title, "updated_at": datetime.utcnow()}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Chat not found")