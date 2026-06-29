import os
from dotenv import load_dotenv

load_dotenv()

# HF Space Settings
HF_TOKEN = os.getenv("HF_TOKEN")
HF_MODEL_ID = os.getenv("HF_MODEL_ID", "Qwen/Qwen2.5-3B-Instruct")
HF_SPACE_URL = os.getenv("HF_SPACE_URL")

# Gemini Settings
GEMINI_API_KEY_1 = os.getenv("GEMINI_API_KEY_1")
GEMINI_API_KEY_2 = os.getenv("GEMINI_API_KEY_2")
GEMINI_API_KEY_3 = os.getenv("GEMINI_API_KEY_3")
GEMINI_MODEL_ID = os.getenv("GEMINI_MODEL_ID", "gemini-2.5-flash")

# Auth
API_SECRET_KEY = os.getenv("API_SECRET_KEY", "your-secret-key-here")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "your-admin-password")

# Vector Store
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")

# Company Bot Identity Defaults
COMPANY_NAME_DEFAULT = os.getenv("COMPANY_NAME", "Your Company Name")
BOT_NAME_DEFAULT = os.getenv("BOT_NAME", "Aria")
SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL", "support@yourcompany.com")
SUPPORT_URL = os.getenv("SUPPORT_URL", "https://yourcompany.com/support")

import json
DYNAMIC_CONFIG_PATH = os.getenv("DYNAMIC_CONFIG_PATH", "./dynamic_config.json")

def get_dynamic_config():
    if os.path.exists(DYNAMIC_CONFIG_PATH):
        try:
            with open(DYNAMIC_CONFIG_PATH, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_dynamic_config(company_name: str, bot_name: str):
    config = {
        "COMPANY_NAME": company_name,
        "BOT_NAME": bot_name
    }
    with open(DYNAMIC_CONFIG_PATH, "w") as f:
        json.dump(config, f)

def get_company_name():
    return get_dynamic_config().get("COMPANY_NAME", COMPANY_NAME_DEFAULT)

def get_bot_name():
    return get_dynamic_config().get("BOT_NAME", BOT_NAME_DEFAULT)

# Limits
MAX_MESSAGE_LENGTH = int(os.getenv("MAX_MESSAGE_LENGTH", 1000))
MAX_PDF_SIZE_MB = int(os.getenv("MAX_PDF_SIZE_MB", 10))
SESSION_TTL_MINUTES = int(os.getenv("SESSION_TTL_MINUTES", 30))
RATE_LIMIT_PER_MINUTE = os.getenv("RATE_LIMIT_PER_MINUTE", "20/minute")
RELEVANCE_THRESHOLD = float(os.getenv("RELEVANCE_THRESHOLD", 0.35))
