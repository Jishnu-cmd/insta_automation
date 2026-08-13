import random
import uuid
from typing import List
from reelforge.agents.base import BaseAgent
from reelforge.models import JobState, Topic, ContentFormat

TRENDING_AI_TOPICS = [
    {
        "title": "Build a Local AI Coding Agent in 30 Seconds",
        "category": "AI Agents",
        "summary": "Demonstrate how to run a local LLM code execution agent using Python and Ollama/LangChain.",
        "format": ContentFormat.PROJECT_DEMO,
        "trend": 9.5, "relevance": 9.8, "novelty": 9.0, "audience": 9.6
    },
    {
        "title": "Python Face Detection with OpenCV in 4 Lines",
        "category": "Computer Vision",
        "summary": "Show live webcam face detection using Haar Cascades in Python.",
        "format": ContentFormat.CODING_TUTORIAL,
        "trend": 8.8, "relevance": 9.5, "novelty": 8.0, "audience": 9.2
    },
    {
        "title": "Top 3 Open Source AI Models Destroying Proprietary APIs",
        "category": "AI News",
        "summary": "Compare DeepSeek-R1, Llama 3.3, and Qwen 2.5 Coder for developer productivity.",
        "format": ContentFormat.TOP_LIST,
        "trend": 9.8, "relevance": 9.9, "novelty": 9.2, "audience": 9.7
    },
    {
        "title": "Automate Web Scraping with AI & Playwright",
        "category": "Automation",
        "summary": "Extract structured JSON data from complex dynamic websites using Python.",
        "format": ContentFormat.PROJECT_DEMO,
        "trend": 9.2, "relevance": 9.4, "novelty": 8.8, "audience": 9.5
    },
    {
        "title": "I Built an AI Cyber Security Threat Scanner in 24 Hours",
        "category": "Security & AI",
        "summary": "Walkthrough of an automated Python agent that scans IP addresses and generates security reports.",
        "format": ContentFormat.BUILD_JOURNEY,
        "trend": 9.4, "relevance": 9.6, "novelty": 9.1, "audience": 9.5
    }
]

class TopicAgent(BaseAgent):
    """
    F2 - AI Topic Discovery Agent
    Discovers, ranks, and selects trending tech topics based on scoring criteria.
    """
    
    def __init__(self):
        super().__init__("TopicAgent")

    def execute(self, state: JobState) -> JobState:
        self.log(state, "Discovering tech & AI content topics...")
        
        # Select topic candidate (or use provided custom topic if available)
        if state.topic and state.topic.title:
            self.log(state, f"Using user-specified topic: '{state.topic.title}'")
            candidate = {
                "title": state.topic.title,
                "category": state.topic.category or "AI & Coding",
                "summary": state.topic.summary or f"Tutorial and demo on {state.topic.title}",
                "format": state.topic.format or ContentFormat.PROJECT_DEMO,
                "trend": 9.0, "relevance": 9.5, "novelty": 9.0, "audience": 9.2
            }
        else:
            candidate = random.choice(TRENDING_AI_TOPICS)

        # Topic Score Formula calculation
        trend = candidate["trend"]
        relevance = candidate["relevance"]
        novelty = candidate["novelty"]
        audience = candidate["audience"]
        history_bonus = round(random.uniform(0.1, 0.5), 2)  # Simulated feedback score bonus
        
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
        self.log(state, f"Selected Topic: '{topic.title}' (Overall Score: {topic.overall_score}/10)")
        return state
