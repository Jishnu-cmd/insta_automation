import sys
import argparse
from reelforge.pipeline.orchestrator import PipelineOrchestrator

def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    parser = argparse.ArgumentParser(description="ReelForge AI CLI — Multi-Agent Reel Generator")
    parser.add_argument("command", choices=["generate", "schedule"], help="Command to execute")
    parser.add_argument("--topic", type=str, default=None, help="Custom Reel topic title")
    parser.add_argument("--format", type=str, default=None, help="Content format (e.g. PROJECT_DEMO)")

    args = parser.parse_args()

    orchestrator = PipelineOrchestrator()

    if args.command == "generate":
        print(f"[ReelForge AI] Starting Pipeline Generation (Topic: {args.topic or 'Autonomous AI Discovery'})...")
        job_state = orchestrator.run_pipeline(custom_topic=args.topic, custom_format=args.format)
        print("\n=========================================================")
        print(f"  Job ID: {job_state.job_id}")
        print(f"  Status: {job_state.status.value}")
        print(f"  Topic: {job_state.topic.title if job_state.topic else 'N/A'}")
        print(f"  Video Path: {job_state.video_path}")
        print(f"  Cover Path: {job_state.cover_path}")
        print(f"  QA Pass Score: {job_state.qa_report.overall_score if job_state.qa_report else 'N/A'}%")
        print("=========================================================")

if __name__ == "__main__":
    main()

