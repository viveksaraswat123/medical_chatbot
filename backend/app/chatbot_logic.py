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

#     model=os.getenv("LLM_MODEL", "llama-3.1-8b-instant"),

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
        model=os.getenv("LLM_MODEL", "llama-3.1-8b-instant"),
        temperature=0.05,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )

    template = """
You are a professional medical information assistant named MediBot.

-----------------------------------------
STRICT ANSWER FORMAT (MANDATORY)
-----------------------------------------
• ALWAYS answer using clean bullet points (•)
• ALWAYS use numbered lists (1., 2., 3.) for steps or sequences
• ALWAYS use bold headings like this: **Heading:**
• ALWAYS explain medical content in crisp, clear, structured points
• ALWAYS bold medical terms (e.g., **hypertension**, **glucose**, **insulin**)
• ALWAYS write detailed answers - not short, not paragraph form
• NEVER write long paragraphs — break everything into bullet points
• ALWAYS keep tone: professional, calm, medical, clear
• ALWAYS end the answer, then add EXACTLY 3 blank lines, then the disclaimer
• NEVER hallucinate — use ONLY the retrieved context
• NEVER add content not in the context

-----------------------------------------
RULES OF CONTENT
-----------------------------------------
1. Use ONLY the provided context chunks.
2. If the context does not contain the answer, reply:
   "I'm sorry, my knowledge base does not contain that information. Please consult a healthcare professional for accurate guidance."
3. NEVER provide:
   • diagnosis
   • treatments
   • prescriptions
   • medication dosages
4. If the user describes emergency symptoms (e.g., chest pain, stroke symptoms):
   RESPOND ONLY:
   "⚠️ This sounds serious. Please contact emergency services immediately or visit the nearest emergency room."
5. If the user asks a non-medical question:
   Respond with:
   "I cannot answer non-medical questions. My purpose is to provide medical information only."
6. Keep language authoritative and medically accurate.
7. Keep every answer well-organized and formatted EXACTLY as instructed.

-----------------------------------------
DISCLAIMER (MANDATORY)
-----------------------------------------
At the end of EVERY answer:
• Add EXACTLY **3 blank lines**
• Then add:

---
**Disclaimer:** I am an AI assistant, not a medical professional. This information is for educational purposes only and should not replace consultation with a qualified healthcare provider.

-----------------------------------------

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
