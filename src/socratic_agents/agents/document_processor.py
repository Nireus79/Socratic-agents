"""Document Processor Agent - Document parsing and processing."""

from typing import Any, Dict, Optional, List
from .base import BaseAgent


class DocumentProcessor(BaseAgent):
    """Agent that processes various document types."""

    def __init__(self, llm_client: Optional[Any] = None):
        """Initialize the Document Processor."""
        super().__init__(name="DocumentProcessor", llm_client=llm_client)
        self.documents: List[Dict[str, Any]] = []
        self.supported_formats = ["txt", "pdf", "md", "json"]

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process document requests."""
        action = request.get("action", "parse")
        if action == "parse":
            return self.parse_document(request.get("content"), request.get("format", "txt"))
        elif action == "extract":
            return self.extract_text(request.get("content"))
        elif action == "list":
            return self.list_documents()
        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    def parse_document(self, content: str, format: str) -> Dict[str, Any]:
        """Parse a document."""
        if not content:
            return {"status": "error", "message": "Content required"}
        if format not in self.supported_formats:
            return {"status": "error", "message": f"Unsupported format: {format}"}
        doc = {"content": content, "format": format, "lines": len(content.split("\n"))}
        self.documents.append(doc)
        return {"status": "success", "agent": self.name, "format": format, "documents_processed": len(self.documents)}

    def extract_text(self, content: str) -> Dict[str, Any]:
        """Extract text from content."""
        if not content:
            return {"status": "error", "message": "Content required"}
        lines = content.split("\n")
        paragraphs = [l for l in lines if l.strip()]
        return {"status": "success", "agent": self.name, "text_extracted": True, "paragraphs": len(paragraphs), "lines": len(lines)}

    def list_documents(self) -> Dict[str, Any]:
        """List processed documents."""
        return {"status": "success", "agent": self.name, "documents_count": len(self.documents), "supported_formats": self.supported_formats}
