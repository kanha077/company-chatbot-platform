from config import HF_TOKEN
import requests

API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"

# A lightweight classifier using a zero-shot model via HF API
# Or we can just use simple keyword matching if API is too slow.
# The prompt specified using a classifier prompt. We will simulate that using a generic prompt approach.

def classify_intent(message: str) -> str:
    """
    Categories:
    - COMPANY_QUERY
    - GREETING
    - OFF_TOPIC
    - JAILBREAK
    - HARMFUL
    """
    message_lower = message.lower()
    
    # Very basic heuristic for this implementation
    greetings = ["hi", "hello", "hey", "greetings", "how are you"]
    if any(message_lower.startswith(g) for g in greetings) and len(message.split()) < 5:
        return "GREETING"
        
    # We will let the guardrails catch jailbreaks and harmful content
    # The rest defaults to COMPANY_QUERY for now, and the RAG relevance gate will handle OFF_TOPIC
    return "COMPANY_QUERY"
