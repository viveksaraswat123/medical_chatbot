# import os
# from langchain_community.document_loaders import DirectoryLoader
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_openai import OpenAIEmbeddings
# from langchain_community.embeddings import HuggingFaceEmbeddings
# from langchain_community.vectorstores import FAISS

# KNOWLEDGE_BASE_PATH = "knowledge_base"
# VECTOR_STORE_PATH = "vector_store_db"

# def build_vector_store():
#     """Builds and saves a FAISS vector store from documents in the knowledge base."""
#     print("Loading documents from knowledge base...")
#     loader = DirectoryLoader(KNOWLEDGE_BASE_PATH, glob="**/*.txt")
#     documents = loader.load()

#     if not documents:
#         raise ValueError("No documents found in the knowledge base directory.")

#     print(f"Loaded {len(documents)} documents.")

#     text_splitter = RecursiveCharacterTextSplitter(
#         chunk_size=1000,
#         chunk_overlap=100
#     )
#     docs = text_splitter.split_documents(documents)
#     print(f"Split documents into {len(docs)} chunks.")

    
#     embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


#     print("Creating and saving FAISS vector store...")
#     db = FAISS.from_documents(docs, embeddings)

#     # Save vector database locally
#     db.save_local(VECTOR_STORE_PATH)
#     print("Vector store created successfully.")

# def get_retriever():
#     """Loads the FAISS vector store and returns a retriever."""
#     if not os.path.exists(VECTOR_STORE_PATH):
#         build_vector_store()

#     embeddings = OpenAIEmbeddings()

#     db = FAISS.load_local(
#         VECTOR_STORE_PATH,
#         embeddings,
#         allow_dangerous_deserialization=True
#     )

#     # Return retriever (top-3 chunks)
#     return db.as_retriever(search_kwargs={"k": 3})

# if __name__ == "__main__":
#     # Pre-build the vector store when running this file directly
#     build_vector_store()


import os
from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings


KNOWLEDGE_BASE_PATH = "knowledge_base"
VECTOR_STORE_PATH = "vector_store_db"


def build_vector_store():
    print("Loading documents...")
    loader = DirectoryLoader(KNOWLEDGE_BASE_PATH, glob="**/*.txt")
    documents = loader.load()

    if not documents:
        raise ValueError("No documents found.")

    print(f"Loaded {len(documents)} documents.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    docs = splitter.split_documents(documents)
    print(f"Split into {len(docs)} chunks.")

    # FREE embeddings
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


    db = FAISS.from_documents(docs, embeddings)
    db.save_local(VECTOR_STORE_PATH)
    print("Vector DB created.")


def get_retriever():
    if not os.path.exists(VECTOR_STORE_PATH):
        build_vector_store()

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    db = FAISS.load_local(
        VECTOR_STORE_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )
    return db.as_retriever(search_kwargs={"k": 3})


if __name__ == "__main__":
    build_vector_store()
