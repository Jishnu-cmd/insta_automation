from reelforge.agents.base import BaseAgent
from reelforge.config import settings
from reelforge.models import JobState

class CaptionAgent(BaseAgent):
    """
    F13 - Caption Agent
    Generates post caption, call to action, targeted hashtags, and Instagram SEO keywords.
    """
    
    def __init__(self):
        super().__init__("CaptionAgent")

    def execute(self, state: JobState) -> JobState:
        if not state.topic or not state.script:
            raise ValueError("Topic and script state required for CaptionAgent.")

        self.log(state, "Generating caption, CTA, hashtags, and keywords...")

        topic = state.topic
        script = state.script

        caption_lines = [
            f"🚀 {topic.title}",
            "",
            f"💡 {script.problem}",
            f"✨ {script.explanation}",
            "",
            "💻 Code snippet tested and executed in Flow Tech Sandbox!",
            "",
            f"Would you use this in your workflow? Comment below 👇",
            "",
            f"👉 Follow {settings.INSTAGRAM_HANDLE} for daily AI, Python & Coding projects!",
            "",
            "#AI #Python #Coding #ArtificialIntelligence #SoftwareEngineering #TechProjects #MachineLearning #Developer #CodeLife #FlowTech"
        ]

        full_caption = "\n".join(caption_lines)
        state.caption = full_caption

        self.log(state, "Instagram caption generated successfully.")
        return state
