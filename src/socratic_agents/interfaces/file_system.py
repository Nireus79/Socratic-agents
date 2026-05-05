"""File system service interface - abstraction for file I/O operations."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class FileSystemService(ABC):
    """Abstract interface for file system operations."""

    @abstractmethod
    async def save_file(
        self,
        file_path: str,
        content: str,
        create_directories: bool = True,
        **kwargs: Any,
    ) -> bool:
        """Save file to disk."""
        pass

    @abstractmethod
    async def load_file(self, file_path: str) -> Optional[str]:
        """Load file from disk."""
        pass

    @abstractmethod
    async def delete_file(self, file_path: str) -> bool:
        """Delete file from disk."""
        pass

    @abstractmethod
    async def file_exists(self, file_path: str) -> bool:
        """Check if file exists."""
        pass

    @abstractmethod
    async def create_directory(self, directory_path: str) -> bool:
        """Create directory."""
        pass

    @abstractmethod
    async def list_files(self, directory_path: str, recursive: bool = False) -> List[str]:
        """List files in directory."""
        pass

    @abstractmethod
    async def save_multi_file_project(
        self,
        project_id: str,
        project_name: str,
        files: Dict[str, str],
        **kwargs: Any,
    ) -> tuple[bool, Optional[str]]:
        """Save multiple files as a project structure.

        Returns: (success: bool, project_root_path: Optional[str])
        """
        pass

    @abstractmethod
    async def get_project_path(self, project_id: str) -> Optional[str]:
        """Get the root path for a project."""
        pass
