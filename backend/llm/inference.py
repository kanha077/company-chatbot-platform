from huggingface_hub import InferenceClient
from config import HF_TOKEN, HF_MODEL_ID
import json

# Initialize the HF Inference Client
client = InferenceClient(model=HF_MODEL_ID, token=HF_TOKEN)

def generate_response(messages: list[dict]) -> str:
    """
    Sends the formatted chat history (including system prompt) to the model.
    """
    try:
        # Assuming model supports Chat Completion API via huggingface_hub
        response = client.chat_completion(
            messages=messages,
            max_tokens=500,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"LLM Error: {e}")
        return "Our assistant is temporarily unavailable. Please try again later."
