import time
import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from reelforge.config import settings
from reelforge.pipeline.orchestrator import PipelineOrchestrator

logger = logging.getLogger("ReelForge.Scheduler")

class AutonomousScheduler:
    """
    F1 - Autonomous Scheduler Agent
    Triggers automated end-to-end Reel generation and publishing every 30 minutes.
    """

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.orchestrator = PipelineOrchestrator()
        self.is_running = False

    def scheduled_job(self):
        logger.info(f"Scheduler Trigger: Executing automated ReelForge AI pipeline run (Interval: {settings.SCHEDULE_INTERVAL_MINUTES}m)...")
        try:
            self.orchestrator.run_pipeline()
        except Exception as e:
            logger.error(f"Scheduler job execution error: {str(e)}")

    def start(self):
        if self.is_running:
            return

        interval_mins = getattr(settings, "SCHEDULE_INTERVAL_MINUTES", 30)

        self.scheduler.add_job(
            self.scheduled_job,
            'interval',
            minutes=interval_mins,
            id="recurring_reelforge_job",
            next_run_time=datetime.now()  # Run immediately on start then every 30 mins
        )
        self.scheduler.start()
        self.is_running = True
        logger.info(f"Autonomous Scheduler active! Automatically generating & publishing Reels every {interval_mins} minutes.")

    def stop(self):
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Autonomous Scheduler stopped.")
