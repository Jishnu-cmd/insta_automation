import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Text, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from reelforge.config import settings

Base = declarative_base()

class TopicDB(Base):
    __tablename__ = "topics"
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    category = Column(String, default="AI & Coding")
    summary = Column(Text)
    overall_score = Column(Float, default=0.0)
    format = Column(String)
    status = Column(String, default="NEW")
    created_at = Column(DateTime, default=datetime.utcnow)

class ScriptDB(Base):
    __tablename__ = "scripts"
    id = Column(String, primary_key=True)
    topic_id = Column(String)
    hook = Column(Text)
    body = Column(Text)
    cta = Column(Text)
    full_text = Column(Text)
    format = Column(String)
    quality_score = Column(Float, default=90.0)
    created_at = Column(DateTime, default=datetime.utcnow)

class ReelDB(Base):
    __tablename__ = "reels"
    id = Column(String, primary_key=True)
    job_id = Column(String)
    topic_title = Column(String)
    video_path = Column(String)
    cover_path = Column(String)
    caption = Column(Text)
    status = Column(String, default="CREATED")
    qa_score = Column(Float, default=0.0)
    instagram_media_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)

class AnalyticsDB(Base):
    __tablename__ = "analytics"
    id = Column(String, primary_key=True)
    reel_id = Column(String)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    saves = Column(Integer, default=0)
    collected_at = Column(DateTime, default=datetime.utcnow)

class JobDB(Base):
    __tablename__ = "jobs"
    id = Column(String, primary_key=True)
    status = Column(String)
    progress = Column(Integer, default=0)
    topic_title = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    state_json = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

engine = create_engine(f"sqlite:///{settings.DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
