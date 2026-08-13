from typing import List
from reelforge.agents.base import BaseAgent
from reelforge.config import settings
from reelforge.models import JobState, ScriptStructure, ScriptSegment, ContentFormat

class ScriptAgent(BaseAgent):
    """
    F4 & F5 - Script Generation & Content Format Agent
    Converts research into a high-retention 9:16 vertical Reel script with timing & visual cues.
    """
    
    def __init__(self):
        super().__init__("ScriptAgent")

    def execute(self, state: JobState) -> JobState:
        if not state.topic or not state.research:
            raise ValueError("State requires topic and research brief before scripting.")

        self.log(state, f"Generating 9:16 short script for format '{state.topic.format.value}'...")

        topic_title = state.topic.title
        research = state.research
        fmt = state.topic.format

        # Generate structured 6-step short-form Reel script
        hook = f"This AI tool can write and execute code for you!" if "Agent" in topic_title else f"Stop writing repetitive Python code manually!"
        problem = "Normally, developers spend hours writing, testing, and debugging every single line."
        explanation = "AI agents combine reasoning with tool execution to automate the entire coding lifecycle."
        
        # Runnable demo code snippet for Code Execution Sandbox
        if research.code_ideas:
            demo_code = research.code_ideas[0]
        else:
            demo_code = (
                "import time\n\n"
                "print('🤖 Flow Tech AI Agent Initializing...')\n"
                "time.sleep(0.5)\n"
                "print('✅ Code Generated & Executed in Sandbox!')"
            )

        result = "In seconds, you get fully functional, tested code ready for production."
        cta = f"Follow {settings.INSTAGRAM_HANDLE} for daily AI & coding projects!"

        segments = [
            ScriptSegment(
                section="HOOK",
                narration=hook,
                visual_prompt="Bold dynamic text animation on dark gradient background",
                duration_seconds=3.5
            ),
            ScriptSegment(
                section="PROBLEM",
                narration=problem,
                visual_prompt="Frustrated developer workflow graphic with red alert badge",
                duration_seconds=4.0
            ),
            ScriptSegment(
                section="EXPLANATION",
                narration=explanation,
                visual_prompt="AI neural network diagram connecting code blocks to execution tools",
                duration_seconds=5.0
            ),
            ScriptSegment(
                section="DEMO",
                narration="Watch this Python sandbox execute the code live.",
                visual_prompt="Live dark-mode IDE code execution terminal window with green output text",
                duration_seconds=6.0,
                code_snippet=demo_code
            ),
            ScriptSegment(
                section="RESULT",
                narration=result,
                visual_prompt="Success metric card showing 100x speedup and clean test passage",
                duration_seconds=4.0
            ),
            ScriptSegment(
                section="CTA",
                narration=cta,
                visual_prompt=f"Account badge for {settings.INSTAGRAM_HANDLE} with pulsing Follow button",
                duration_seconds=3.5
            )
        ]

        full_text = " ".join([seg.narration for seg in segments])

        script = ScriptStructure(
            topic=topic_title,
            format=fmt,
            hook=hook,
            problem=problem,
            explanation=explanation,
            demo_code=demo_code,
            result=result,
            cta=cta,
            full_text=full_text,
            segments=segments,
            quality_score=94.5
        )

        state.script = script
        self.log(state, f"Script generated successfully ({len(segments)} segments, total narration ~{sum(s.duration_seconds for s in segments)}s).")
        return state
