"""Agent orchestration and coordination system."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional

from .events import EventType


class EventEmitter:
    """Simple event emitter for agent communication."""

    def __init__(self):
        """Initialize event emitter."""
        self._listeners: Dict[EventType, List[Callable]] = {}
        self.logger = logging.getLogger("socratic_agents.events")

    def on(self, event_type: EventType, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Register a listener for an event type.

        Args:
            event_type: The EventType to listen for
            callback: Function to call when event is emitted
        """
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)

    def off(self, event_type: EventType, callback: Callable) -> None:
        """
        Remove a listener for an event type.

        Args:
            event_type: The EventType to stop listening for
            callback: The callback function to remove
        """
        if event_type in self._listeners:
            if callback in self._listeners[event_type]:
                self._listeners[event_type].remove(callback)

    def emit(self, event_type: EventType, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Emit an event to all registered listeners.

        Args:
            event_type: The EventType being emitted
            data: Optional data to include with the event
        """
        if data is None:
            data = {}

        # Add event type to data if not present
        if "event_type" not in data:
            data["event_type"] = event_type.value

        # Call all registered listeners
        if event_type in self._listeners:
            for callback in self._listeners[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    self.logger.error(
                        f"Error in event listener for {event_type.value}: {e}", exc_info=True
                    )

    def emit_async(self, event_type: EventType, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Emit an event asynchronously (for compatibility, currently synchronous).

        Args:
            event_type: The EventType being emitted
            data: Optional data to include with the event
        """
        self.emit(event_type, data)


class AgentOrchestrator:
    """
    Orchestrates communication and coordination between agents.

    Provides:
    - Event emission system for agent communication
    - Agent registration and discovery
    - Shared state management
    - Task coordination
    """

    def __init__(
        self,
        database: Any = None,
        vector_db: Any = None,
        claude_client: Any = None,
        config: Any = None,
    ) -> None:
        """
        Initialize the orchestrator.

        Args:
            database: Database connection (Socrates context)
            vector_db: Vector database connection (Socrates context)
            claude_client: Claude LLM client (Socrates context)
            config: Configuration object (Socrates context)
        """
        self.logger = logging.getLogger("socratic_agents.orchestrator")
        self.event_emitter = EventEmitter()
        self._agents: Dict[str, Any] = {}
        self._state: Dict[str, Any] = {}
        # Socrates-specific attributes
        self.database = database
        self.vector_db = vector_db
        self.claude_client = claude_client
        self.config = config
        self.context_analyzer: Any = None

    def register_agent(self, name: str, agent: Any) -> None:
        """
        Register an agent with the orchestrator.

        Args:
            name: Unique name for the agent
            agent: The agent instance to register
        """
        self._agents[name] = agent
        self.logger.info(f"Registered agent: {name}")

    def get_agent(self, name: str) -> Optional[Any]:
        """
        Get a registered agent by name.

        Args:
            name: The agent name

        Returns:
            The agent instance, or None if not found
        """
        return self._agents.get(name)

    def list_agents(self) -> List[str]:
        """
        List all registered agent names.

        Returns:
            List of agent names
        """
        return list(self._agents.keys())

    def set_state(self, key: str, value: Any) -> None:
        """
        Set shared state value.

        Args:
            key: State key
            value: State value
        """
        self._state[key] = value

    def get_state(self, key: str, default: Any = None) -> Any:
        """
        Get shared state value.

        Args:
            key: State key
            default: Default value if key not found

        Returns:
            The state value, or default
        """
        return self._state.get(key, default)

    def clear_state(self) -> None:
        """Clear all shared state."""
        self._state.clear()

    async def process_async(self, agent_name: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a request through an agent asynchronously.

        Args:
            agent_name: Name of the agent to process request
            request: Request dictionary

        Returns:
            Response from the agent
        """
        agent = self.get_agent(agent_name)
        if not agent:
            return {"status": "error", "message": f"Agent not found: {agent_name}"}

        if hasattr(agent, "process_async"):
            return await agent.process_async(request)
        else:
            # Run sync method in thread pool
            return await asyncio.to_thread(agent.process, request)

    def process(self, agent_name: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a request through an agent synchronously.

        Args:
            agent_name: Name of the agent to process request
            request: Request dictionary

        Returns:
            Response from the agent
        """
        agent = self.get_agent(agent_name)
        if not agent:
            return {"status": "error", "message": f"Agent not found: {agent_name}"}

        return agent.process(request)
