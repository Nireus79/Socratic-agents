"""
Base Agent class for Socrates AI with service injection support.

Agents can be initialized in two ways:
1. Service Injection (Recommended): Pass individual services for loose coupling
2. Orchestrator (Legacy): Pass orchestrator for backward compatibility
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional

from socratic_agents.events import EventType

if TYPE_CHECKING:
    from socratic_agents.orchestration.orchestrator import AgentOrchestrator
    from socratic_agents.services.base import (
        ConfigService,
        DatabaseService,
        EventEmitterService,
        LLMService,
        VectorDatabaseService,
    )


class Agent(ABC):
    """
    Abstract base class for all agents in the Socrates AI.

    Supports both service injection (recommended) and orchestrator-based initialization
    for backward compatibility.

    Service-Injected Initialization:
        agent = MyAgent(
            name="MyAgent",
            database=db_service,
            llm=llm_service,
            vector_db=vector_service,
            config=config_service,
            event_emitter=event_service
        )

    Legacy Orchestrator Initialization (backward compatible):
        agent = MyAgent(name="MyAgent", orchestrator=orchestrator)
    """

    def __init__(
        self,
        name: str,
        orchestrator: Optional["AgentOrchestrator"] = None,
        database: Optional["DatabaseService"] = None,
        llm: Optional["LLMService"] = None,
        vector_db: Optional["VectorDatabaseService"] = None,
        config: Optional["ConfigService"] = None,
        event_emitter: Optional["EventEmitterService"] = None,
    ):
        """
        Initialize an agent with either services or orchestrator.

        Args:
            name: Display name for the agent
            orchestrator: (Legacy) AgentOrchestrator for backward compatibility
            database: DatabaseService for database operations
            llm: LLMService for LLM operations
            vector_db: VectorDatabaseService for vector operations
            config: ConfigService for configuration
            event_emitter: EventEmitterService for event handling
        """
        self.name = name
        self.logger = logging.getLogger(f"socrates.agents.{name}")

        # Support both service injection and orchestrator patterns
        if orchestrator is not None:
            # Legacy: Extract services from orchestrator
            self.orchestrator = orchestrator
            self.database = orchestrator.database if hasattr(orchestrator, "database") else database
            self.llm = orchestrator.claude_client if hasattr(orchestrator, "claude_client") else llm
            self.vector_db = (
                orchestrator.vector_db if hasattr(orchestrator, "vector_db") else vector_db
            )
            self.config = orchestrator.config if hasattr(orchestrator, "config") else config
            self.event_emitter = (
                orchestrator.event_emitter
                if hasattr(orchestrator, "event_emitter")
                else event_emitter
            )
        else:
            # New: Direct service injection
            self.orchestrator = None
            self.database = database
            self.llm = llm
            self.vector_db = vector_db
            self.config = config
            self.event_emitter = event_emitter

    @abstractmethod
    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a request and return a response (synchronous).

        All subclasses must implement this method to handle their specific logic.

        Args:
            request: Dictionary containing the request parameters

        Returns:
            Dictionary containing the response data

        Example:
            >>> result = agent.process({'action': 'create', 'name': 'Project X'})
            >>> if result['status'] == 'success':
            ...     print(result['data'])
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
        # Run sync method in thread pool to avoid blocking
        return await asyncio.to_thread(self.process, request)

    def log(self, message: str, level: str = "INFO") -> None:
        """
        Emit a structured log event and write to logger.

        Replaces direct print statements with event emission for better integration
        with plugins and UI systems. Works with both service injection and orchestrator patterns.

        Args:
            message: The message to log
            level: Log level (DEBUG, INFO, WARNING, ERROR)

        Example:
            >>> agent.log("Processing request", level="INFO")
            >>> agent.log("Something went wrong!", level="ERROR")
        """
        # Map log level to EventType and logger level
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

        # Log to Python logger
        logger_method(f"{self.name}: {message}")

        # Emit structured event (if event_emitter is available)
        event_emitter = self.event_emitter
        if event_emitter is None and self.orchestrator is not None:
            event_emitter = self.orchestrator.event_emitter

        if event_emitter is not None:
            event_emitter.emit(
                event_type,
                {"agent": self.name, "message": message, "timestamp": datetime.now().isoformat()},
            )

    def emit_event(self, event_type: EventType, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Emit a structured event through the event emitter.

        Allows agents to emit domain-specific events (e.g., CODE_GENERATED, CONFLICT_DETECTED).
        Works with both service injection and orchestrator patterns.

        Args:
            event_type: The type of event to emit
            data: Optional data to include with the event

        Example:
            >>> self.emit_event(EventType.CODE_GENERATED, {"script": code, "lines": 42})
        """
        if data is None:
            data = {}

        # Add agent context if not already present
        if "agent" not in data:
            data["agent"] = self.name

        # Emit through available event emitter
        event_emitter = self.event_emitter
        if event_emitter is None and self.orchestrator is not None:
            event_emitter = self.orchestrator.event_emitter

        if event_emitter is not None:
            event_emitter.emit(event_type, data)

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
            reason: Why this knowledge is being suggested (insufficient_context, pattern_detected, etc.)

        Example:
            >>> self.suggest_knowledge_addition(
            ...     content="REST APIs use HTTP methods for CRUD operations",
            ...     category="api_design",
            ...     topic="rest_conventions",
            ...     difficulty="intermediate",
            ...     reason="insufficient_context"
            ... )
        """
        self.emit_event(
            EventType.KNOWLEDGE_SUGGESTION,
            {
                "content": content,
                "category": category,
                "topic": topic or category,
                "difficulty": difficulty,
                "reason": reason,
                "timestamp": datetime.now().isoformat(),
            },
        )
