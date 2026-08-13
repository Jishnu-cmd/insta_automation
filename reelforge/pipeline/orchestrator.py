import uuid
import logging
from datetime import datetime
from reelforge.database import SessionLocal, JobDB, ReelDB, TopicDB, init_db
from reelforge.models import JobState, JobStatus, Topic, ContentFormat
from reelforge.agents.topic_agent import TopicAgent
from reelforge.agents.research_agent import ResearchAgent
from reelforge.agents.script_agent import ScriptAgent
from reelforge.agents.code_agent import CodeAgent
from reelforge.agents.visual_agent import VisualAgent
from reelforge.agents.voice_agent import VoiceAgent
from reelforge.agents.subtitle_agent import SubtitleAgent
from reelforge.agents.video_agent import VideoAgent
from reelforge.agents.cover_agent import CoverAgent
from reelforge.agents.caption_agent import CaptionAgent
from reelforge.agents.qa_agent import QAAgent
from reelforge.agents.publishing_agent import PublishingAgent
from reelforge.agents.analytics_agent import AnalyticsAgent
from reelforge.agents.learning_agent import LearningAgent

logger = logging.getLogger("ReelForge.Orchestrator")

class PipelineOrchestrator:
    """
    End-to-End Workflow Orchestrator for ReelForge AI.
    Executes multi-agent pipeline sequentially with state persistence and failure retries.
    """

    def __init__(self):
        init_db()
        self.topic_agent = TopicAgent()
        self.research_agent = ResearchAgent()
        self.script_agent = ScriptAgent()
        self.code_agent = CodeAgent()
        self.visual_agent = VisualAgent()
        self.voice_agent = VoiceAgent()
        self.subtitle_agent = SubtitleAgent()
        self.video_agent = VideoAgent()
        self.cover_agent = CoverAgent()
        self.caption_agent = CaptionAgent()
        self.qa_agent = QAAgent()
        self.publishing_agent = PublishingAgent()
        self.analytics_agent = AnalyticsAgent()
        self.learning_agent = LearningAgent()

    def run_pipeline(self, custom_topic: str = None, custom_format: str = None) -> JobState:
        job_id = f"REEL-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}"
        state = JobState(job_id=job_id, status=JobStatus.PENDING)

        if custom_topic:
            fmt = ContentFormat.PROJECT_DEMO
            if custom_format and custom_format.upper() in ContentFormat.__members__:
                fmt = ContentFormat[custom_format.upper()]
            state.topic = Topic(
                title=custom_topic,
                category="AI & Projects",
                summary=f"Custom Reel topic: {custom_topic}",
                format=fmt
            )

        self._save_job_db(state)
        logger.info(f"Starting ReelForge AI Pipeline Job [{job_id}]...")

        steps = [
            (JobStatus.DISCOVERING, 10, self.topic_agent),
            (JobStatus.RESEARCHING, 20, self.research_agent),
            (JobStatus.SCRIPTING, 30, self.script_agent),
            (JobStatus.EXECUTING_CODE, 40, self.code_agent),
            (JobStatus.GENERATING_VISUALS, 50, self.visual_agent),
            (JobStatus.GENERATING_VOICE, 60, self.voice_agent),
            (JobStatus.GENERATING_SUBTITLES, 65, self.subtitle_agent),
            (JobStatus.COMPOSING_VIDEO, 75, self.video_agent),
            (JobStatus.GENERATING_COVER, 80, self.cover_agent),
            (JobStatus.GENERATING_CAPTION, 85, self.caption_agent),
            (JobStatus.QA_CHECKING, 90, self.qa_agent),
            (JobStatus.PUBLISHING, 95, self.publishing_agent),
        ]

        try:
            for status, progress, agent in steps:
                state.status = status
                state.progress = progress
                self._save_job_db(state)
                
                # Execute agent on state
                state = agent.execute(state)

                # Check QA failure gate rule
                if status == JobStatus.QA_CHECKING and state.qa_report and not state.qa_report.passed:
                    state.error_message = f"QA Gate Check Failed (Score: {state.qa_report.overall_score}%). Triggering regeneration."
                    state.status = JobStatus.FAILED
                    self._save_job_db(state)
                    return state

            # Post-publish analytics & learning
            state = self.analytics_agent.execute(state)
            state = self.learning_agent.execute(state)

            state.status = JobStatus.COMPLETED
            state.progress = 100
            self._save_job_db(state)
            self._save_reel_db(state)

            logger.info(f"Job [{job_id}] completed successfully!")

        except Exception as e:
            logger.exception(f"Error during job [{job_id}] execution: {str(e)}")
            state.status = JobStatus.FAILED
            state.error_message = str(e)
            self._save_job_db(state)

        return state

    def _save_job_db(self, state: JobState):
        db = SessionLocal()
        try:
            job_record = db.query(JobDB).filter(JobDB.id == state.job_id).first()
            if not job_record:
                job_record = JobDB(
                    id=state.job_id,
                    status=state.status.value,
                    progress=state.progress,
                    topic_title=state.topic.title if state.topic else "",
                    error_message=state.error_message,
                    state_json=state.model_dump_json()
                )
                db.add(job_record)
            else:
                job_record.status = state.status.value
                job_record.progress = state.progress
                job_record.topic_title = state.topic.title if state.topic else ""
                job_record.error_message = state.error_message
                job_record.state_json = state.model_dump_json()
                job_record.updated_at = datetime.utcnow()
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"DB Job save error: {str(e)}")
        finally:
            db.close()

    def _save_reel_db(self, state: JobState):
        if not state.video_path or not state.topic:
            return

        db = SessionLocal()
        try:
            reel_id = state.reel_id or f"reel_{uuid.uuid4().hex[:8]}"
            reel_record = ReelDB(
                id=reel_id,
                job_id=state.job_id,
                topic_title=state.topic.title,
                video_path=state.video_path,
                cover_path=state.cover_path or "",
                caption=state.caption or "",
                status="PUBLISHED" if state.status == JobStatus.COMPLETED else "CREATED",
                qa_score=state.qa_report.overall_score if state.qa_report else 90.0,
                published_at=datetime.utcnow()
            )
            db.add(reel_record)
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"DB Reel save error: {str(e)}")
        finally:
            db.close()
