import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

def init_firebase():
    if not firebase_admin._apps:
        # Load from environment variable (useful for HF Spaces Secrets)
        service_account_str = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
        if service_account_str:
            try:
                cred_dict = json.loads(service_account_str)
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred)
                print("Firebase Admin initialized from env var.")
            except Exception as e:
                print(f"Failed to initialize Firebase Admin from env var: {e}")
        else:
            # Fallback to local file for dev
            local_path = "serviceAccountKey.json"
            if os.path.exists(local_path):
                cred = credentials.Certificate(local_path)
                firebase_admin.initialize_app(cred)
                print("Firebase Admin initialized from local file.")
            else:
                print("WARNING: No Firebase credentials found. Backend will not be able to connect to Firestore.")

init_firebase()
db = firestore.client()
