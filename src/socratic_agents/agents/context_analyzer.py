"""Context Analyzer Agent - Context understanding and analysis."""

from typing import Any, Dict, Optional

from .base import BaseAgent


class ContextAnalyzer(BaseAgent):
    """Agent that analyzes and understands context."""

    def __init__(self, llm_client: Optional[Any] = None):
        """Initialize the Context Analyzer."""
        super().__init__(name="ContextAnalyzer", llm_client=llm_client)
        self.contexts: Dict[str, Any] = {}

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process context analysis requests."""
        action = request.get("action", "analyze")
        if action == "analyze":
            return self.analyze_context(request.get("content"))  # type: ignore[arg-type]
        elif action == "store":
            return self.store_context(request.get("name"), request.get("content"))  # type: ignore[arg-type]
        elif action == "retrieve":
            return self.retrieve_context(request.get("name"))  # type: ignore[arg-type]
        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    def analyze_context(self, content: str) -> Dict[str, Any]:
        """Analyze content context."""
        if not content:
            return {"status": "error", "message": "Content required"}
        keywords = content.split()[:5]
        return {
            "status": "success",
            "agent": self.name,
            "keywords": keywords,
            "content_length": len(content),
            "word_count": len(keywords),
        }

    def store_context(self, name: str, content: str) -> Dict[str, Any]:
        """Store a context."""
        if not name or not content:
            return {"status": "error", "message": "Name and content required"}
        self.contexts[name] = content
        return {
            "status": "success",
            "agent": self.name,
            "context_stored": name,
            "contexts_count": len(self.contexts),
        }

    def retrieve_context(self, name: str) -> Dict[str, Any]:
        """Retrieve a stored context."""
        if not name:
            return {"status": "error", "message": "Name required"}
        if name not in self.contexts:
            return {"status": "error", "message": f"Context '{name}' not found"}
        return {"status": "success", "agent": self.name, "context": self.contexts[name]}
