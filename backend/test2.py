

from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv(".env")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

print("Calling Groq...")
chat = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[{"role": "user", "content": "Hello"}]
)

msg = chat.choices[0].message

# Try attribute access first (most SDKs expose .content)
if hasattr(msg, "content"):
    print("CONTENT (attribute):", msg.content)
elif hasattr(msg, "text"):
    print("CONTENT (text):", msg.text)
elif isinstance(msg, dict):
    print("CONTENT (dict):", msg.get("content") or msg.get("text"))
else:
    print("UNEXPECTED message type:", type(msg))
    print("repr(msg):", repr(msg))
    try:
        print("msg.__dict__:", msg.__dict__)
    except Exception:
        pass
