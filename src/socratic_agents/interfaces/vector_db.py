"""Vector database service interface - abstraction for semantic search."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class VectorDatabaseService(ABC):
    """Abstract interface for vector database operations."""

    @abstractmethod
    async def add_documents(
        self,
        documents: List[Dict[str, Any]],
        project_id: Optional[str] = None,
        **kwargs: Any,
    ) -> List[str]:
        """Add documents to vector database and return document IDs."""
        pass

    @abstractmethod
    async def search(
        self,
        query: str,
        top_k: int = 5,
        project_id: Optional[str] = None,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """Search vector database for similar documents."""
        pass

    @abstractmethod
    async def delete_documents(
        self,
        document_ids: List[str],
        **kwargs: Any,
    ) -> None:
        """Delete documents from vector database."""
        pass

    @abstractmethod
    async def update_document(
        self,
        document_id: str,
        document_data: Dict[str, Any],
        **kwargs: Any,
    ) -> None:
        """Update a document in vector database."""
        pass

    @abstractmethod
    async def get_document(
        self,
        document_id: str,
        **kwargs: Any,
    ) -> Optional[Dict[str, Any]]:
        """Get a document by ID."""
        pass

    @abstractmethod
    async def clear_project(self, project_id: str) -> None:
        """Clear all documents for a project."""
        pass
