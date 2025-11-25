# import os
# from langchain_groq import ChatGroq
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.runnables import RunnablePassthrough
# from langchain_core.output_parsers import StrOutputParser
# from .vector_store import get_retriever

# # In-memory store
# conversation_histories = {}

# def format_docs(docs):
#     return "\n\n".join(doc.page_content for doc in docs)

# def get_chatbot_response(conversation_id: str, user_query: str):
#     """Generates a FREE response using RAG (Groq)."""

#     retriever = get_retriever()

#     model_name = os.getenv("LLM_MODEL", "llama3-70b-8192")

#     llm = ChatGroq(
#         model=model_name,
#         temperature=0.1,
#         groq_api_key=os.getenv("GROQ_API_KEY")
#     )

#     template = """
#     You are a helpful and safe AI medical information assistant named 'MediBot'.
#     Use ONLY the context below.

#     RULES:
#     1. Use ONLY the provided context extracted from medical documents.
#     2. If the context does not contain the answer, say:
#        "I'm sorry, my knowledge base does not contain information on that topic. Please consult a medical professional."
#     3. NEVER provide diagnosis, treatment, or prescriptions.
#     4. Emergency-like symptoms → say:
#        "This sounds serious. Please contact local emergency services immediately."
#     5. End with:
#        "Disclaimer: I am an AI assistant. This information is not a substitute for professional medical advice."
#     6. Non-medical questions → say:
#        "My purpose is to provide medical information. I cannot answer non-medical questions."
#     7. Keep the answer short and simple.

#     CONTEXT:
#     {context}

#     CHAT HISTORY:
#     {chat_history}

#     USER QUESTION:
#     {question}

#     ANSWER:
#     """

#     prompt = ChatPromptTemplate.from_template(template)

#     chat_history = conversation_histories.get(conversation_id, "")

#     rag_chain = (
#         {
#             "context": retriever | format_docs,
#             "question": RunnablePassthrough(),
#             "chat_history": lambda _: chat_history
#         }
#         | prompt
#         | llm
#         | StrOutputParser()
#     )

#     response = rag_chain.invoke(user_query)

#     conversation_histories[conversation_id] = (
#         f"{chat_history}\nUser: {user_query}\nAssistant: {response}"
#     )

#     return response

import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from .vector_store import get_retriever

conversation_histories = {}

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def get_chatbot_response(conversation_id: str, user_query: str):

    retriever = get_retriever()

    llm = ChatGroq(
        model=os.getenv("LLM_MODEL", "openai/gpt-oss-20b"),
        temperature=0.05,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )

    template = """
    You are a professional medical information assistant named MediBot.

    FORMATTING INSTRUCTIONS - MANDATORY:
    • ALWAYS use bullet points (•) for listing information
    • ALWAYS use numbered lists (1. 2. 3.) for step-by-step procedures
    • ALWAYS use headers with bold text (**Header:**) to organize sections
    • ALWAYS keep each point short and clear (one sentence per bullet)
    • ALWAYS format medical terms in bold (**term**)
    • ALWAYS end your main answer content, then add 3 blank lines, then add the disclaimer at the very end
    • NEVER write in paragraph form - use structured bullet points instead

    CONTENT RULES:
    1. Use ONLY the provided context.
    2. If context lacks answer → say:
       "I'm sorry, my knowledge base does not contain that information. Please consult a healthcare professional for accurate guidance."
    3. NO diagnosis, NO prescriptions, NO treatment advice.
    4. Emergencies → say:
       "⚠️ This sounds serious. Please contact emergency services immediately or visit the nearest emergency room."
    5. Non-medical questions → say:
       "I cannot answer non-medical questions. My purpose is to provide medical information only."
    6. Use clear, professional language suitable for medical contexts.

    DISCLAIMER FORMAT:
    After your answer, add exactly 3 blank lines, then add:
    ---
    **Disclaimer:** I am an AI assistant, not a medical professional. This information is for educational purposes only and should not replace consultation with a qualified healthcare provider.

    CONTEXT:
    {context}

    CHAT HISTORY:
    {history}

    USER QUESTION:
    {question}

    ANSWER:
    """

    prompt = ChatPromptTemplate.from_template(template)

    history = conversation_histories.get(conversation_id, "")

    chain = (
        {
            "context": retriever | format_docs,
            "history": lambda _: history,
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    response = chain.invoke(user_query)

    conversation_histories[conversation_id] = (
        f"{history}\nUser: {user_query}\nAssistant: {response}"
    )

    return response
