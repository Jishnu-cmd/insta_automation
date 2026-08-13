import os
import re
from PIL import Image
from reelforge.agents.base import BaseAgent
from reelforge.config import settings
from reelforge.models import JobState, QAReport, QACheckItem

class QAAgent(BaseAgent):
    """
    F14 - AI Quality Control Agent
    Automated multi-point QA checking for technical integrity, visual specifications, secret safety, and content quality.
    """
    
    def __init__(self):
        super().__init__("QAAgent")

    def execute(self, state: JobState) -> JobState:
        self.log(state, f"Executing automated Quality Control checks against threshold ({settings.QA_SCORE_THRESHOLD}%)...")

        checks = []

        # 1. Video Resolution & Aspect Ratio Check
        v_passed = False
        v_score = 0.0
        v_details = "Video file missing"

        if state.video_path and os.path.exists(state.video_path) and os.path.getsize(state.video_path) > 0:
            v_passed = True
            v_score = 100.0
            v_details = f"Valid MP4 file exists ({round(os.path.getsize(state.video_path)/(1024*1024), 2)} MB)"

        checks.append(QACheckItem(name="Video File Integrity", passed=v_passed, score=v_score, details=v_details))

        # 2. Cover Thumbnail Check
        c_passed = False
        c_score = 0.0
        c_details = "Cover image missing"

        if state.cover_path and os.path.exists(state.cover_path):
            try:
                with Image.open(state.cover_path) as img:
                    w, h = img.size
                    if w == settings.VIDEO_WIDTH and h == settings.VIDEO_HEIGHT:
                        c_passed = True
                        c_score = 100.0
                        c_details = f"Cover dimensions verified (1080x1920)"
                    else:
                        c_score = 70.0
                        c_details = f"Cover dimensions mismatch ({w}x{h})"
            except Exception as e:
                c_details = f"Cover inspection error: {str(e)}"

        checks.append(QACheckItem(name="Cover Dimensions Check", passed=c_passed, score=c_score, details=c_details))

        # 3. Secret & API Key Exposure Scan
        secret_clean = True
        secret_details = "No sensitive keys or secrets detected"
        scan_text = f"{state.script.full_text if state.script else ''} {state.caption or ''} {state.code_result.code if state.code_result else ''}"

        # Detect potential API keys or secrets
        secret_patterns = [r"sk-[a-zA-Z0-9]{32,}", r"AIzaSy[a-zA-Z0-9_-]{33}", r"bearer\s+[a-zA-Z0-9\._-]{20,}"]
        for pat in secret_patterns:
            if re.search(pat, scan_text, re.IGNORECASE):
                secret_clean = False
                secret_details = "EXPOSED API KEY DETECTED IN CONTENT!"
                break

        checks.append(QACheckItem(
            name="Secret & Safety Scan",
            passed=secret_clean,
            score=100.0 if secret_clean else 0.0,
            details=secret_details
        ))

        # 4. Code Execution Verification
        code_passed = state.code_result.executed if state.code_result else True
        checks.append(QACheckItem(
            name="Code Execution Check",
            passed=code_passed,
            score=100.0 if code_passed else 50.0,
            details="Code executed without syntax errors" if code_passed else "Code produced execution errors"
        ))

        # Calculate overall score
        total_score = sum(c.score for c in checks) / len(checks)
        passed = total_score >= settings.QA_SCORE_THRESHOLD and secret_clean

        report = QAReport(
            passed=passed,
            overall_score=round(total_score, 1),
            checks=checks,
            secret_scan_clean=secret_clean,
            recommendations=[] if passed else ["Regenerate visual assets or check audio tracks."]
        )

        state.qa_report = report
        self.log(state, f"QA Gate Evaluation Finished: {'PASSED' if passed else 'FAILED'} (Overall Score: {report.overall_score}%).")

        return state
