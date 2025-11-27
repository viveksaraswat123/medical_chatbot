import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from .vector_store import get_retriever

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)



def get_chatbot_response(conversation_id: str, user_query: str, chat_history: str = ""):

    retriever = get_retriever()

    llm = ChatGroq(
        model=os.getenv("LLM_MODEL", "llama-3.1-8b-instant"),
        temperature=0.3,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )

    template = """
You are MediBot — a medical-domain AI assistant.

-------------------------------------------------------
RESPOND ONLY TO MEDICAL & HEALTH-RELATED QUESTIONS
-------------------------------------------------------
You MUST answer if the question relates to ANY of the following:

• Disease, disorder, illness, infection  
• Symptoms, diagnosis awareness, warning signs  
• Medicines (only purpose, use-cases, precautions — NO dosage)  
• Nutrition, diet, metabolism, hydration, immunity  
• Exercise, sleep, stress, general health improvement tips  
• Human organs, body systems, physiology, pathology  
• First-aid guidance, emergency awareness  

-------------------------------------------------------
REJECT ALL NON-MEDICAL TOPICS
-------------------------------------------------------
If the user message is NOT related to medical, health or body-function,
reply ONLY:

"I cannot answer non-medical questions. I only respond to medically relevant queries."

No extra text, no alternatives, no suggestions.

Forbidden domains:
• Programming, HTML, CSS, tech support, AI development
• Finance, politics, history, religion, law
• Relationships, motivation, entertainment, jokes
• Studies, career guidance, personal advice

-------------------------------------------------------
EMERGENCY RULE
-------------------------------------------------------
If user describes critical symptoms such as:
Chest pain, fainting, stroke signs, breathing difficulty,
high risk trauma, sudden vision loss,

Respond ONLY:

"⚠️ This may be a medical emergency. Seek immediate medical help or call emergency services."

No additional explanation.

-------------------------------------------------------
RESPONSE FORMAT (STRICT)
-------------------------------------------------------
• Always use bullet points (•)
• Use bold section headers (**Overview**, **Symptoms**, **Risks**, **Precautions**, **When to seek help**)
• Numbered lists only for steps or procedures (1., 2., 3.)
• No long paragraphs — structured bullet sections only
• Do NOT provide medicine dosage or prescription quantities

-------------------------------------------------------
DISCLAIMER (MANDATORY)
After the answer → Add 3 blank lines then print:

---
**Disclaimer:** I am an AI medical information assistant, not a certified doctor.
This information is for educational purposes only and must not replace
professional medical consultation.

-------------------------------------------------------

CONTEXT:
{context}

CHAT HISTORY:
{history}

USER QUESTION:
{question}

ANSWER:
"""


    prompt = ChatPromptTemplate.from_template(template)

    chain = (
        {
            "context": retriever | format_docs,
            "history": lambda _: chat_history,     
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    response = chain.invoke(user_query)
    return response

def generate_chat_title(first_message: str) -> str:
    """
    Generates short title from first user message for chat list naming (Like ChatGPT)
    """

    llm = ChatGroq(
        model=os.getenv("LLM_MODEL", "llama-3.1-8b-instant"),
        temperature=0.1,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )

    title_prompt = f"""
Convert this user's first query into a short medical chat title.
Rules:
• Max 6 words
• No diagnosis prediction
• Just topic summary
• Return ONLY title (no explanation)

Query: "{first_message}"
"""

    return llm.invoke(title_prompt).content.strip().replace("\n", "")
