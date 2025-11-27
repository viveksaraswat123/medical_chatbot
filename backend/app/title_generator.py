from .llm_model import generate_response   

def generate_title(text: str):
    prompt = f"""
    Summarize the medical query into a 4-7 word title.
    Do NOT invent diagnosis — only rewrite what user said.
    Respond only with the title text.

    Query: "{text}"
    """
    return generate_response(prompt)
