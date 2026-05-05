"""
Abstract base classes for agent services.

Defines the interfaces that agents depend on. Implementations can be provided
for both local (orchestrator-based) and distributed (API-based) scenarios.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional


class EventEmitterService(ABC):
    """Abstract service for event emission and listening."""

    @abstractmethod
    def on(self, event_type: str, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Register a listener for an event type."""
        pass

    @abstractmethod
    def off(self, event_type: str, callback: Callable) -> None:
        """Remove a listener for an event type."""
        pass

    @abstractmethod
    def emit(self, event_type: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Emit an event to all registered listeners."""
        pass


class DatabaseService(ABC):
    """Abstract service for database operations."""

    @abstractmethod
    def load_user(self, user_id: str) -> Optional[Any]:
        """Load a user by ID."""
        pass

    @abstractmethod
    def save_user(self, user: Any) -> bool:
        """Save a user."""
        pass

    @abstractmethod
    def get_project(self, project_id: str) -> Optional[Any]:
        """Get a project by ID."""
        pass

    @abstractmethod
    def save_project(self, project: Any) -> bool:
        """Save a project."""
        pass

    @abstractmethod
    def get_project_notes(self, project_id: str) -> List[Any]:
        """Get notes for a project."""
        pass

    @abstractmethod
    def save_note(self, project_id: str, note: Any) -> bool:
        """Save a note for a project."""
        pass

    @property
    @abstractmethod
    def db_path(self) -> str:
        """Get the database path."""
        pass


class LLMService(ABC):
    """Abstract service for LLM operations."""

    @abstractmethod
    def generate_response(
        self, prompt: str, context: Optional[str] = None, **kwargs
    ) -> str:
        """Generate a response from the LLM."""
        pass

    @abstractmethod
    def generate_artifact(
        self, context: str, artifact_type: str, auth_method: str = "api_key", **kwargs
    ) -> str:
        """Generate an artifact (code, document, etc.)."""
        pass

    @abstractmethod
    def generate_documentation(
        self, project: Any, artifact: Optional[str] = None, artifact_type: str = "code", **kwargs
    ) -> str:
        """Generate documentation."""
        pass

    @abstractmethod
    def generate_question(
        self, project: Any, context: Optional[str] = None, **kwargs
    ) -> str:
        """Generate a question."""
        pass


class VectorDatabaseService(ABC):
    """Abstract service for vector database operations."""

    @abstractmethod
    def search_similar(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        pass

    @abstractmethod
    def add_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Add text to the vector database."""
        pass

    @abstractmethod
    def delete_by_metadata(self, metadata: Dict[str, Any]) -> bool:
        """Delete entries by metadata."""
        pass


class ConfigService(ABC):
    """Abstract service for configuration."""

    @property
    @abstractmethod
    def data_dir(self) -> str:
        """Get the data directory."""
        pass

    @property
    @abstractmethod
    def api_key(self) -> Optional[str]:
        """Get the API key."""
        pass

    @property
    @abstractmethod
    def claude_model(self) -> str:
        """Get the Claude model name."""
        pass

    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        pass


class ServiceRegistry(ABC):
    """Abstract service for managing and accessing other services."""

    @abstractmethod
    def register(self, service_name: str, service: Any) -> None:
        """Register a service."""
        pass

    @abstractmethod
    def get_service(self, service_name: str) -> Optional[Any]:
        """Get a registered service."""
        pass

    @abstractmethod
    def list_services(self) -> List[str]:
        """List all registered service names."""
        pass
