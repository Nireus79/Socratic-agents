"""Agent Orchestrator - coordinates agents with event emission and state management."""

import logging
from typing import Any, Dict, Optional

from ..events import EventBus, EventType


class AgentOrchestrator:
    """
    Orchestrates agent execution with event emission and state management.

    Provides the interface expected by Agent base classes for:
    - Event emission and handling
    - Agent coordination
    - State tracking
    """

    def __init__(self, event_bus: Optional[EventBus] = None):
        """
        Initialize the orchestrator.

        Args:
            event_bus: Optional EventBus for event handling. Creates new if not provided.
        """
        self.event_emitter = event_bus or EventBus()
        self.logger = logging.getLogger("socratic_agents.orchestrator")
        self.agents: Dict[str, Any] = {}
        self.services: Dict[str, Any] = {}

    def register_agent(self, name: str, agent: Any) -> None:
        """
        Register an agent with the orchestrator.

        Args:
            name: Agent name
            agent: Agent instance
        """
        self.agents[name] = agent
        self.logger.info(f"Registered agent: {name}")

    def get_agent(self, name: str) -> Optional[Any]:
        """
        Get a registered agent.

        Args:
            name: Agent name

        Returns:
            Agent instance or None if not found
        """
        return self.agents.get(name)

    def register_service(self, name: str, service: Any) -> None:
        """
        Register a service with the orchestrator.

        Args:
            name: Service name
            service: Service instance
        """
        self.services[name] = service
        self.logger.info(f"Registered service: {name}")

    def get_service(self, name: str) -> Optional[Any]:
        """
        Get a registered service.

        Args:
            name: Service name

        Returns:
            Service instance or None if not found
        """
        return self.services.get(name)

    def emit_event(self, event_type: EventType, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Emit an event through the event bus.

        Args:
            event_type: Type of event to emit
            data: Optional event data
        """
        self.event_emitter.emit(event_type, data or {})

    def on_event(self, event_type: EventType, callback) -> None:
        """
        Register an event handler.

        Args:
            event_type: EventType to listen for
            callback: Callable to invoke on event
        """
        self.event_emitter.subscribe(event_type, callback)

    def off_event(self, event_type: EventType, callback) -> None:
        """
        Unregister an event handler.

        Args:
            event_type: EventType to stop listening for
            callback: Callable to remove
        """
        self.event_emitter.unsubscribe(event_type, callback)
