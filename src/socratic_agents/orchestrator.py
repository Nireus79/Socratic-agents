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
    - Provider-aware LLM client selection
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

    def get_llm_client_for_provider(self, provider_config: Dict[str, Any] | None = None) -> Any:
        """
        Get the appropriate LLM client based on provider configuration.

        This method implements provider-aware client selection. When Socrates passes
        a provider_config with provider name and credentials, this method instantiates
        the correct client (Claude, OpenAI, Ollama, Gemini, etc.).

        Supported providers:
        - claude: Anthropic Claude API (via socratic-nexus ClaudeClient)
        - openai: OpenAI GPT models (via socratic-nexus OpenAIClient)
        - ollama: Local Ollama models (via socratic-nexus OllamaClient)
        - gemini: Google Gemini API (via socratic-nexus GoogleClient)

        For backward compatibility, if no provider_config is provided, defaults to
        the existing claude_client.

        Args:
            provider_config: Dict with 'provider', 'api_key', and 'settings'.
                           If None, defaults to claude_client.

        Returns:
            An LLM client instance appropriate for the provider

        Raises:
            ValueError: If provider is unknown or client instantiation fails
        """
        # Default to Claude client if no provider config
        if not provider_config or not provider_config.get("provider"):
            return self.claude_client

        provider = provider_config.get("provider", "").lower()
        api_key = provider_config.get("api_key")

        try:
            if provider == "claude":
                from socratic_nexus.clients import ClaudeClient
                subscription_token = provider_config.get("subscription_token")
                client = ClaudeClient(
                    api_key=api_key,
                    orchestrator=self,
                    subscription_token=subscription_token,
                )
                self.logger.debug(f"Created ClaudeClient for provider: {provider}")
                return client

            elif provider == "ollama":
                from socratic_nexus.clients import OllamaClient
                # Ollama doesn't require API key, but accepts it for compatibility
                client = OllamaClient(api_key=api_key, orchestrator=self)
                settings = provider_config.get("settings", {})
                base_url = settings.get("base_url", "http://localhost:11434")
                if hasattr(client, "base_url"):
                    client.base_url = base_url
                self.logger.debug(f"Created OllamaClient for provider: {provider} (base_url: {base_url})")
                return client

            elif provider == "openai":
                from socratic_nexus.clients import OpenAIClient
                if not api_key:
                    raise ValueError("OpenAI provider requires an API key")
                client = OpenAIClient(api_key=api_key, orchestrator=self)
                self.logger.debug(f"Created OpenAIClient for provider: {provider}")
                return client

            elif provider == "gemini":
                from socratic_nexus.clients import GoogleClient
                if not api_key:
                    raise ValueError("Gemini provider requires an API key")
                client = GoogleClient(api_key=api_key, orchestrator=self)
                self.logger.debug(f"Created GoogleClient for provider: {provider}")
                return client

            else:
                self.logger.warning(f"Unknown provider: {provider}, falling back to claude_client")
                return self.claude_client

        except ImportError as e:
            self.logger.error(f"Client library not available for {provider}: {e}")
            return self.claude_client  # Fallback to claude
        except Exception as e:
            self.logger.error(f"Failed to create LLM client for {provider}: {e}")
            return self.claude_client  # Fallback to claude

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


# Agent bus for inter-agent communication
from .agent_bus import AgentBus

# Add agent_bus attribute to AgentOrchestrator
AgentOrchestrator.agent_bus = None

# Store original __init__
_original_init = AgentOrchestrator.__init__


def __new_init__(
    self,
    database=None,
    vector_db=None,
    claude_client=None,
    config=None,
    enable_agent_bus=True,
):
    """Enhanced __init__ with agent bus support."""
    _original_init(self, database, vector_db, claude_client, config)
    self.agent_bus = AgentBus(enable_persistence=True) if enable_agent_bus else None
    if enable_agent_bus:
        self.logger.info("Agent bus enabled")


def get_agent_bus_stats(self) -> Dict[str, Any]:
    """Get agent bus statistics."""
    if not hasattr(self, "agent_bus") or self.agent_bus is None:
        return {"enabled": False}

    return {
        "enabled": True,
        "agents": self.agent_bus.list_agents(),
        "message_history_size": len(self.agent_bus._message_history),
    }


# Monkey-patch methods
AgentOrchestrator.get_agent_bus_stats = get_agent_bus_stats
AgentOrchestrator.__init__ = __new_init__
