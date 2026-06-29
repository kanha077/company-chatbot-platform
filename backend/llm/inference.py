from config import GEMINI_API_KEY_1, GEMINI_API_KEY_2, GEMINI_API_KEY_3, GEMINI_MODEL_ID
import json
import threading
import google.generativeai as genai

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
            local_pipeline = pipeline("text-generation", model=FALLBACK_MODEL_ID, device="cpu")
            print("Local fallback model loaded successfully.")
    return local_pipeline

def try_gemini(api_key: str, messages: list[dict]) -> str:
    if not api_key:
        raise ValueError("API Key is empty")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(GEMINI_MODEL_ID)
    
    # Convert standard chat history to Gemini format
    gemini_history = []
    sys_prompt = ""
    for msg in messages:
        if msg["role"] == "system":
            sys_prompt += msg["content"] + "\n"
        elif msg["role"] == "user":
            gemini_history.append({"role": "user", "parts": [msg["content"]]})
        elif msg["role"] == "assistant":
            gemini_history.append({"role": "model", "parts": [msg["content"]]})
            
    # If using System prompt, Gemini supports it natively in GenerativeModel(system_instruction=sys_prompt)
    if sys_prompt.strip():
        model = genai.GenerativeModel(model_name=GEMINI_MODEL_ID, system_instruction=sys_prompt)
    else:
        model = genai.GenerativeModel(model_name=GEMINI_MODEL_ID)
    
    # Gemini chat session doesn't easily let us send history like this if we use system_instruction, 
    # instead we can just generate content by formatting it as a single string, or starting a chat.
    # Let's start a chat with history
    chat = model.start_chat(history=gemini_history[:-1])
    last_user_msg = gemini_history[-1]["parts"][0]
    
    response = chat.send_message(last_user_msg, generation_config=genai.types.GenerationConfig(
        max_output_tokens=500,
        temperature=0.3
    ))
    return response.text.strip()

def generate_response(messages: list[dict]) -> str:
    """
    Sends the formatted chat history (including system prompt) to the model.
    Tries 3 Gemini keys, falls back to a local 1.5B model if all fail.
    """
    api_keys = [GEMINI_API_KEY_1, GEMINI_API_KEY_2, GEMINI_API_KEY_3]
    
    for i, key in enumerate(api_keys, 1):
        try:
            print(f"Attempting generation with Gemini Key {i}...")
            return try_gemini(key, messages)
        except Exception as api_error:
            print(f"Gemini Key {i} Failed: {api_error}")
            
    print("All Gemini keys failed! Triggering local fallback...")
    try:
        # Trigger ultimate fallback
        pipe = get_local_pipeline()
        
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
