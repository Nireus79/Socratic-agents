"""
Default service implementations for standalone use.

Provides basic implementations of services for projects that don't have
their own database, LLM, or vector DB implementations.
"""

import logging
from typing import Any, Callable, Dict, List, Optional

from socratic_agents.services.base import (
    ConfigService,
    DatabaseService,
    EventEmitterService,
    LLMService,
    VectorDatabaseService,
)


class DefaultEventEmitterService(EventEmitterService):
    """Basic in-memory event emitter service."""

    def __init__(self):
        """Initialize event emitter."""
        self._listeners: Dict[str, List[Callable]] = {}
        self.logger = logging.getLogger("socratic_agents.event_emitter")

    def on(self, event_type: str, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Register a listener."""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)
        self.logger.debug(f"Registered listener for {event_type}")

    def off(self, event_type: str, callback: Callable) -> None:
        """Remove a listener."""
        if event_type in self._listeners and callback in self._listeners[event_type]:
            self._listeners[event_type].remove(callback)
            self.logger.debug(f"Removed listener for {event_type}")

    def emit(self, event_type: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Emit an event."""
        if data is None:
            data = {}

        if event_type in self._listeners:
            for callback in self._listeners[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    self.logger.error(f"Error in event listener for {event_type}: {e}")


class DefaultConfigService(ConfigService):
    """Basic configuration service."""

    def __init__(self, data_dir: str = ".", api_key: Optional[str] = None, claude_model: str = "claude-haiku-4-5-20251001"):
        """
        Initialize config service.

        Args:
            data_dir: Data directory path
            api_key: Optional API key
            claude_model: Claude model name
        """
        self._data_dir = data_dir
        self._api_key = api_key
        self._claude_model = claude_model
        self._config: Dict[str, Any] = {}

    @property
    def data_dir(self) -> str:
        """Get data directory."""
        return self._data_dir

    @property
    def api_key(self) -> Optional[str]:
        """Get API key."""
        return self._api_key

    @property
    def claude_model(self) -> str:
        """Get Claude model."""
        return self._claude_model

    def get(self, key: str, default: Any = None) -> Any:
        """Get config value."""
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set config value."""
        self._config[key] = value


class DefaultDatabaseService(DatabaseService):
    """
    Stub database service that returns None/defaults.

    Replace with actual database service for production use.
    """

    def __init__(self):
        """Initialize stub database."""
        self.logger = logging.getLogger("socratic_agents.database")

    def load_user(self, user_id: str) -> Optional[Any]:
        """Load user - not implemented in stub."""
        self.logger.warning("DefaultDatabaseService.load_user() not implemented")
        return None

    def save_user(self, user: Any) -> bool:
        """Save user - not implemented in stub."""
        self.logger.warning("DefaultDatabaseService.save_user() not implemented")
        return False

    def get_project(self, project_id: str) -> Optional[Any]:
        """Get project - not implemented in stub."""
        self.logger.warning("DefaultDatabaseService.get_project() not implemented")
        return None

    def save_project(self, project: Any) -> bool:
        """Save project - not implemented in stub."""
        self.logger.warning("DefaultDatabaseService.save_project() not implemented")
        return False

    def get_project_notes(self, project_id: str) -> List[Any]:
        """Get project notes - not implemented in stub."""
        self.logger.warning("DefaultDatabaseService.get_project_notes() not implemented")
        return []

    def save_note(self, project_id: str, note: Any) -> bool:
        """Save note - not implemented in stub."""
        self.logger.warning("DefaultDatabaseService.save_note() not implemented")
        return False

    @property
    def db_path(self) -> str:
        """Get database path - not implemented in stub."""
        return ""


class DefaultLLMService(LLMService):
    """
    Stub LLM service that requires actual API key and client.

    Replace with actual LLM service implementation.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize LLM service.

        Args:
            api_key: Anthropic API key
        """
        self.api_key = api_key
        self.logger = logging.getLogger("socratic_agents.llm")

    def generate_response(
        self, prompt: str, context: Optional[str] = None, **kwargs
    ) -> str:
        """Generate response - requires implementation."""
        if not self.api_key:
            self.logger.error("LLM service not configured (no API key)")
            return ""
        self.logger.warning("DefaultLLMService.generate_response() not fully implemented")
        return ""

    def generate_artifact(
        self, context: str, artifact_type: str, auth_method: str = "api_key", **kwargs
    ) -> str:
        """Generate artifact - requires implementation."""
        if not self.api_key:
            self.logger.error("LLM service not configured (no API key)")
            return ""
        self.logger.warning("DefaultLLMService.generate_artifact() not fully implemented")
        return ""

    def generate_documentation(
        self, project: Any, artifact: Optional[str] = None, artifact_type: str = "code", **kwargs
    ) -> str:
        """Generate documentation - requires implementation."""
        if not self.api_key:
            self.logger.error("LLM service not configured (no API key)")
            return ""
        self.logger.warning("DefaultLLMService.generate_documentation() not fully implemented")
        return ""

    def generate_question(
        self, project: Any, context: Optional[str] = None, **kwargs
    ) -> str:
        """Generate question - requires implementation."""
        if not self.api_key:
            self.logger.error("LLM service not configured (no API key)")
            return ""
        self.logger.warning("DefaultLLMService.generate_question() not fully implemented")
        return ""


class DefaultVectorDatabaseService(VectorDatabaseService):
    """
    Stub vector database service.

    Replace with actual vector database service implementation.
    """

    def __init__(self):
        """Initialize stub vector DB."""
        self.logger = logging.getLogger("socratic_agents.vector_db")

    def search_similar(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search similar - not implemented in stub."""
        self.logger.warning("DefaultVectorDatabaseService.search_similar() not implemented")
        return []

    def add_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Add text - not implemented in stub."""
        self.logger.warning("DefaultVectorDatabaseService.add_text() not implemented")
        return False

    def delete_by_metadata(self, metadata: Dict[str, Any]) -> bool:
        """Delete by metadata - not implemented in stub."""
        self.logger.warning("DefaultVectorDatabaseService.delete_by_metadata() not implemented")
        return False
