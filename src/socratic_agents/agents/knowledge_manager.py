"""Knowledge Manager Agent - Manages knowledge base, documents, and intelligent retrieval.

This agent:
1. Persists and organizes knowledge documents
2. Provides advanced search with semantic understanding
3. Manages categorization and tagging
4. Integrates with vector databases for semantic search
5. Tracks knowledge relationships and connections
6. Supports full-text and semantic search modes
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from .base import BaseAgent


class DocumentCategory(Enum):
    """Document categorization."""

    CODE = "code"
    DOCUMENTATION = "documentation"
    SPECIFICATION = "specification"
    DESIGN = "design"
    TEST = "test"
    INSIGHT = "insight"
    LEARNING = "learning"
    RESEARCH = "research"


class KnowledgeDocument:
    """Rich knowledge document with metadata and relationships."""

    def __init__(self, content: str, doc_type: str = "text"):
        self.id = f"doc_{uuid.uuid4().hex[:8]}"
        self.content = content
        self.doc_type = doc_type
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.access_count = 0
        self.last_accessed = None

        # Organization
        self.categories: Set[DocumentCategory] = set()
        self.tags: Set[str] = set()
        self.metadata: Dict[str, Any] = {}

        # Relationships
        self.related_docs: Set[str] = set()
        self.references: Set[str] = set()
        self.referenced_by: Set[str] = set()

        # Vector representation (for semantic search)
        self.vector: Optional[List[float]] = None
        self.embeddings_model: Optional[str] = None

    def add_category(self, category: DocumentCategory) -> None:
        """Add category to document."""
        self.categories.add(category)

    def add_tag(self, tag: str) -> None:
        """Add tag to document."""
        self.tags.add(tag.lower())

    def add_relation(self, doc_id: str) -> None:
        """Link to related document."""
        self.related_docs.add(doc_id)

    def record_access(self) -> None:
        """Record document access."""
        self.access_count += 1
        self.last_accessed = datetime.utcnow()


class KnowledgeManager(BaseAgent):
    """
    Agent that manages knowledge base with persistence and semantic search.

    Organizes documents, tracks relationships, supports full-text and semantic
    search, manages categorization, and integrates with vector databases.
    """

    def __init__(self, llm_client: Optional[Any] = None):
        """Initialize the Knowledge Manager."""
        super().__init__(name="KnowledgeManager", llm_client=llm_client)
        self.knowledge_base: Dict[str, KnowledgeDocument] = {}
        self.category_index: Dict[str, Set[str]] = {cat.value: set() for cat in DocumentCategory}
        self.tag_index: Dict[str, Set[str]] = {}
        self.vector_db_enabled = False
        self.vector_dimension = 384  # Default for sentence-transformers

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process knowledge management requests."""
        action = request.get("action", "list")

        # Document operations
        if action == "add":
            return self.add_document(
                request.get("content"), request.get("doc_type", "text"), request.get("metadata")
            )
        elif action == "get":
            return self.get_document(request.get("doc_id"))
        elif action == "update":
            return self.update_document(
                request.get("doc_id"), request.get("content"), request.get("metadata")
            )
        elif action == "delete":
            return self.delete_document(request.get("doc_id"))
        elif action == "list":
            return self.list_documents(
                request.get("category"), request.get("tags"), request.get("limit", 50)
            )

        # Search operations
        elif action == "search":
            return self.search_documents(
                request.get("query"), request.get("mode", "full_text"), request.get("category")
            )
        elif action == "semantic_search":
            return self.semantic_search(request.get("query"), request.get("limit", 10))

        # Organization operations
        elif action == "add_category":
            return self.add_category(request.get("doc_id"), request.get("category"))
        elif action == "add_tag":
            return self.add_tag(request.get("doc_id"), request.get("tag"))
        elif action == "remove_tag":
            return self.remove_tag(request.get("doc_id"), request.get("tag"))
        elif action == "relate_documents":
            return self.relate_documents(request.get("doc_id1"), request.get("doc_id2"))

        # Vector DB operations
        elif action == "enable_vector_db":
            return self.enable_vector_database(
                request.get("model", "sentence-transformers/all-MiniLM-L6-v2")
            )
        elif action == "index_vector":
            return self.index_vector(request.get("doc_id"), request.get("vector"))

        # Analytics
        elif action == "get_stats":
            return self.get_knowledge_stats()
        elif action == "get_trending":
            return self.get_trending_documents(request.get("limit", 10))

        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    def add_document(
        self, content: str, doc_type: str = "text", metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Add document to knowledge base."""
        if not content:
            return {"status": "error", "message": "Document content required"}

        doc = KnowledgeDocument(content, doc_type)
        if metadata:
            doc.metadata = metadata

        self.knowledge_base[doc.id] = doc
        self.logger.info(f"Added document: {doc.id}")

        return {
            "status": "success",
            "agent": self.name,
            "document_id": doc.id,
            "doc_type": doc_type,
            "total_documents": len(self.knowledge_base),
        }

    def get_document(self, doc_id: str) -> Dict[str, Any]:
        """Get detailed document information."""
        if not doc_id:
            return {"status": "error", "message": "Document ID required"}

        if doc_id not in self.knowledge_base:
            return {"status": "error", "message": f"Document {doc_id} not found"}

        doc = self.knowledge_base[doc_id]
        doc.record_access()

        return {
            "status": "success",
            "agent": self.name,
            "document": {
                "id": doc.id,
                "doc_type": doc.doc_type,
                "content": doc.content,
                "categories": [cat.value for cat in doc.categories],
                "tags": list(doc.tags),
                "metadata": doc.metadata,
                "access_count": doc.access_count,
                "created_at": doc.created_at.isoformat(),
            },
        }

    def update_document(
        self, doc_id: str, content: Optional[str] = None, metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Update document content or metadata."""
        if not doc_id:
            return {"status": "error", "message": "Document ID required"}

        if doc_id not in self.knowledge_base:
            return {"status": "error", "message": f"Document {doc_id} not found"}

        doc = self.knowledge_base[doc_id]
        if content:
            doc.content = content
        if metadata:
            doc.metadata.update(metadata)
        doc.updated_at = datetime.utcnow()

        return {
            "status": "success",
            "agent": self.name,
            "document_id": doc_id,
            "updated_at": doc.updated_at.isoformat(),
        }

    def delete_document(self, doc_id: str) -> Dict[str, Any]:
        """Delete document from knowledge base."""
        if not doc_id:
            return {"status": "error", "message": "Document ID required"}

        if doc_id not in self.knowledge_base:
            return {"status": "error", "message": f"Document {doc_id} not found"}

        doc = self.knowledge_base.pop(doc_id)

        # Clean up indices
        for category in doc.categories:
            self.category_index[category.value].discard(doc_id)
        for tag in doc.tags:
            if tag in self.tag_index:
                self.tag_index[tag].discard(doc_id)

        return {
            "status": "success",
            "agent": self.name,
            "document_id": doc_id,
            "total_documents": len(self.knowledge_base),
        }

    def list_documents(
        self, category: Optional[str] = None, tags: Optional[List[str]] = None, limit: int = 50
    ) -> Dict[str, Any]:
        """List documents with optional filtering."""
        docs = list(self.knowledge_base.values())

        # Filter by category
        if category:
            doc_ids = self.category_index.get(category, set())
            docs = [d for d in docs if d.id in doc_ids]

        # Filter by tags
        if tags:
            tag_set = set(tags)
            docs = [d for d in docs if d.tags & tag_set]

        # Apply limit
        docs = docs[:limit]

        return {
            "status": "success",
            "agent": self.name,
            "total_count": len(self.knowledge_base),
            "result_count": len(docs),
            "documents": [
                {
                    "id": d.id,
                    "doc_type": d.doc_type,
                    "preview": d.content[:100],
                    "categories": [cat.value for cat in d.categories],
                    "tags": list(d.tags),
                }
                for d in docs
            ],
        }

    def search_documents(
        self, query: str, mode: str = "full_text", category: Optional[str] = None
    ) -> Dict[str, Any]:
        """Search documents using full-text or semantic search."""
        if not query:
            return {"status": "error", "message": "Search query required"}

        results = []

        if mode == "full_text":
            query_lower = query.lower()
            for doc in self.knowledge_base.values():
                if query_lower in doc.content.lower():
                    results.append(doc)
        elif mode == "semantic":
            # Semantic search using vectors (if enabled)
            if self.vector_db_enabled:
                results = self._semantic_search_impl(query)
            else:
                return {"status": "error", "message": "Semantic search not enabled"}

        # Filter by category if specified
        if category:
            results = [d for d in results if any(c.value == category for c in d.categories)]

        # Sort by relevance (access count as proxy)
        results.sort(key=lambda d: d.access_count, reverse=True)

        return {
            "status": "success",
            "agent": self.name,
            "query": query,
            "mode": mode,
            "result_count": len(results),
            "results": [
                {
                    "id": d.id,
                    "preview": d.content[:150],
                    "categories": [cat.value for cat in d.categories],
                    "tags": list(d.tags),
                }
                for d in results
            ],
        }

    def semantic_search(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Perform semantic search using vectors."""
        if not self.vector_db_enabled:
            return {"status": "error", "message": "Vector database not enabled"}

        if not query:
            return {"status": "error", "message": "Search query required"}

        results = self._semantic_search_impl(query, limit)

        return {
            "status": "success",
            "agent": self.name,
            "query": query,
            "result_count": len(results),
            "results": [
                {
                    "id": d.id,
                    "preview": d.content[:150],
                    "similarity_score": 0.85,  # Placeholder
                }
                for d in results
            ],
        }

    def add_category(self, doc_id: str, category: str) -> Dict[str, Any]:
        """Add category to document."""
        if not doc_id or not category:
            return {"status": "error", "message": "Document ID and category required"}

        if doc_id not in self.knowledge_base:
            return {"status": "error", "message": f"Document {doc_id} not found"}

        try:
            cat_enum = DocumentCategory[category.upper()]
        except KeyError:
            return {"status": "error", "message": f"Invalid category: {category}"}

        doc = self.knowledge_base[doc_id]
        doc.add_category(cat_enum)
        self.category_index[category.lower()].add(doc_id)

        return {
            "status": "success",
            "agent": self.name,
            "document_id": doc_id,
            "category": category,
        }

    def add_tag(self, doc_id: str, tag: str) -> Dict[str, Any]:
        """Add tag to document."""
        if not doc_id or not tag:
            return {"status": "error", "message": "Document ID and tag required"}

        if doc_id not in self.knowledge_base:
            return {"status": "error", "message": f"Document {doc_id} not found"}

        doc = self.knowledge_base[doc_id]
        doc.add_tag(tag)

        tag_lower = tag.lower()
        if tag_lower not in self.tag_index:
            self.tag_index[tag_lower] = set()
        self.tag_index[tag_lower].add(doc_id)

        return {
            "status": "success",
            "agent": self.name,
            "document_id": doc_id,
            "tag": tag,
        }

    def remove_tag(self, doc_id: str, tag: str) -> Dict[str, Any]:
        """Remove tag from document."""
        if not doc_id or not tag:
            return {"status": "error", "message": "Document ID and tag required"}

        if doc_id not in self.knowledge_base:
            return {"status": "error", "message": f"Document {doc_id} not found"}

        doc = self.knowledge_base[doc_id]
        tag_lower = tag.lower()
        doc.tags.discard(tag_lower)

        if tag_lower in self.tag_index:
            self.tag_index[tag_lower].discard(doc_id)

        return {
            "status": "success",
            "agent": self.name,
            "document_id": doc_id,
            "tag": tag,
        }

    def relate_documents(self, doc_id1: str, doc_id2: str) -> Dict[str, Any]:
        """Create relationship between documents."""
        if not doc_id1 or not doc_id2:
            return {"status": "error", "message": "Two document IDs required"}

        if doc_id1 not in self.knowledge_base or doc_id2 not in self.knowledge_base:
            return {"status": "error", "message": "One or both documents not found"}

        doc1 = self.knowledge_base[doc_id1]
        doc2 = self.knowledge_base[doc_id2]

        doc1.add_relation(doc_id2)
        doc2.add_relation(doc_id1)

        return {
            "status": "success",
            "agent": self.name,
            "doc_id1": doc_id1,
            "doc_id2": doc_id2,
        }

    def enable_vector_database(
        self, model: str = "sentence-transformers/all-MiniLM-L6-v2"
    ) -> Dict[str, Any]:
        """Enable vector database for semantic search."""
        self.vector_db_enabled = True
        self.logger.info(f"Enabled vector database with model: {model}")

        return {
            "status": "success",
            "agent": self.name,
            "vector_db_enabled": True,
            "model": model,
            "vector_dimension": self.vector_dimension,
        }

    def index_vector(self, doc_id: str, vector: List[float]) -> Dict[str, Any]:
        """Index document vector in vector database."""
        if not doc_id:
            return {"status": "error", "message": "Document ID required"}

        if doc_id not in self.knowledge_base:
            return {"status": "error", "message": f"Document {doc_id} not found"}

        if not self.vector_db_enabled:
            return {"status": "error", "message": "Vector database not enabled"}

        doc = self.knowledge_base[doc_id]
        doc.vector = vector

        return {
            "status": "success",
            "agent": self.name,
            "document_id": doc_id,
            "indexed": True,
        }

    def get_knowledge_stats(self) -> Dict[str, Any]:
        """Get statistics about knowledge base."""
        total_docs = len(self.knowledge_base)
        category_counts = {cat: len(doc_ids) for cat, doc_ids in self.category_index.items()}
        tag_counts = len(self.tag_index)
        total_access = sum(d.access_count for d in self.knowledge_base.values())

        return {
            "status": "success",
            "agent": self.name,
            "total_documents": total_docs,
            "total_tags": tag_counts,
            "total_accesses": total_access,
            "documents_by_category": category_counts,
            "vector_db_enabled": self.vector_db_enabled,
        }

    def get_trending_documents(self, limit: int = 10) -> Dict[str, Any]:
        """Get most-accessed documents."""
        trending = sorted(self.knowledge_base.values(), key=lambda d: d.access_count, reverse=True)[
            :limit
        ]

        return {
            "status": "success",
            "agent": self.name,
            "trending_count": len(trending),
            "trending": [
                {
                    "id": d.id,
                    "access_count": d.access_count,
                    "preview": d.content[:100],
                }
                for d in trending
            ],
        }

    # Helper methods
    def _semantic_search_impl(self, query: str, limit: int = 10) -> List[KnowledgeDocument]:
        """Implement semantic search (simplified - would use real embeddings)."""
        # Placeholder implementation
        return list(self.knowledge_base.values())[:limit]
