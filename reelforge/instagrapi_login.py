import os
import json
from pathlib import Path
from instagrapi import Client
from reelforge.config import settings, STORAGE_DIR

SESSION_FILE = STORAGE_DIR / "session.json"

def get_instagram_client():
    cl = Client()
    
    # Load session if exists
    if os.path.exists(SESSION_FILE):
        try:
            cl.load_settings(str(SESSION_FILE))
            print("Loaded existing Instagram session settings.")
        except Exception as e:
            print(f"Session load notice: {e}")

    username = settings.INSTAGRAM_USERNAME.replace("@", "").strip()
    password = settings.INSTAGRAM_PASSWORD

    if not password:
        raise ValueError("INSTAGRAM_PASSWORD is not set in .env")

    print(f"Logging into Instagram as @{username}...")
    
    try:
        cl.login(username, password)
        cl.dump_settings(str(SESSION_FILE))
        print("✅ Login successful! Session settings dumped.")
        return cl
    except Exception as e:
        print(f"Login Exception: {e}")
        # Try relogin with dump
        try:
            cl.login(username, password, relogin=True)
            cl.dump_settings(str(SESSION_FILE))
            return cl
        except Exception as ex:
            raise ex

if __name__ == "__main__":
    get_instagram_client()
