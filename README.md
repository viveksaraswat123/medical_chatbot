# Medibot: RAG-Powered Medical Assistant

A specialized Retrieval-Augmented Generation (RAG) system designed to query medical documentation with high contextual accuracy. By grounding the LLM in a specific vector database of medical PDFs, the system minimizes hallucinations and provides source-backed responses.



## 🛠 Features
* **PDF Ingestion:** Automated text extraction and recursive character splitting for large medical documents.
* **Vector Search:** Semantic search using ChromaDB to retrieve the most relevant document chunks.
* **Grounded Response:** Custom prompt templates that force the LLM to answer *only* based on the retrieved context.
* **Context Preservation:** Implemented chunk overlapping to ensure medical terms and definitions aren't lost during splitting.

## 🏗 System Architecture
The pipeline follows a decoupled logic:
1. **Preprocessing:** Documents are split into 1000-character chunks with a 200-character overlap using `RecursiveCharacterTextSplitter`.
2. **Embedding:** Text chunks are converted into high-dimensional vectors using `sentence-transformers`.
3. **Storage:** Vectors are indexed in a local **ChromaDB** instance for persistence.
4. **Inference:** User queries are vectorized, matched against the DB, and passed to **Gemini/OpenAI** for final synthesis.



## 💻 Tech Stack
* **Orchestration:** LangChain
* **LLM:** Google Gemini API / OpenAI
* **Vector DB:** ChromaDB
* **Languages:** Python 3.10+
* **Libraries:** PyPDF2, Tiktoken, Dotenv

## 🚀 Quick Start

### 1. Setup Environment
```bash
git clone [https://github.com/viveksaraswat123/medibot](https://github.com/viveksaraswat123/medibot)
cd medibot
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
2. Configure Keys
Create a .env file in the root directory:

Plaintext
GOOGLE_API_KEY=your_gemini_key_here
3. Usage
Place your medical PDFs in the /data folder, then run:

Bash
# To index the documents and create the vector store
python ingest.py

# To start the query interface
python app.py
📝 Implementation Notes
Chunking Strategy: Used recursive splitting to preserve the structural integrity of medical tables and lists.

Prompt Engineering: Utilized a system prompt that explicitly instructs the model: "If the answer is not in the context, state that you do not know. Do not use outside knowledge."

⚠️ Disclaimer
This tool is a technical proof-of-concept. It is not a medical device and should not be used for self-diagnosis or as a substitute for professional medical advice.