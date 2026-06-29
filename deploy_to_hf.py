from huggingface_hub import HfApi
import os

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
