from huggingface_hub import InferenceClient
from config import HF_TOKEN, HF_MODEL_ID
import json
import threading

# Primary fast API Client
client = InferenceClient(model=HF_MODEL_ID, token=HF_TOKEN)

# Fallback Local Pipeline Setup
local_pipeline = None
pipeline_lock = threading.Lock()
FALLBACK_MODEL_ID = "Qwen/Qwen2.5-1.5B-Instruct"

def get_local_pipeline():
    global local_pipeline
    with pipeline_lock:
        if local_pipeline is None:
            print(f"Loading local fallback model ({FALLBACK_MODEL_ID})...")
            from transformers import pipeline
            # Load the smaller 1.5B model for CPU inference
            local_pipeline = pipeline("text-generation", model=FALLBACK_MODEL_ID, device="cpu")
            print("Local fallback model loaded successfully.")
    return local_pipeline

def generate_response(messages: list[dict]) -> str:
    """
    Sends the formatted chat history (including system prompt) to the model.
    Falls back to a local 1.5B model if the primary API fails.
    """
    try:
        # Try primary API first
        response = client.chat_completion(
            messages=messages,
            max_tokens=500,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as api_error:
        print(f"Primary API Error: {api_error}. Triggering local fallback...")
        
        try:
            # Trigger fallback
            pipe = get_local_pipeline()
            
            # Format messages for the pipeline
            prompt = pipe.tokenizer.apply_chat_template(
                messages, 
                tokenize=False, 
                add_generation_prompt=True
            )
            
            outputs = pipe(
                prompt, 
                max_new_tokens=500, 
                temperature=0.3,
                do_sample=True,
                return_full_text=False
            )
            return outputs[0]["generated_text"].strip()
            
        except Exception as local_error:
            print(f"Local Fallback Error: {local_error}")
            return "Our assistant is temporarily unavailable. Please try again later."
