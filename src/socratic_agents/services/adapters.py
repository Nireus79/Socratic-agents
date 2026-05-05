"""
Service adapters that wrap an orchestrator for backward compatibility.

These adapters implement the abstract service interfaces using an existing
orchestrator instance, allowing gradual migration to service injection.
"""

from typing import Any, Callable, Dict, List, Optional

from socratic_agents.services.base import (
    ConfigService,
    DatabaseService,
    EventEmitterService,
    LLMService,
    VectorDatabaseService,
)


class OrchestratorEventEmitterAdapter(EventEmitterService):
    """Wraps orchestrator's event_emitter to implement EventEmitterService."""

    def __init__(self, orchestrator: Any):
        self.orchestrator = orchestrator

    def on(self, event_type: str, callback: Callable[[Dict[str, Any]], None]) -> None:
        if hasattr(self.orchestrator, "event_emitter"):
            self.orchestrator.event_emitter.on(event_type, callback)

    def off(self, event_type: str, callback: Callable) -> None:
        if hasattr(self.orchestrator, "event_emitter"):
            self.orchestrator.event_emitter.off(event_type, callback)

    def emit(self, event_type: str, data: Optional[Dict[str, Any]] = None) -> None:
        if hasattr(self.orchestrator, "event_emitter"):
            self.orchestrator.event_emitter.emit(event_type, data)


class OrchestratorDatabaseAdapter(DatabaseService):
    """Wraps orchestrator's database to implement DatabaseService."""

    def __init__(self, orchestrator: Any):
        self.orchestrator = orchestrator
        self._database = orchestrator.database if hasattr(orchestrator, "database") else None

    def load_user(self, user_id: str) -> Optional[Any]:
        if self._database and hasattr(self._database, "load_user"):
            return self._database.load_user(user_id)
        return None

    def save_user(self, user: Any) -> bool:
        if self._database and hasattr(self._database, "save_user"):
            return self._database.save_user(user)
        return False

    def get_project(self, project_id: str) -> Optional[Any]:
        if self._database and hasattr(self._database, "get_project"):
            return self._database.get_project(project_id)
        return None

    def save_project(self, project: Any) -> bool:
        if self._database and hasattr(self._database, "save_project"):
            return self._database.save_project(project)
        return False

    def get_project_notes(self, project_id: str) -> List[Any]:
        if self._database and hasattr(self._database, "get_project_notes"):
            return self._database.get_project_notes(project_id)
        return []

    def save_note(self, project_id: str, note: Any) -> bool:
        if self._database and hasattr(self._database, "save_note"):
            return self._database.save_note(project_id, note)
        return False

    @property
    def db_path(self) -> str:
        if self._database and hasattr(self._database, "db_path"):
            return self._database.db_path
        return ""


class OrchestratorLLMAdapter(LLMService):
    """Wraps orchestrator's claude_client to implement LLMService."""

    def __init__(self, orchestrator: Any):
        self.orchestrator = orchestrator
        self._llm = orchestrator.claude_client if hasattr(orchestrator, "claude_client") else None

    def generate_response(
        self, prompt: str, context: Optional[str] = None, **kwargs
    ) -> str:
        if self._llm and hasattr(self._llm, "generate_response"):
            return self._llm.generate_response(prompt, context=context, **kwargs)
        return ""

    def generate_artifact(
        self, context: str, artifact_type: str, auth_method: str = "api_key", **kwargs
    ) -> str:
        if self._llm and hasattr(self._llm, "generate_artifact"):
            return self._llm.generate_artifact(context, artifact_type, auth_method, **kwargs)
        return ""

    def generate_documentation(
        self, project: Any, artifact: Optional[str] = None, artifact_type: str = "code", **kwargs
    ) -> str:
        if self._llm and hasattr(self._llm, "generate_documentation"):
            return self._llm.generate_documentation(project, artifact, artifact_type, **kwargs)
        return ""

    def generate_question(
        self, project: Any, context: Optional[str] = None, **kwargs
    ) -> str:
        if self._llm and hasattr(self._llm, "generate_question"):
            return self._llm.generate_question(project, context=context, **kwargs)
        return ""


class OrchestratorVectorDBAdapter(VectorDatabaseService):
    """Wraps orchestrator's vector_db to implement VectorDatabaseService."""

    def __init__(self, orchestrator: Any):
        self.orchestrator = orchestrator
        self._vector_db = orchestrator.vector_db if hasattr(orchestrator, "vector_db") else None

    def search_similar(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if self._vector_db and hasattr(self._vector_db, "search_similar"):
            return self._vector_db.search_similar(query, top_k=top_k)
        return []

    def add_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        if self._vector_db and hasattr(self._vector_db, "add_text"):
            return self._vector_db.add_text(text, metadata=metadata)
        return False

    def delete_by_metadata(self, metadata: Dict[str, Any]) -> bool:
        if self._vector_db and hasattr(self._vector_db, "delete_by_metadata"):
            return self._vector_db.delete_by_metadata(metadata)
        return False


class OrchestratorConfigAdapter(ConfigService):
    """Wraps orchestrator's config to implement ConfigService."""

    def __init__(self, orchestrator: Any):
        self.orchestrator = orchestrator
        self._config = orchestrator.config if hasattr(orchestrator, "config") else None

    @property
    def data_dir(self) -> str:
        if self._config and hasattr(self._config, "data_dir"):
            return str(self._config.data_dir)
        return ""

    @property
    def api_key(self) -> Optional[str]:
        if self._config and hasattr(self._config, "api_key"):
            return self._config.api_key
        return None

    @property
    def claude_model(self) -> str:
        if self._config and hasattr(self._config, "claude_model"):
            return self._config.claude_model
        return "claude-haiku-4-5-20251001"

    def get(self, key: str, default: Any = None) -> Any:
        if self._config and hasattr(self._config, "get"):
            return self._config.get(key, default)
        return default


def create_service_adapters(orchestrator: Any) -> Dict[str, Any]:
    """
    Create all service adapters from an orchestrator instance.

    Args:
        orchestrator: An AgentOrchestrator instance

    Returns:
        Dictionary of service_name -> service_adapter
    """
    return {
        "event_emitter": OrchestratorEventEmitterAdapter(orchestrator),
        "database": OrchestratorDatabaseAdapter(orchestrator),
        "llm": OrchestratorLLMAdapter(orchestrator),
        "vector_db": OrchestratorVectorDBAdapter(orchestrator),
        "config": OrchestratorConfigAdapter(orchestrator),
    }
