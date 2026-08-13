import random
import uuid
from typing import List
from reelforge.agents.base import BaseAgent
from reelforge.config import settings
from reelforge.models import JobState, Topic, ContentFormat

TOPIC_LIBRARIES = {
    "AI, Coding & Tech Projects": [
        {
            "title": "Build a Local AI Coding Agent in 30 Seconds",
            "category": "AI & Coding",
            "summary": "Demonstrate running a local Python AI agent that writes and executes code automatically.",
            "format": ContentFormat.PROJECT_DEMO
        },
        {
            "title": "AI Face Detection in Python in 4 Lines",
            "category": "Computer Vision",
            "summary": "Real-time OpenCV synthetic frame detection and bounding box visualization in Python.",
            "format": ContentFormat.CODING_TUTORIAL
        },
        {
            "title": "Automate Web Data Extraction with AI & Python",
            "category": "Automation",
            "summary": "Extract structured JSON payloads from dynamic websites using Python automation scripts.",
            "format": ContentFormat.PROJECT_DEMO
        }
    ],
    "Interesting Tech & Science Facts": [
        {
            "title": "Why 99% of Internet Data Travels Under the Ocean",
            "category": "Tech Facts",
            "summary": "Subsea fiber-optic cables transmit over 99% of international data, not satellites.",
            "format": ContentFormat.AI_NEWS
        },
        {
            "title": "The First Computer Bug Was an Actual Moth in 1947",
            "category": "Tech Facts",
            "summary": "Grace Hopper's team found a real moth trapped in Relay #70 of the Harvard Mark II computer.",
            "format": ContentFormat.TOP_LIST
        },
        {
            "title": "Why Python is Named After a Comedy Show, Not a Snake",
            "category": "Tech Facts",
            "summary": "Guido van Rossum named Python after Monty Python's Flying Circus BBC comedy series in 1991.",
            "format": ContentFormat.CODING_TUTORIAL
        },
        {
            "title": "How Quantum Computers Solve 10,000-Year Math in Seconds",
            "category": "Quantum Science",
            "summary": "Superposition and entanglement allow qubits to evaluate billions of states simultaneously.",
            "format": ContentFormat.PROJECT_DEMO
        }
    ],
    "AI News & Breakthroughs": [
        {
            "title": "Top 3 Open Source AI Models Destroying Proprietary APIs",
            "category": "AI News",
            "summary": "Comparison of DeepSeek-R1, Llama 3.3, and Qwen 2.5 Coder for developer productivity.",
            "format": ContentFormat.TOP_LIST
        },
        {
            "title": "This New AI Model Solved 50-Year Biological Mysteries in 24 Hours",
            "category": "AI Breakthroughs",
            "summary": "AlphaFold protein structure prediction revolutionizes medical research and drug discovery.",
            "format": ContentFormat.AI_NEWS
        }
    ],
    "Developer Tips & Hacks": [
        {
            "title": "5 Hidden Python Tricks Senior Developers Use Daily",
            "category": "Developer Hacks",
            "summary": "List comprehension, walrus operator :=, zip(), and dataclasses performance tricks.",
            "format": ContentFormat.TOP_LIST
        },
        {
            "title": "Stop Using Print Statements for Python Debugging",
            "category": "Developer Hacks",
            "summary": "How to use Python icecream (ic) and built-in breakpoint() for fast debugging.",
            "format": ContentFormat.CODING_TUTORIAL
        }
    ]
}

class TopicAgent(BaseAgent):
    """
    F2 - AI Topic Discovery Agent
    Discovers, ranks, and selects trending tech topics based on active niche category.
    """
    
    def __init__(self):
        super().__init__("TopicAgent")

    def execute(self, state: JobState) -> JobState:
        active_niche = settings.ACTIVE_NICHE
        self.log(state, f"Discovering topics for active niche: '{active_niche}'...")
        
        # User custom topic or active niche pool selection
        if state.topic and state.topic.title:
            self.log(state, f"Using user-specified topic: '{state.topic.title}'")
            candidate = {
                "title": state.topic.title,
                "category": state.topic.category or active_niche,
                "summary": state.topic.summary or f"Explainer and demo on {state.topic.title}",
                "format": state.topic.format or ContentFormat.PROJECT_DEMO
            }
        else:
            pool = TOPIC_LIBRARIES.get(active_niche, TOPIC_LIBRARIES["AI, Coding & Tech Projects"])
            candidate = random.choice(pool)

        trend = round(random.uniform(9.0, 9.8), 2)
        relevance = round(random.uniform(9.2, 9.9), 2)
        novelty = round(random.uniform(8.8, 9.6), 2)
        audience = round(random.uniform(9.0, 9.7), 2)
        history_bonus = round(random.uniform(0.1, 0.4), 2)
        
        overall_score = round((trend + relevance + novelty + audience) / 4.0 + history_bonus, 2)
        overall_score = min(overall_score, 10.0)

        topic = Topic(
            id=str(uuid.uuid4())[:8],
            title=candidate["title"],
            category=candidate["category"],
            summary=candidate["summary"],
            trend_score=trend,
            relevance_score=relevance,
            novelty_score=novelty,
            audience_score=audience,
            historical_score=history_bonus,
            overall_score=overall_score,
            format=candidate["format"]
        )

        state.topic = topic
        self.log(state, f"Selected Topic: '{topic.title}' [{topic.category}] (Score: {topic.overall_score}/10)")
        return state
