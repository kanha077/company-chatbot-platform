import threading
import requests
import time
import os

def keep_alive_ping():
    space_url = os.getenv("HF_SPACE_URL")
    if not space_url:
        print("[KeepAlive] HF_SPACE_URL not set, skipping keep-alive ping.")
        return

    health_url = f"{space_url.rstrip('/')}/health"
    while True:
        try:
            r = requests.get(health_url, timeout=10)
            print(f"[KeepAlive] Ping: {r.status_code}")
        except Exception as e:
            print(f"[KeepAlive] Failed: {e}")
        time.sleep(480)  # Ping every 8 minutes

def start_keepalive():
    thread = threading.Thread(target=keep_alive_ping, daemon=True)
    thread.start()
