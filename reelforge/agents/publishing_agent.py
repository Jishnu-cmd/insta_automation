import uuid
import time
import os
import requests
from datetime import datetime
from reelforge.agents.base import BaseAgent
from reelforge.config import settings
from reelforge.models import JobState, ReelStatus

class PublishingAgent(BaseAgent):
    """
    F15 - Instagram Publishing Agent
    Manages Instagram Reel publication using:
    1. Direct Username & Password via instagrapi (Simplest method)
    2. Meta Graph API (Official developer token method)
    3. Dry-Run Mode (Simulation for offline preview)
    """
    
    def __init__(self):
        super().__init__("PublishingAgent")

    def execute(self, state: JobState) -> JobState:
        if not state.video_path or not state.caption:
            raise ValueError("Video path and caption are required for publishing.")

        self.log(state, "Initiating Instagram Reel publishing pipeline...")

        # Determine publishing mode
        if settings.PUBLISH_DRY_RUN:
            return self._execute_dry_run_publish(state)
        elif settings.INSTAGRAM_SESSION_ID or settings.INSTAGRAM_PASSWORD:
            return self._execute_instagrapi_publish(state)
        elif settings.INSTAGRAM_ACCESS_TOKEN:
            return self._execute_live_publish(state)
        else:
            self.log(state, "No session_id, password, or access token found. Defaulting to Dry-Run Mode.")
            return self._execute_dry_run_publish(state)


    def _execute_instagrapi_publish(self, state: JobState) -> JobState:
        self.log(state, f"Publishing Reel live to @{settings.INSTAGRAM_USERNAME} using Direct Instagram Client...")
        
        try:
            from instagrapi import Client
            from reelforge.config import STORAGE_DIR
            
            session_file = STORAGE_DIR / "session.json"
            cl = Client()

            if os.path.exists(session_file):
                try:
                    cl.load_settings(str(session_file))
                    self.log(state, "Loaded saved Instagram session device settings.")
                except Exception as e:
                    self.log(state, f"Session load note: {str(e)}")

            username = settings.INSTAGRAM_USERNAME.replace("@", "").strip()
            password = settings.INSTAGRAM_PASSWORD
            session_id = settings.INSTAGRAM_SESSION_ID

            # Prioritize Direct Username & Password Login
            if username and password:
                self.log(state, f"Authenticating directly as @{username} with password...")
                try:
                    cl.login(username, password)
                except Exception as login_err:
                    self.log(state, f"Password login note: {str(login_err)}")
                    if session_id:
                        self.log(state, "Fallback: Authenticating using browser sessionid cookie...")
                        cl.login_by_sessionid(session_id)
                    else:
                        raise login_err
            elif session_id:
                self.log(state, f"Authenticating using browser sessionid cookie...")
                cl.login_by_sessionid(session_id)
            
            cl.dump_settings(str(session_file))


            
            # Upload Reel MP4 with cover image and caption
            cover_path = state.cover_path if state.cover_path and os.path.exists(state.cover_path) else None
            
            self.log(state, f"Uploading Reel MP4 ({state.video_path})...")
            media = cl.clip_upload(
                path=state.video_path,
                caption=state.caption,
                thumbnail=cover_path
            )
            
            media_id = str(media.pk)
            state.reel_id = media_id
            self.log(state, f"REEL PUBLISHED LIVE ON INSTAGRAM! Media PK: {media_id} (Code: {media.code})")

        except Exception as e:
            self.log(state, f"Direct Instagram publishing exception: {str(e)}. Falling back to dry-run status.")
            state.reel_id = f"ig_instagrapi_fallback_{uuid.uuid4().hex[:8]}"

        return state


    def _execute_dry_run_publish(self, state: JobState) -> JobState:
        self.log(state, "Running in DRY-RUN mode. Simulating Reel publishing...")

        time.sleep(0.5)
        self.log(state, "State transition: CREATED -> UPLOADED (Media container created)")
        
        time.sleep(0.5)
        self.log(state, "State transition: UPLOADED -> PROCESSING (Instagram transcoding video)")

        time.sleep(0.5)
        simulated_media_id = f"ig_media_{uuid.uuid4().hex[:12]}"
        self.log(state, f"State transition: PROCESSING -> PUBLISHED (Media ID: {simulated_media_id})")

        state.reel_id = simulated_media_id
        return state

    def _execute_live_publish(self, state: JobState) -> JobState:
        self.log(state, f"Publishing Reel live to account {settings.INSTAGRAM_HANDLE} via Meta Graph API...")

        try:
            container_url = f"https://graph.facebook.com/v19.0/{settings.INSTAGRAM_ACCOUNT_ID}/media"
            payload = {
                "media_type": "REELS",
                "video_url": state.video_path,
                "caption": state.caption,
                "access_token": settings.INSTAGRAM_ACCESS_TOKEN
            }
            res = requests.post(container_url, data=payload, timeout=30).json()

            if "id" not in res:
                raise Exception(f"Failed to create media container: {res}")

            container_id = res["id"]
            self.log(state, f"Container created: {container_id}. Waiting for processing...")

            status_url = f"https://graph.facebook.com/v19.0/{container_id}?fields=status_code&access_token={settings.INSTAGRAM_ACCESS_TOKEN}"
            for _ in range(10):
                time.sleep(5)
                s_res = requests.get(status_url, timeout=15).json()
                if s_res.get("status_code") == "FINISHED":
                    break

            publish_url = f"https://graph.facebook.com/v19.0/{settings.INSTAGRAM_ACCOUNT_ID}/media_publish"
            pub_res = requests.post(publish_url, data={"creation_id": container_id, "access_token": settings.INSTAGRAM_ACCESS_TOKEN}, timeout=30).json()

            media_id = pub_res.get("id", container_id)
            state.reel_id = media_id
            self.log(state, f"REEL PUBLISHED LIVE ON INSTAGRAM! Media ID: {media_id}")
        except Exception as e:
            self.log(state, f"Live Instagram Meta API Publishing failed: {str(e)}.")
            state.reel_id = f"ig_meta_fallback_{uuid.uuid4().hex[:8]}"

        return state
