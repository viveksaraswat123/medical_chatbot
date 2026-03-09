# Medibot — AI Medical Assistant

A RAG-based medical chatbot built to explore how retrieval-augmented generation works in practice. You ask a health question, it searches a custom medical knowledge base first, then generates a response — instead of relying purely on what the LLM already knows.

Built with FastAPI, LangChain, FAISS, and Groq.

**Live:** https://medical-chatbot-new-978r.onrender.com

Screenshot: ![alt text](<Screenshot (345).png>) ![alt text](<Screenshot (339).png>) ![alt text](<Screenshot (341).png>) ![alt text](<Screenshot (342).png>)

---

## What it does

- Answers health-related questions using a custom knowledge base (not just generic LLM responses)
- Maintains full chat history per user with multiple conversation sessions
- User authentication with JWT (signup, login, protected routes)
- AI-generated chat titles based on your first message
- Clean frontend — no React, just HTML/CSS/JS

---

## Tech Stack

| Layer | Tech |
|---|---|
| Backend | FastAPI, Python 3.11 |
| Database | MongoDB (users + chat history) |
| Auth | JWT (python-jose) |
| RAG Pipeline | LangChain + FAISS |
| Embeddings | HuggingFace `BAAI/bge-base-en-v1.5` |
| LLM | Groq API — Llama 3.3 70B |
| Deployment | Render |

---

## Project Structure

```
medical_chatbot/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app, routes
│   │   ├── auth.py           # Signup, login, JWT
│   │   ├── chatbot_logic.py  # RAG chain, LLM calls
│   │   ├── chat_storage.py   # MongoDB chat operations
│   │   ├── vector_store.py   # FAISS setup, retriever
│   │   ├── db.py             # MongoDB connection
│   │   └── utils.py
│   ├── knowledge_base/       # .txt files used to build the vector store
│   ├── vector_store_db/      # FAISS index (pre-built)
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── login_page.html
│   ├── signup.html
│   ├── chat.html
│   └── static/
│       └── auth.js
└── render.yaml
```

---

## Running Locally

**1. Clone the repo**
```bash
git clone https://github.com/viveksaraswat123/medical_chatbot
cd medical_chatbot
```

**2. Create a virtual environment**
```bash
python -m venv myenv
source myenv/bin/activate  # Windows: myenv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r backend/requirements.txt
```

**4. Set up environment variables**

Create a `.env` file inside the `backend/` folder:
```
GROQ_API_KEY=your_groq_api_key
MONGO_URI=your_mongodb_connection_string
SECRET_KEY=any_random_secret_string
LLM_MODEL=llama-3.3-70b-versatile
LOG_LEVEL=INFO
LOG_FILE=logs/medibot.log
```

**5. Build the vector store** (only needed once)
```bash
cd backend
python -m app.vector_store
```

**6. Start the server**
```bash
cd ..  # back to project root
PYTHONPATH=. uvicorn backend.app.main:app --reload
```

App runs at `http://localhost:8000`

---

## How the RAG pipeline works

1. Medical text files in `knowledge_base/` are split into chunks
2. Each chunk is converted to a vector using HuggingFace embeddings
3. Vectors are stored in a FAISS index locally
4. When a user asks a question, the top 3 most relevant chunks are retrieved
5. Those chunks + the question are passed to the LLM as context
6. Groq (Llama 3.3 70B) generates the final response

This means the bot answers from actual medical content, not just from what the LLM was trained on.

---

## Deployment (Render)

The `render.yaml` at the root handles the full deployment config. A few things worth noting if you're deploying this yourself:

- Pin Python to `3.11.x` — LangChain breaks on 3.14
- Set `PYTHONPATH=.` in the start command
- Use `/tmp/` for log files on cloud servers
- The `vector_store_db/` folder must be committed to your repo — Render won't build it

---

## Disclaimer

This is a personal project built to learn RAG and AI integration. It is not a substitute for professional medical advice. Always consult a real doctor for anything health-related.

---

## Author

**Vivek Saraswat**
Final year B.Tech CS - ABES Institute of Technology, Noida
Interning at Webmobril Technologies

[LinkedIn](https://www.linkedin.com/in/saraswat-vivek) · [GitHub](https://github.com/viveksaraswat123)