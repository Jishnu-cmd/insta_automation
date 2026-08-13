from abc import ABC, abstractmethod
import logging
from typing import Dict, Any
from reelforge.models import JobState

logger = logging.getLogger("ReelForge.Agent")

class BaseAgent(ABC):
    """
    Abstract Base Class for all ReelForge AI Agents.
    Enforces standardized execution logging, error isolation, and state mutation.
    """
    
    def __init__(self, name: str):
        self.name = name

    def log(self, state: JobState, message: str):
        log_entry = f"[{self.name}] {message}"
        state.logs.append(log_entry)
        logger.info(log_entry)

    @abstractmethod
    def execute(self, state: JobState) -> JobState:
        """
        Execute the agent's task on the provided job state.
        Must return the updated JobState.
        """
        pass
