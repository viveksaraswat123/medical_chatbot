# Medibot

A medical Q&A chatbot that answers from a retrieval-augmented pipeline instead of a raw LLM prompt. I built it mainly to actually understand RAG — chunking, embeddings, vector search, grounding a generation step — rather than just reading about it.

**Live demo:** https://medical-chatbot-new-978r.onrender.com
*(hosted on Render's free tier, so the first request after idle can take 30-50s to spin up - that's a cold start, not a bug)*

![Chat interface](<Screenshot (345).png>)
![Login](<Screenshot (339).png>)
![Signup](<Screenshot (341).png>)
![Chat history](<Screenshot (342).png>)

---

## Why RAG instead of just calling the LLM

Ask Llama 3.3 directly about a specific condition and it'll answer from whatever it memorized during training — no source, no way to check it, and it'll happily hallucinate details in a confident tone. Medibot instead:

1. Splits a medical knowledge base into chunks
2. Embeds them and stores them in a local FAISS index
3. On a new question, retrieves the top-3 most relevant chunks
4. Feeds those chunks + the question to the LLM as context, and asks it to answer *from that*

It's still not a doctor and still not perfect — retrieval quality caps how good the answer can be, and a bad chunk boundary can cut a fact in half. But answers are at least traceable back to something in the knowledge base instead of being pure recall.

---

## Stack

| Layer | Choice | Why |
|---|---|---|
| Backend | FastAPI | async support, fast to iterate on |
| RAG | LangChain + FAISS | FAISS runs locally, no vector DB hosting cost |
| Embeddings | `BAAI/bge-base-en-v1.5` (HuggingFace) | solid mid-size model, runs fine on CPU |
| LLM | Groq — Llama 3.3 70B | free tier + very fast inference |
| Auth | JWT (python-jose) | stateless, no session store needed |
| DB | MongoDB | users + per-session chat history |
| Frontend | plain HTML/CSS/JS | didn't want a build step for a project this size |
| Hosting | Render | free tier, deploys straight from GitHub |

---

## What it actually does

- Answers questions grounded in a custom medical knowledge base
- Signup/login with JWT-protected routes
- Multiple chat sessions per user, each with full history saved to MongoDB
- Auto-generates a short title for each chat from the first message
- Rate limiting and email validation on the auth endpoints

---

## Project layout

```
medical_chatbot/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI routes
│   │   ├── auth.py            # signup, login, JWT
│   │   ├── chatbot_logic.py   # RAG chain + LLM calls
│   │   ├── chat_storage.py    # Mongo chat CRUD
│   │   ├── vector_store.py    # FAISS index build/load
│   │   └── db.py
│   ├── knowledge_base/        # source .txt files
│   ├── vector_store_db/       # pre-built FAISS index
│   └── requirements.txt
├── frontend/
│   ├── index.html / login_page.html / signup.html / chat.html
│   └── static/auth.js
└── render.yaml
```

---

## Running it locally

```bash
git clone https://github.com/viveksaraswat123/medical_chatbot
cd medical_chatbot
python -m venv myenv && source myenv/bin/activate   # Windows: myenv\Scripts\activate
pip install -r backend/requirements.txt
```

Create `backend/.env`:

```
GROQ_API_KEY=your_groq_api_key
MONGO_URI=your_mongodb_connection_string
SECRET_KEY=any_random_secret_string
LLM_MODEL=llama-3.3-70b-versatile
LOG_LEVEL=INFO
LOG_FILE=logs/medibot.log
```

Build the FAISS index (only needed once, or after changing the knowledge base):

```bash
cd backend && python -m app.vector_store
```

Run the server from the project root:

```bash
PYTHONPATH=. uvicorn backend.app.main:app --reload
```

→ `http://localhost:8000`

---

## Deploying on Render

`render.yaml` at the root has the full config. A couple of things that weren't obvious until they broke the build:

- Pin `pythonVersion` to `3.11.x` — LangChain doesn't play well with newer Python on Render's image
- `vector_store_db/` has to be committed to the repo; Render doesn't build it at deploy time
- Log to `/tmp/` on Render, not `logs/` — the filesystem outside `/tmp` is read-only

---

## Known limitations

- Retrieval is top-k similarity search, no re-ranking — good enough for a demo, not production-grade
- Knowledge base is a small set of curated text files, not a live medical corpus
- Free-tier Render + free-tier Groq means occasional cold starts and rate limits

---

## Disclaimer

Built for learning RAG and backend integration end to end. Not medical advice — see an actual doctor.

---

## Author

**Vivek Saraswat**
Final year B.Tech CSE, ABES Institute of Technology, Noida
Interning at Webmobril Technologies

[LinkedIn](https://www.linkedin.com/in/saraswat-vivek) · [GitHub](https://github.com/viveksaraswat123)
