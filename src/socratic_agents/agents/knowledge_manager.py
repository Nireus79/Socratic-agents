"""Knowledge Manager Agent - Manages knowledge base and document organization."""

from typing import Any, Dict, Optional

from .base import BaseAgent


class KnowledgeManager(BaseAgent):
    """Agent that manages knowledge base, documents, and retrieval."""

    def __init__(self, llm_client: Optional[Any] = None):
        """Initialize the Knowledge Manager."""
        super().__init__(name="KnowledgeManager", llm_client=llm_client)
        self.knowledge_base: Dict[str, Any] = {}
        self.document_count = 0

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process knowledge management requests."""
        action = request.get("action", "list")
        if action == "add":
            return self.add_document(request.get("document"), request.get("metadata"))  # type: ignore[arg-type]
        elif action == "search":
            return self.search_documents(request.get("query"))  # type: ignore[arg-type]
        elif action == "list":
            return self.list_documents()
        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    def add_document(self, document: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Add a document to the knowledge base."""
        if not document:
            return {"status": "error", "message": "Document content required"}
        doc_id = f"doc_{self.document_count + 1}"
        self.knowledge_base[doc_id] = {"content": document, "metadata": metadata or {}}
        self.document_count += 1
        return {
            "status": "success",
            "agent": self.name,
            "document_id": doc_id,
            "total_documents": self.document_count,
        }

    def search_documents(self, query: str) -> Dict[str, Any]:
        """Search documents by query."""
        if not query:
            return {"status": "error", "message": "Query required"}
        results = [
            {"id": doc_id, "content": doc["content"][:200]}
            for doc_id, doc in self.knowledge_base.items()
            if query.lower() in doc["content"].lower()
        ]
        return {
            "status": "success",
            "agent": self.name,
            "query": query,
            "results_count": len(results),
            "results": results,
        }

    def list_documents(self) -> Dict[str, Any]:
        """List all documents in knowledge base."""
        return {
            "status": "success",
            "agent": self.name,
            "total_documents": self.document_count,
            "documents": list(self.knowledge_base.keys()),
        }
