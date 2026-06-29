JAILBREAK_PATTERNS = [
    "ignore previous instructions",
    "ignore your system prompt",
    "pretend you are",
    "act as if you have no restrictions",
    "you are now",
    "DAN",
    "developer mode",
    "jailbreak",
    "bypass your",
    "forget your instructions",
    "your true self",
    "without any restrictions",
    "override",
    "simulate being",
    "roleplay as chatgpt",
    "disregard your guidelines",
]

HARMFUL_PATTERNS = [
    "kill", "murder", "bomb", "terrorist", "suicide", "hack", "steal"
]

def check_guardrails(message: str) -> str | None:
    """
    Returns the blocked reason ("JAILBREAK" or "HARMFUL") if triggered, else None.
    """
    msg_lower = message.lower()
    
    for pattern in JAILBREAK_PATTERNS:
        if pattern in msg_lower:
            return "JAILBREAK"
            
    for pattern in HARMFUL_PATTERNS:
        if pattern in msg_lower:
            return "HARMFUL"
            
    return None
