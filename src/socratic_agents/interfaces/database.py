"""Database service interface - abstraction for data persistence."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class DatabaseService(ABC):
    """Abstract interface for database operations."""

    @abstractmethod
    async def save_project(self, project_id: str, project_data: Dict[str, Any]) -> None:
        """Save project to database."""
        pass

    @abstractmethod
    async def load_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Load project from database."""
        pass

    @abstractmethod
    async def update_project(self, project_id: str, updates: Dict[str, Any]) -> None:
        """Update project in database."""
        pass

    @abstractmethod
    async def delete_project(self, project_id: str) -> None:
        """Delete project from database."""
        pass

    @abstractmethod
    async def save_knowledge(self, knowledge_id: str, knowledge_data: Dict[str, Any]) -> None:
        """Save knowledge entry to database."""
        pass

    @abstractmethod
    async def load_knowledge(self, knowledge_id: str) -> Optional[Dict[str, Any]]:
        """Load knowledge entry from database."""
        pass

    @abstractmethod
    async def get_project_files(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all files for a project."""
        pass

    @abstractmethod
    async def save_project_file(self, project_id: str, file_data: Dict[str, Any]) -> None:
        """Save a file for a project."""
        pass

    @abstractmethod
    async def get_maturity_scores(self, project_id: str) -> Dict[str, Any]:
        """Get maturity scores for a project."""
        pass

    @abstractmethod
    async def save_maturity_scores(self, project_id: str, scores: Dict[str, Any]) -> None:
        """Save maturity scores for a project."""
        pass
