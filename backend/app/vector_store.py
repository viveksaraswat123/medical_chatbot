import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

VECTOR_STORE_PATH = os.getenv(
    "VECTOR_STORE_PATH",
    os.path.abspath(os.path.join(BASE_DIR, "..", "vector_store_db"))
)

_embeddings = None
_retriever = None


def _get_embeddings():
    global _embeddings

    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-en-v1.5",
            cache_folder="./hf_cache",
            encode_kwargs={"normalize_embeddings": True}
        )

    return _embeddings


def get_retriever():
    global _retriever

    if _retriever is None:

        if not os.path.exists(VECTOR_STORE_PATH):
            raise FileNotFoundError(f"Vector store not found at {VECTOR_STORE_PATH}")

        db = FAISS.load_local(
            VECTOR_STORE_PATH,
            _get_embeddings(),
            allow_dangerous_deserialization=True
        )

        _retriever = db.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": 5,
                "fetch_k": 20
            }
        )

    return _retriever