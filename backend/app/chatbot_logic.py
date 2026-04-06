import os
import re
import logging
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from .vector_store import get_retriever

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if not os.getenv("GROQ_API_KEY"):
    raise EnvironmentError(
        "GROQ_API_KEY is not set. Please configure it in your environment variables."
    )

_retriever = None
_llm = None
_chain = None

def _get_retriever():
    global _retriever
    if _retriever is None:
        logger.info("Initialising retriever...")
        _retriever = get_retriever()
    return _retriever


def _get_llm() -> ChatGroq:
    global _llm
    if _llm is None:
        logger.info("Initialising LLM...")
        _llm = ChatGroq(
            model=os.getenv("LLM_MODEL", "llama-3.1-8b-instant"),
            temperature=0.3,
            groq_api_key=os.getenv("GROQ_API_KEY"),
        )
    return _llm


MEDIBOT_TEMPLATE = """
You are MediBot — a medical-domain AI assistant.

#RESPOND ONLY TO MEDICAL & HEALTH-RELATED QUESTIONS

You MUST answer if the question relates to ANY of the following:

• Disease, disorder, illness, infection  
• Symptoms, diagnosis awareness, warning signs  
• Medicines (only purpose, use-cases, precautions — NO dosage)  
• Nutrition, diet, metabolism, hydration, immunity  
• Exercise, sleep, stress, general health improvement tips  
• Human organs, body systems, physiology, pathology  
• First-aid guidance, emergency awareness  


#REJECT ALL NON-MEDICAL TOPICS

If the user message is NOT related to medical, health or body-function,
reply ONLY:

"I cannot answer non-medical questions. I only respond to medically relevant queries."

No extra text, no alternatives, no suggestions.

Forbidden domains:
• Programming, HTML, CSS, tech support, AI development
• Finance, politics, history, religion, law
• Relationships, motivation, entertainment, jokes
• Studies, career guidance, personal advice


#EMERGENCY RULE

If user describes critical symptoms such as:
Chest pain, fainting, stroke signs, breathing difficulty,
high risk trauma, sudden vision loss,

Respond ONLY:

"⚠️ This may be a medical emergency. Seek immediate medical help or call emergency services."

No additional explanation.


#RESPONSE FORMAT (STRICT)
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

_NON_MEDICAL_PATTERN = re.compile(
    r"^\s*(good|hi+|hello|hey|thanks?|thank you|ok(ay)?|cool|nice|great|"
    r"lol|haha|hehe|bye|goodbye|test|yo|sup|wassup|howdy|cheers|"
    r"awesome|wow|bravo|well done|congrats?)\W*$",
    re.IGNORECASE,
)

NON_MEDICAL_REPLY = (
    "I cannot answer non-medical questions. "
    "I only respond to medically relevant queries."
)


def _is_non_medical(text: str) -> bool:
    return bool(_NON_MEDICAL_PATTERN.match(text))


def _format_docs(docs) -> str:
    if not docs:
        return "No relevant context found."
    return "\n\n".join(doc.page_content for doc in docs)


def _sanitise_input(text: str) -> str:
    text = text.strip()
    if len(text) > 2000:
        text = text[:2000]
    return text


def _build_chain(retriever, llm):
    prompt = ChatPromptTemplate.from_template(MEDIBOT_TEMPLATE)
    return (
        {
            "context":  (lambda x: x["question"]) | retriever | _format_docs,
            "history":  lambda x: x["history"],
            "question": lambda x: x["question"],
        }
        | prompt
        | llm
        | StrOutputParser()
    )


def _get_chain():
    global _chain
    if _chain is None:
        logger.info("Building RAG chain...")
        _chain = _build_chain(_get_retriever(), _get_llm())
    return _chain


def get_chatbot_response(
    conversation_id: str,
    user_query: str,
    chat_history: str = "",
) -> str:
    user_query = _sanitise_input(user_query)
    if not user_query:
        return "Please enter a valid question."

    if _is_non_medical(user_query):
        logger.info("conversation_id=%s | non-medical input blocked: %r", conversation_id, user_query)
        return NON_MEDICAL_REPLY

    logger.info("conversation_id=%s | query_length=%d", conversation_id, len(user_query))

    try:
        response = _get_chain().invoke({"question": user_query, "history": chat_history})
        return response
    except Exception:
        logger.exception("LLM chain failed for conversation_id=%s", conversation_id)
        return (
            "I'm sorry, I encountered an error while processing your request. "
            "Please try again later."
        )


def generate_chat_title(first_message: str) -> str:
    first_message = _sanitise_input(first_message)
    if not first_message:
        return "New Medical Chat"

    title_prompt = (
        "Convert this user's first query into a short medical chat title.\n"
        "Rules:\n"
        "• Max 6 words\n"
        "• No diagnosis prediction\n"
        "• Just topic summary\n"
        "• Return ONLY the title (no explanation, no punctuation at the end)\n\n"
        f'Query: "{first_message}"'
    )

    try:
        title = _get_llm().invoke(title_prompt).content.strip().replace("\n", "")
        return title if title else "Medical Query"
    except Exception:
        logger.exception("Title generation failed")
        return "Medical Query"