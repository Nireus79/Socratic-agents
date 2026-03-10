"""Document Context Analyzer Agent - Document semantic analysis."""

from typing import Any, Dict, List, Optional

from .base import BaseAgent


class DocumentContextAnalyzer(BaseAgent):
    """Agent that analyzes document context and semantics."""

    def __init__(self, llm_client: Optional[Any] = None):
        """Initialize the Document Context Analyzer."""
        super().__init__(name="DocumentContextAnalyzer", llm_client=llm_client)
        self.analyzed_docs: List[Dict[str, Any]] = []

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process document context analysis requests."""
        action = request.get("action", "analyze")
        if action == "analyze":
            return self.analyze_document(request.get("document"))  # type: ignore[arg-type]
        elif action == "extract_context":
            return self.extract_context(request.get("document"))  # type: ignore[arg-type]
        elif action == "list":
            return self.list_analyzed()
        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    def analyze_document(self, document: str) -> Dict[str, Any]:
        """Analyze document context."""
        if not document:
            return {"status": "error", "message": "Document required"}
        analysis = {
            "doc_length": len(document),
            "paragraphs": len(document.split("\n")),
            "sentences": document.count("."),
        }
        self.analyzed_docs.append(analysis)
        return {
            "status": "success",
            "agent": self.name,
            "analysis": analysis,
            "documents_analyzed": len(self.analyzed_docs),
        }

    def extract_context(self, document: str) -> Dict[str, Any]:
        """Extract context from document."""
        if not document:
            return {"status": "error", "message": "Document required"}
        lines = document.split("\n")
        context_lines = [line for line in lines if len(line.strip()) > 5]
        return {
            "status": "success",
            "agent": self.name,
            "context_extracted": len(context_lines),
            "context_density": round(len(context_lines) / max(len(lines), 1) * 100, 1),
        }

    def list_analyzed(self) -> Dict[str, Any]:
        """List analyzed documents."""
        return {
            "status": "success",
            "agent": self.name,
            "documents_analyzed": len(self.analyzed_docs),
            "total_length": sum(d.get("doc_length", 0) for d in self.analyzed_docs),
        }
