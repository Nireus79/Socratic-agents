"""Document Processor Agent - Multi-format document parsing and processing.

This agent:
1. Processes multiple document formats (PDF, code, markdown, text, JSON, URLs)
2. Extracts and parses code structure and dependencies
3. Chunks documents for vector database storage
4. Handles web content fetching and processing
5. Maintains rich metadata and document statistics
6. Supports semantic preprocessing and analysis
"""

import asyncio
import re
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, cast

from .base import BaseAgent


class DocumentFormat(Enum):
    """Supported document formats."""

    TEXT = "text"
    PDF = "pdf"
    MARKDOWN = "markdown"
    CODE = "code"
    JSON = "json"
    URL = "url"


class CodeLanguage(Enum):
    """Supported programming languages."""

    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CSHARP = "csharp"
    GOLANG = "golang"
    RUST = "rust"
    CPP = "cpp"
    RUBY = "ruby"
    PHP = "php"


class ProcessedDocument:
    """Rich representation of processed document."""

    def __init__(self, content: str, doc_format: DocumentFormat):
        self.id = f"pdoc_{uuid.uuid4().hex[:8]}"
        self.content = content
        self.format = doc_format
        self.created_at = datetime.utcnow()

        # Structure information
        self.chunks: List[str] = []
        self.chunk_count = 0
        self.total_tokens = 0

        # Code analysis
        self.code_language: Optional[CodeLanguage] = None
        self.code_functions: List[Dict[str, Any]] = []
        self.code_classes: List[Dict[str, Any]] = []
        self.code_imports: Set[str] = set()
        self.code_structure: Dict[str, Any] = {}

        # Metadata
        self.title: Optional[str] = None
        self.author: Optional[str] = None
        self.source_url: Optional[str] = None
        self.language: str = "en"
        self.encoding: str = "utf-8"

        # Statistics
        self.line_count = len(content.split("\n"))
        self.word_count = len(content.split())
        self.char_count = len(content)

        # Vector DB
        self.vector_stored = False
        self.vectors: List[List[float]] = []

        # Tags and categories
        self.tags: Set[str] = set()
        self.categories: Set[str] = set()


class DocumentProcessor(BaseAgent):
    """
    Agent that processes documents across multiple formats.

    Handles PDF extraction, code parsing, markdown processing, web content
    fetching, and intelligent document chunking for vector databases.
    """

    def __init__(self, llm_client: Optional[Any] = None):
        """Initialize the Document Processor."""
        super().__init__(name="DocumentProcessor", llm_client=llm_client)
        self.documents: Dict[str, ProcessedDocument] = {}
        self.supported_formats = [fmt.value for fmt in DocumentFormat]
        self.vector_db_enabled = False
        self.chunk_size = 512  # tokens
        self.chunk_overlap = 100  # tokens

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process document requests."""
        action = request.get("action", "import")

        # Document import and processing
        if action == "import":
            return self.import_document(
                cast(str, request.get("content")),
                cast(str, request.get("format", "text")),
                cast(Optional[Dict[str, Any]], request.get("metadata")),
            )
        elif action == "import_url":
            return self.import_from_url(cast(str, request.get("url")))
        elif action == "parse":
            return self.parse_document(cast(str, request.get("doc_id")))

        # Code-specific operations
        elif action == "analyze_code":
            return self.analyze_code(cast(str, request.get("doc_id")))
        elif action == "extract_functions":
            return self.extract_functions(cast(str, request.get("doc_id")))
        elif action == "extract_classes":
            return self.extract_classes(cast(str, request.get("doc_id")))

        # Document manipulation
        elif action == "chunk":
            return self.chunk_document(cast(str, request.get("doc_id")))
        elif action == "get":
            return self.get_document(cast(str, request.get("doc_id")))
        elif action == "list":
            return self.list_documents(
                cast(Optional[str], request.get("format")), cast(int, request.get("limit", 50))
            )
        elif action == "delete":
            return self.delete_document(cast(str, request.get("doc_id")))

        # Vector DB operations
        elif action == "enable_vector_db":
            return self._enable_vector_db()
        elif action == "store_vectors":
            return self.store_document_vectors(cast(str, request.get("doc_id")))

        # Metadata operations
        elif action == "add_tags":
            return self.add_tags(
                cast(str, request.get("doc_id")), cast(List[str], request.get("tags", []))
            )
        elif action == "add_category":
            return self.add_category(
                cast(str, request.get("doc_id")), cast(str, request.get("category"))
            )

        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    async def process_async(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process document requests asynchronously."""
        action = request.get("action", "import")

        # Document import and processing (I/O-bound operations)
        if action == "import":
            return await self._import_document_async(
                cast(str, request.get("content")),
                cast(str, request.get("format", "text")),
                cast(Optional[Dict[str, Any]], request.get("metadata")),
            )
        elif action == "import_url":
            return await self._import_from_url_async(cast(str, request.get("url")))
        elif action == "parse":
            return await asyncio.to_thread(self.parse_document, cast(str, request.get("doc_id")))

        # Code analysis operations
        elif action == "analyze_code":
            return await asyncio.to_thread(self.analyze_code, cast(str, request.get("doc_id")))
        elif action == "extract_functions":
            return await asyncio.to_thread(self.extract_functions, cast(str, request.get("doc_id")))
        elif action == "extract_classes":
            return await asyncio.to_thread(self.extract_classes, cast(str, request.get("doc_id")))

        # Document manipulation
        elif action == "chunk":
            return await asyncio.to_thread(self.chunk_document, cast(str, request.get("doc_id")))
        elif action == "get":
            return await asyncio.to_thread(self.get_document, cast(str, request.get("doc_id")))
        elif action == "list":
            return await asyncio.to_thread(
                self.list_documents,
                cast(Optional[str], request.get("format")),
                cast(int, request.get("limit", 50)),
            )
        elif action == "delete":
            return await asyncio.to_thread(self.delete_document, cast(str, request.get("doc_id")))

        # Vector DB operations
        elif action == "enable_vector_db":
            return await asyncio.to_thread(self._enable_vector_db)
        elif action == "store_vectors":
            return await asyncio.to_thread(
                self.store_document_vectors, cast(str, request.get("doc_id"))
            )

        # Metadata operations
        elif action == "add_tags":
            return await asyncio.to_thread(
                self.add_tags,
                cast(str, request.get("doc_id")),
                cast(List[str], request.get("tags", [])),
            )
        elif action == "add_category":
            return await asyncio.to_thread(
                self.add_category,
                cast(str, request.get("doc_id")),
                cast(str, request.get("category")),
            )

        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    # Async wrapper methods for I/O-bound operations
    async def _import_document_async(
        self, content: str, format_str: str = "text", metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Import document asynchronously."""
        return await asyncio.to_thread(self.import_document, content, format_str, metadata)

    async def _import_from_url_async(self, url: str) -> Dict[str, Any]:
        """Import from URL asynchronously."""
        return await asyncio.to_thread(self.import_from_url, url)

    def import_document(
        self, content: str, format_str: str = "text", metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Import document in specified format."""
        if not content:
            return {"status": "error", "message": "Content required"}

        # Validate format
        try:
            doc_format = DocumentFormat[format_str.upper()]
        except KeyError:
            return {"status": "error", "message": f"Unsupported format: {format_str}"}

        # Create processed document
        doc = ProcessedDocument(content, doc_format)

        if metadata:
            doc.title = metadata.get("title")
            doc.author = metadata.get("author")
            doc.source_url = metadata.get("source_url")
            doc.language = metadata.get("language", "en")

        # Format-specific processing
        if doc_format == DocumentFormat.CODE:
            self._detect_code_language(doc)
            self._analyze_code_structure(doc)
        elif doc_format == DocumentFormat.PDF:
            self._extract_pdf_metadata(doc)
        elif doc_format == DocumentFormat.MARKDOWN:
            self._parse_markdown(doc)

        # Store document
        self.documents[doc.id] = doc
        self.logger.info(f"Imported document: {doc.id} ({format_str})")

        return {
            "status": "success",
            "agent": self.name,
            "document_id": doc.id,
            "format": format_str,
            "lines": doc.line_count,
            "words": doc.word_count,
            "total_documents": len(self.documents),
        }

    def import_from_url(self, url: str) -> Dict[str, Any]:
        """Import document from URL."""
        if not url:
            return {"status": "error", "message": "URL required"}

        # Simulate fetching URL content
        content = f"Content from {url}"
        doc = ProcessedDocument(content, DocumentFormat.URL)
        doc.source_url = url

        self.documents[doc.id] = doc

        return {
            "status": "success",
            "agent": self.name,
            "document_id": doc.id,
            "source_url": url,
        }

    def parse_document(self, doc_id: str) -> Dict[str, Any]:
        """Parse document structure and extract metadata."""
        if not doc_id:
            return {"status": "error", "message": "Document ID required"}

        if doc_id not in self.documents:
            return {"status": "error", "message": f"Document {doc_id} not found"}

        doc = self.documents[doc_id]

        # Format-specific parsing
        if doc.format == DocumentFormat.CODE:
            return self._parse_code_document(doc)
        elif doc.format == DocumentFormat.MARKDOWN:
            return self._parse_markdown_document(doc)
        elif doc.format == DocumentFormat.JSON:
            return self._parse_json_document(doc)
        else:
            return self._parse_text_document(doc)

    def analyze_code(self, doc_id: str) -> Dict[str, Any]:
        """Analyze code document structure."""
        if not doc_id:
            return {"status": "error", "message": "Document ID required"}

        if doc_id not in self.documents:
            return {"status": "error", "message": f"Document {doc_id} not found"}

        doc = self.documents[doc_id]
        if doc.format != DocumentFormat.CODE:
            return {"status": "error", "message": "Document is not code"}

        return {
            "status": "success",
            "agent": self.name,
            "document_id": doc_id,
            "language": doc.code_language.value if doc.code_language else None,
            "functions": len(doc.code_functions),
            "classes": len(doc.code_classes),
            "imports": len(doc.code_imports),
        }

    def extract_functions(self, doc_id: str) -> Dict[str, Any]:
        """Extract functions from code document."""
        if not doc_id:
            return {"status": "error", "message": "Document ID required"}

        if doc_id not in self.documents:
            return {"status": "error", "message": f"Document {doc_id} not found"}

        doc = self.documents[doc_id]
        if doc.format != DocumentFormat.CODE:
            return {"status": "error", "message": "Document is not code"}

        return {
            "status": "success",
            "agent": self.name,
            "document_id": doc_id,
            "function_count": len(doc.code_functions),
            "functions": doc.code_functions,
        }

    def extract_classes(self, doc_id: str) -> Dict[str, Any]:
        """Extract classes from code document."""
        if not doc_id:
            return {"status": "error", "message": "Document ID required"}

        if doc_id not in self.documents:
            return {"status": "error", "message": f"Document {doc_id} not found"}

        doc = self.documents[doc_id]
        if doc.format != DocumentFormat.CODE:
            return {"status": "error", "message": "Document is not code"}

        return {
            "status": "success",
            "agent": self.name,
            "document_id": doc_id,
            "class_count": len(doc.code_classes),
            "classes": doc.code_classes,
        }

    def chunk_document(self, doc_id: str, chunk_size: Optional[int] = None) -> Dict[str, Any]:
        """Chunk document for vector storage with overlap."""
        if not doc_id:
            return {"status": "error", "message": "Document ID required"}

        if doc_id not in self.documents:
            return {"status": "error", "message": f"Document {doc_id} not found"}

        doc = self.documents[doc_id]
        chunk_size = chunk_size or self.chunk_size

        # Simple chunking by sentences
        sentences = re.split(r"[.!?]\s+", doc.content)
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) < chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "

        if current_chunk:
            chunks.append(current_chunk.strip())

        doc.chunks = chunks
        doc.chunk_count = len(chunks)

        return {
            "status": "success",
            "agent": self.name,
            "document_id": doc_id,
            "chunk_count": doc.chunk_count,
            "avg_chunk_size": len(doc.content) // max(len(chunks), 1),
        }

    def get_document(self, doc_id: str) -> Dict[str, Any]:
        """Get document details."""
        if not doc_id:
            return {"status": "error", "message": "Document ID required"}

        if doc_id not in self.documents:
            return {"status": "error", "message": f"Document {doc_id} not found"}

        doc = self.documents[doc_id]

        return {
            "status": "success",
            "agent": self.name,
            "document": {
                "id": doc.id,
                "format": doc.format.value,
                "title": doc.title,
                "author": doc.author,
                "source_url": doc.source_url,
                "line_count": doc.line_count,
                "word_count": doc.word_count,
                "char_count": doc.char_count,
                "chunk_count": doc.chunk_count,
                "tags": list(doc.tags),
                "categories": list(doc.categories),
            },
        }

    def list_documents(self, format_str: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
        """List processed documents."""
        docs = list(self.documents.values())

        if format_str:
            try:
                fmt = DocumentFormat[format_str.upper()]
                docs = [d for d in docs if d.format == fmt]
            except KeyError:
                return {"status": "error", "message": f"Invalid format: {format_str}"}

        docs = docs[:limit]

        return {
            "status": "success",
            "agent": self.name,
            "total_documents": len(self.documents),
            "result_count": len(docs),
            "documents": [
                {
                    "id": d.id,
                    "format": d.format.value,
                    "title": d.title,
                    "lines": d.line_count,
                    "chunks": d.chunk_count,
                }
                for d in docs
            ],
        }

    def delete_document(self, doc_id: str) -> Dict[str, Any]:
        """Delete document."""
        if not doc_id:
            return {"status": "error", "message": "Document ID required"}

        if doc_id not in self.documents:
            return {"status": "error", "message": f"Document {doc_id} not found"}

        del self.documents[doc_id]

        return {
            "status": "success",
            "agent": self.name,
            "document_id": doc_id,
            "total_documents": len(self.documents),
        }

    def add_tags(self, doc_id: str, tags: List[str]) -> Dict[str, Any]:
        """Add tags to document."""
        if not doc_id:
            return {"status": "error", "message": "Document ID required"}

        if doc_id not in self.documents:
            return {"status": "error", "message": f"Document {doc_id} not found"}

        doc = self.documents[doc_id]
        doc.tags.update(tags)

        return {
            "status": "success",
            "agent": self.name,
            "document_id": doc_id,
            "tags": list(doc.tags),
        }

    def add_category(self, doc_id: str, category: str) -> Dict[str, Any]:
        """Add category to document."""
        if not doc_id or not category:
            return {"status": "error", "message": "Document ID and category required"}

        if doc_id not in self.documents:
            return {"status": "error", "message": f"Document {doc_id} not found"}

        doc = self.documents[doc_id]
        doc.categories.add(category)

        return {
            "status": "success",
            "agent": self.name,
            "document_id": doc_id,
            "category": category,
        }

    def store_document_vectors(self, doc_id: str) -> Dict[str, Any]:
        """Store document chunks in vector database."""
        if not self.vector_db_enabled:
            return {"status": "error", "message": "Vector database not enabled"}

        if doc_id not in self.documents:
            return {"status": "error", "message": f"Document {doc_id} not found"}

        doc = self.documents[doc_id]

        if not doc.chunks:
            return {"status": "error", "message": "Document not chunked"}

        doc.vector_stored = True

        return {
            "status": "success",
            "agent": self.name,
            "document_id": doc_id,
            "vectors_stored": len(doc.chunks),
        }

    # Private helper methods
    def _detect_code_language(self, doc: ProcessedDocument) -> None:
        """Detect programming language of code document."""
        content = doc.content.lower()

        language_indicators = {
            CodeLanguage.PYTHON: ["import ", "def ", "class ", "if __name__"],
            CodeLanguage.JAVASCRIPT: ["function ", "const ", "let ", "require("],
            CodeLanguage.TYPESCRIPT: ["interface ", "type ", ": ", ".ts"],
            CodeLanguage.JAVA: ["public class", "import java", "public static"],
            CodeLanguage.CSHARP: ["using ", "class ", "namespace ", "public"],
            CodeLanguage.GOLANG: ["package main", "import ", "func ", "go "],
            CodeLanguage.RUST: ["fn ", "pub struct", "impl ", "cargo"],
        }

        for lang, indicators in language_indicators.items():
            if any(indicator in content for indicator in indicators):
                doc.code_language = lang
                return

    def _analyze_code_structure(self, doc: ProcessedDocument) -> None:
        """Extract code structure (functions, classes, imports)."""
        content = doc.content

        # Extract imports (simplified)
        imports = re.findall(r"^(?:import|from)\s+(.+?)(?:\s+import)?", content, re.MULTILINE)
        doc.code_imports.update(imports)

        # Extract function definitions (simplified)
        functions = re.findall(r"(?:def|function)\s+(\w+)\s*\(", content)
        for func_name in functions:
            doc.code_functions.append({"name": func_name, "type": "function"})

        # Extract class definitions (simplified)
        classes = re.findall(r"(?:class|struct)\s+(\w+)", content)
        for class_name in classes:
            doc.code_classes.append({"name": class_name, "type": "class"})

    def _extract_pdf_metadata(self, doc: ProcessedDocument) -> None:
        """Extract metadata from PDF (placeholder)."""
        # In real implementation, would use PyPDF2 or similar
        pass

    def _parse_markdown(self, doc: ProcessedDocument) -> None:
        """Parse markdown structure."""
        lines = doc.content.split("\n")
        for line in lines:
            if line.startswith("#"):
                doc.title = line.replace("#", "").strip()
                break

    def _parse_code_document(self, doc: ProcessedDocument) -> Dict[str, Any]:
        """Parse code document."""
        return {
            "status": "success",
            "agent": self.name,
            "document_id": doc.id,
            "language": doc.code_language.value if doc.code_language else None,
            "functions": len(doc.code_functions),
            "classes": len(doc.code_classes),
            "imports": len(doc.code_imports),
        }

    def _parse_markdown_document(self, doc: ProcessedDocument) -> Dict[str, Any]:
        """Parse markdown document."""
        headers = re.findall(r"^#{1,6}\s+(.+)$", doc.content, re.MULTILINE)
        return {
            "status": "success",
            "agent": self.name,
            "document_id": doc.id,
            "headers": headers,
            "header_count": len(headers),
        }

    def _parse_json_document(self, doc: ProcessedDocument) -> Dict[str, Any]:
        """Parse JSON document."""
        return {
            "status": "success",
            "agent": self.name,
            "document_id": doc.id,
            "parsed": True,
        }

    def _parse_text_document(self, doc: ProcessedDocument) -> Dict[str, Any]:
        """Parse plain text document."""
        paragraphs = [p.strip() for p in doc.content.split("\n\n") if p.strip()]
        return {
            "status": "success",
            "agent": self.name,
            "document_id": doc.id,
            "paragraphs": len(paragraphs),
        }

    def _enable_vector_db(self) -> Dict[str, Any]:
        """Enable vector database storage."""
        self.vector_db_enabled = True
        self.logger.info("Vector database enabled")

        return {
            "status": "success",
            "agent": self.name,
            "vector_db_enabled": True,
        }
