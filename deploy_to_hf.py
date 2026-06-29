from huggingface_hub import HfApi
import os
from dotenv import load_dotenv

# Load local .env
load_dotenv('backend/.env')

TOKEN = os.environ.get("HF_TOKEN", "your_token_here")
api = HfApi(token=TOKEN)

user_info = api.whoami()
username = user_info['name']
repo_id = f"{username}/company-chatbot-backend"

print(f"Creating Space: {repo_id}")

try:
    api.create_repo(repo_id=repo_id, repo_type="space", space_sdk="docker", exist_ok=True)
    print("Space created or already exists.")
except Exception as e:
    print(f"Error creating space: {e}")

# Push Secrets
print("Pushing Secrets to Hugging Face...")
for key_name in ["API_SECRET_KEY", "GEMINI_API_KEY_1", "GEMINI_API_KEY_2", "GEMINI_API_KEY_3"]:
    val = os.environ.get(key_name)
    if val:
        try:
            api.add_space_secret(repo_id=repo_id, key=key_name, value=val)
        except Exception as e:
            print(f"Error setting secret {key_name}: {e}")
print("Secrets pushed successfully.")

print("Uploading backend files...")
try:
    # Upload everything in the backend directory except the virtual environment
    api.upload_folder(
        folder_path="backend",
        repo_id=repo_id,
        repo_type="space",
        ignore_patterns=["*.venv*", "*__pycache__*", "*.pyc", ".env", "*.sqlite3", "*.bin"]
    )
    print(f"Upload complete! Space URL: https://huggingface.co/spaces/{repo_id}")
except Exception as e:
    print(f"Error uploading files: {e}")
