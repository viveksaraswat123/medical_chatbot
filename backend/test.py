from app.vector_store import build_vector_store, get_retriever

# Step 1: Build vector store
build_vector_store()

# Step 2: Get retriever
retriever = get_retriever()

# Step 3: Dummy chatbot response function
def get_chatbot_response_offline(user_query):
    # Pass run_manager=None for internal method
    docs = retriever._get_relevant_documents(user_query, run_manager=None)

    context = "\n\n".join([doc.page_content for doc in docs])

    if not context:
        return "I'm sorry, but I have no information on that topic in my knowledge base."

    response = f"Based on the knowledge base, here is some information:\n\n{context[:500]}..."  # first 500 chars
    return response

# Step 4: Test queries
queries = [
    "What are the symptoms of type 2 diabetes?",
    "How to manage high blood pressure?",
    "Signs of a heart attack"
]

for i, q in enumerate(queries, 1):
    print(f"\n--- Query {i}: {q} ---")
    response = get_chatbot_response_offline(q)
    print(response)
