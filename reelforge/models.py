import enum
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

# --- Enums ---

class JobStatus(str, enum.Enum):
    PENDING = "PENDING"
    DISCOVERING = "DISCOVERING"
    RESEARCHING = "RESEARCHING"
    SCRIPTING = "SCRIPTING"
    EXECUTING_CODE = "EXECUTING_CODE"
    GENERATING_VISUALS = "GENERATING_VISUALS"
    GENERATING_VOICE = "GENERATING_VOICE"
    GENERATING_SUBTITLES = "GENERATING_SUBTITLES"
    COMPOSING_VIDEO = "COMPOSING_VIDEO"
    GENERATING_COVER = "GENERATING_COVER"
    GENERATING_CAPTION = "GENERATING_CAPTION"
    QA_CHECKING = "QA_CHECKING"
    PUBLISHING = "PUBLISHING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class ContentFormat(str, enum.Enum):
    PROJECT_DEMO = "PROJECT_DEMO"
    CODING_TUTORIAL = "CODING_TUTORIAL"
    AI_NEWS = "AI_NEWS"
    TOP_LIST = "TOP_LIST"
    BUILD_JOURNEY = "BUILD_JOURNEY"

class ReelStatus(str, enum.Enum):
    CREATED = "CREATED"
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    PUBLISHED = "PUBLISHED"
    FAILED = "FAILED"

# --- Pydantic Data Contracts ---

class Topic(BaseModel):
    id: Optional[str] = None
    title: str
    category: str = "AI & Coding"
    summary: str
    trend_score: float = 8.0
    relevance_score: float = 9.0
    novelty_score: float = 8.5
    audience_score: float = 9.0
    historical_score: float = 0.0
    overall_score: float = 8.6
    format: ContentFormat = ContentFormat.PROJECT_DEMO
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ResearchBrief(BaseModel):
    topic_title: str
    summary: str
    key_points: List[str]
    technical_details: List[str]
    code_ideas: List[str]
    sources: List[str]
    confidence_score: float = 0.95

class ScriptSegment(BaseModel):
    section: str  # HOOK, PROBLEM, EXPLANATION, DEMO, RESULT, CTA
    narration: str
    visual_prompt: str
    duration_seconds: float
    code_snippet: Optional[str] = None

class ScriptStructure(BaseModel):
    topic: str
    format: ContentFormat
    hook: str
    problem: str
    explanation: str
    demo_code: str
    result: str
    cta: str
    full_text: str
    segments: List[ScriptSegment]
    quality_score: float = 90.0

class CodeExecutionResult(BaseModel):
    code: str
    language: str = "python"
    executed: bool = True
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    execution_time_ms: float = 0.0
    output_image_path: Optional[str] = None

class QACheckItem(BaseModel):
    name: str
    passed: bool
    score: float
    details: str

class QAReport(BaseModel):
    passed: bool
    overall_score: float
    checks: List[QACheckItem]
    secret_scan_clean: bool = True
    recommendations: List[str] = []

class ReelMetadata(BaseModel):
    id: str
    job_id: str
    topic_title: str
    format: ContentFormat
    video_path: str
    cover_path: str
    caption: str
    hashtags: List[str]
    status: ReelStatus = ReelStatus.CREATED
    qa_score: float = 0.0
    instagram_media_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = None

class JobState(BaseModel):
    job_id: str
    status: JobStatus = JobStatus.PENDING
    progress: int = 0  # 0 to 100
    topic: Optional[Topic] = None
    research: Optional[ResearchBrief] = None
    script: Optional[ScriptStructure] = None
    code_result: Optional[CodeExecutionResult] = None
    visual_paths: List[str] = []
    audio_path: Optional[str] = None
    subtitle_path: Optional[str] = None
    video_path: Optional[str] = None
    cover_path: Optional[str] = None
    caption: Optional[str] = None
    qa_report: Optional[QAReport] = None
    reel_id: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    logs: List[str] = []
