"""Base Agent class for Socratic Agents - aligned with monolithic standards."""

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional

from socratic_agents.events import EventType

if TYPE_CHECKING:
    from socratic_agents.orchestration import AgentOrchestrator


class Agent(ABC):
    """
    Abstract base class for all agents in Socratic Agents.

    Agents are specialized components that handle different aspects of AI workflows.
    All agents are capable of:
    - Synchronous request processing
    - Asynchronous request processing (default wraps sync)
    - Event-based logging (replaces print statements)
    - Structured error handling
    """

    def __init__(self, name: str, orchestrator: "AgentOrchestrator"):
        """
        Initialize an agent.

        Args:
            name: Display name for the agent
            orchestrator: Reference to the AgentOrchestrator for accessing other agents/services
        """
        self.name = name
        self.orchestrator = orchestrator
        self.logger = logging.getLogger(f"socratic_agents.{name}")
        self.created_at = datetime.utcnow()

    @abstractmethod
    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a request and return a response (synchronous).

        All subclasses must implement this method to handle their specific logic.

        Args:
            request: Dictionary containing the request parameters

        Returns:
            Dictionary containing the response data
        """
        pass

    async def process_async(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a request asynchronously.

        Default implementation wraps the synchronous process method using asyncio.
        Subclasses can override this to provide true async processing (e.g., for I/O-bound operations).

        Args:
            request: Dictionary containing the request parameters

        Returns:
            Dictionary containing the response data
        """
        return await asyncio.to_thread(self.process, request)

    def log(self, message: str, level: str = "INFO") -> None:
        """
        Emit a structured log event and write to logger.

        Replaces direct print statements with event emission for better integration
        with plugins and UI systems.

        Args:
            message: The message to log
            level: Log level (DEBUG, INFO, WARNING, ERROR)
        """
        event_map = {
            "DEBUG": EventType.LOG_DEBUG,
            "INFO": EventType.LOG_INFO,
            "WARNING": EventType.LOG_WARNING,
            "ERROR": EventType.LOG_ERROR,
        }
        logger_method_map = {
            "DEBUG": self.logger.debug,
            "INFO": self.logger.info,
            "WARNING": self.logger.warning,
            "ERROR": self.logger.error,
        }

        event_type = event_map.get(level, EventType.LOG_INFO)
        logger_method = logger_method_map.get(level, self.logger.info)

        logger_method(f"{self.name}: {message}")
        self.orchestrator.event_emitter.emit(
            event_type,
            {"agent": self.name, "message": message, "timestamp": datetime.utcnow().isoformat()},
        )

    def emit_event(self, event_type: EventType, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Emit a structured event through the orchestrator's event emitter.

        Allows agents to emit domain-specific events (e.g., CODE_GENERATED, CONFLICT_DETECTED).

        Args:
            event_type: The type of event to emit
            data: Optional data to include with the event
        """
        if data is None:
            data = {}

        if "agent" not in data:
            data["agent"] = self.name

        self.orchestrator.event_emitter.emit(event_type, data)

    def suggest_knowledge_addition(
        self,
        content: str,
        category: str,
        topic: Optional[str] = None,
        difficulty: str = "intermediate",
        reason: str = "insufficient_context",
    ) -> None:
        """
        Suggest adding knowledge when agent detects a gap.

        This enables automatic knowledge enrichment when agents encounter
        topics or patterns that should be remembered for the project.

        Args:
            content: The knowledge content to remember
            category: Knowledge category (e.g., 'technical', 'domain_specific')
            topic: Specific topic within category
            difficulty: beginner, intermediate, or advanced
            reason: Why this knowledge is being suggested
        """
        self.emit_event(
            EventType.KNOWLEDGE_SUGGESTION,
            {
                "content": content,
                "category": category,
                "topic": topic or category,
                "difficulty": difficulty,
                "reason": reason,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"


# Backwards compatibility alias
BaseAgent = Agent
