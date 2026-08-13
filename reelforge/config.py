import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

STORAGE_DIR = BASE_DIR / "storage"
VIDEOS_DIR = STORAGE_DIR / "videos"
AUDIO_DIR = STORAGE_DIR / "audio"
IMAGES_DIR = STORAGE_DIR / "images"
COVERS_DIR = STORAGE_DIR / "covers"
TEMP_DIR = STORAGE_DIR / "temp"

for d in [STORAGE_DIR, VIDEOS_DIR, AUDIO_DIR, IMAGES_DIR, COVERS_DIR, TEMP_DIR]:
    d.mkdir(parents=True, exist_ok=True)

class Settings(BaseModel):
    # Brand & Niche Configuration
    BRAND_NAME: str = "Flow Tech"
    INSTAGRAM_HANDLE: str = "@flow.tech.0306"
    PRIMARY_NICHE: str = "AI, Technology, Coding & Projects"
    ACTIVE_NICHE: str = os.getenv("ACTIVE_NICHE", "AI, Coding & Tech Projects")

    
    # Execution & API Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    
    # Direct Instagram Credentials (instagrapi & session cookie)
    INSTAGRAM_USERNAME: str = os.getenv("INSTAGRAM_USERNAME", "flow.tech.0306")
    INSTAGRAM_PASSWORD: str = os.getenv("INSTAGRAM_PASSWORD", "")
    INSTAGRAM_SESSION_ID: str = os.getenv("INSTAGRAM_SESSION_ID", "")


    # Meta / Instagram Graph API
    INSTAGRAM_ACCOUNT_ID: str = os.getenv("INSTAGRAM_ACCOUNT_ID", "")
    INSTAGRAM_ACCESS_TOKEN: str = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
    PUBLISH_DRY_RUN: bool = os.getenv("PUBLISH_DRY_RUN", "True").strip().lower() not in ("false", "0", "no", "off")


    
    # Voice TTS Configuration
    TTS_VOICE: str = "en-US-ChristopherNeural"  # High quality Azure TTS voice
    TTS_RATE: str = "+5%"  # Slightly energetic narration rate
    
    # Video Composition Specs (9:16 vertical standard)
    VIDEO_WIDTH: int = 1080
    VIDEO_HEIGHT: int = 1920
    VIDEO_FPS: int = 30
    
    # Quality Control Gate
    QA_SCORE_THRESHOLD: float = 85.0
    
    # Scheduler Configuration
    SCHEDULE_ENABLED: bool = True
    SCHEDULE_INTERVAL_MINUTES: int = 30  # Triggers pipeline every 30 minutes
    REELS_PER_DAY: int = 48
    PREFERRED_PUBLISH_TIME: str = "19:00"

    
    # Database
    DB_PATH: str = str(STORAGE_DIR / "reelforge.db")

settings = Settings()
