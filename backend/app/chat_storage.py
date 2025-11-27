import uuid
from datetime import datetime
from fastapi import HTTPException
from .db import chats    # MongoDB collection

# CREATE NEW CHAT
def start_chat(user_id):
    chat_id = str(uuid.uuid4())

    chats.insert_one({
        "chat_id": chat_id,
        "user_id": user_id,

        "title": None,

        "messages": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })

    return chat_id

def save_msg(chat_id, role, content):
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
        raise HTTPException(404, "Chat not found")


# GET FULL CHAT HISTORY
def get_chat_history(chat_id, user_id):
    chat = chats.find_one({"chat_id": chat_id, "user_id": user_id})
    if not chat:
        raise HTTPException(404, "Chat not found")
    
    messages = []
    for m in chat.get("messages", []):
        role = m.get("role") or m.get("sender") or "user"
        content = m.get("content") or m.get("text") or ""
        messages.append({
            "role": role,
            "content": content,
            "timestamp": m.get("timestamp")
        })

    return {
        "chat_id": chat["chat_id"],
        "title": chat.get("title", None),    
        "messages": messages,
        "created_at": chat["created_at"],
        "updated_at": chat["updated_at"]
    }






# LIST ALL USER CHATS
def list_user_chats(user_id):
    result = list(chats.find({"user_id": user_id}))
    for c in result:
        c["_id"] = str(c["_id"])
        c["chat_id"] = str(c["chat_id"])
        c["title"] = c.get("title")     
        if "messages" not in c:
            c["messages"] = []
    return result

#delete chat
def delete_chat(chat_id, user_id):
    deleted = chats.delete_one({"chat_id": chat_id, "user_id": user_id})

    if deleted.deleted_count == 0:
        raise HTTPException(404, "Chat not found")

    return {"deleted": True}
