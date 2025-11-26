import os
from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

KNOWLEDGE_BASE_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "knowledge_base"))
VECTOR_STORE_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "vector_store_db"))

def build_vector_store():
    print("Loading documents...")
    loader = DirectoryLoader(KNOWLEDGE_BASE_PATH, glob="**/*.txt")
    documents = loader.load()

    if not documents:
        raise ValueError(f"No documents found in: {KNOWLEDGE_BASE_PATH}")

    print(f"Loaded {len(documents)} documents.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    docs = splitter.split_documents(documents)
    print(f"Split documents into {len(docs)} chunks.")

    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-base-en-v1.5",
        encode_kwargs={"normalize_embeddings": True}
    )

    print("Creating and saving FAISS vector store...")
    db = FAISS.from_documents(docs, embeddings)
    db.save_local(VECTOR_STORE_PATH)
    print("Vector store created successfully.")

def get_retriever():
    if not os.path.exists(VECTOR_STORE_PATH):
        build_vector_store()

    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-base-en-v1.5",
        encode_kwargs={"normalize_embeddings": True}
    )

    db = FAISS.load_local(
        VECTOR_STORE_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )

    return db.as_retriever(search_kwargs={"k": 3})

if __name__ == "__main__":
    build_vector_store()
