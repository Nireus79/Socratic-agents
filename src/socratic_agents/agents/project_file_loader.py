"""
Project File Loader Agent - Auto-loads project files into knowledge base

Extracted from monolithic Socrates system and adapted for modular architecture.

Handles:
- Checking if project has files to load
- Loading files with different strategies (priority, sample, all)
- Filtering duplicates from knowledge base
- Processing files through document processors
"""

import logging
import random
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ProjectFileLoader:
    """
    Auto-loads project files into knowledge base for Socratic dialogue.

    Supports multiple loading strategies:
    - priority: Load most important files first (README, main entry points, source)
    - sample: Load important files + random sample
    - all: Load all available files
    """

    def __init__(self, llm_client: Optional[Any] = None, knowledge_store: Optional[Any] = None):
        """
        Initialize project file loader.

        Args:
            llm_client: Optional LLM client for file analysis
            knowledge_store: Optional knowledge store for persistence
        """
        self.name = "ProjectFileLoader"
        self.llm_client = llm_client
        self.knowledge_store = knowledge_store
        self.logger = logging.getLogger(f"{__name__}.{self.name}")

    def should_load_files(self, project: Dict[str, Any]) -> bool:
        """
        Check if project has files and they should be loaded.

        Args:
            project: Project context dict

        Returns:
            True if project has files to load, False otherwise
        """
        try:
            files = project.get("files", [])
            return len(files) > 0 if files else False
        except Exception as e:
            self.logger.error(f"Error checking if files should be loaded: {str(e)}")
            return False

    def load_project_files(
        self,
        project: Dict[str, Any],
        strategy: str = "priority",
        max_files: int = 50,
        show_progress: bool = True,
    ) -> Dict[str, Any]:
        """
        Load project files into knowledge base based on strategy.

        Args:
            project: Project context with files
            strategy: Loading strategy (priority, sample, all)
            max_files: Maximum files to load
            show_progress: Whether to log progress

        Returns:
            Status dict with loaded file counts
        """
        try:
            project_id = project.get("project_id", "unknown")
            all_files = project.get("files", [])

            if not all_files:
                return self._empty_files_response(strategy)

            # Apply strategy and filter duplicates
            selected_files = self._apply_strategy(all_files, strategy, max_files)
            new_files = self._filter_duplicates(selected_files, project_id)

            if not new_files:
                return self._already_loaded_response(strategy)

            # Process files
            loaded_count, total_chunks = self._process_project_files(
                new_files, project_id, show_progress
            )

            self.logger.info(
                f"Successfully loaded {loaded_count} files "
                f"({total_chunks} chunks) using {strategy} strategy"
            )

            return {
                "status": "success",
                "files_loaded": loaded_count,
                "total_chunks": total_chunks,
                "strategy_used": strategy,
                "total_available": len(all_files),
                "files_selected": len(selected_files),
                "files_new": len(new_files),
            }

        except Exception as e:
            self.logger.error(f"Error loading project files: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to load project files: {str(e)}",
            }

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a file loading request (agent interface).

        Args:
            request: Request dict with project and options

        Returns:
            Status response
        """
        project = request.get("project", {})
        strategy = request.get("strategy", "priority")
        max_files = request.get("max_files", 50)

        return self.load_project_files(project, strategy, max_files)

    def _process_project_files(
        self,
        files: List[Dict[str, Any]],
        project_id: str,
        show_progress: bool,
    ) -> tuple[int, int]:
        """
        Process files through document processor and return counts.

        Args:
            files: Files to process
            project_id: Project ID
            show_progress: Whether to log progress

        Returns:
            Tuple of (files_loaded, total_chunks)
        """
        loaded_count = 0
        total_chunks = 0

        for idx, file_info in enumerate(files):
            if show_progress:
                file_path = file_info.get("file_path", file_info.get("name", "unknown"))
                self.logger.info(f"Loading files... [{idx + 1}/{len(files)}] {file_path}")

            try:
                # Process file content
                file_path = file_info.get("file_path", file_info.get("name", ""))
                content = file_info.get("content", "")
                language = file_info.get("language", "text")

                if not content:
                    self.logger.warning(f"No content in file {file_path}")
                    continue

                # Add to knowledge store if available
                if self.knowledge_store:
                    result = self.knowledge_store.add_file(
                        project_id=project_id,
                        file_path=file_path,
                        content=content,
                        language=language,
                    )
                    if result:
                        loaded_count += 1
                        # Estimate chunks based on content length
                        chunks = max(1, len(content) // 512)
                        total_chunks += chunks
                else:
                    # Without knowledge store, just count as processed
                    loaded_count += 1
                    chunks = max(1, len(content) // 512)
                    total_chunks += chunks

            except Exception as e:
                file_path = file_info.get("file_path", file_info.get("name", "unknown"))
                self.logger.error(f"Error processing file {file_path}: {str(e)}")

        return loaded_count, total_chunks

    def _apply_strategy(
        self, files: List[Dict[str, Any]], strategy: str, max_files: int
    ) -> List[Dict[str, Any]]:
        """
        Apply loading strategy to select which files to load.

        Args:
            files: All available files
            strategy: Loading strategy name
            max_files: Maximum files to select

        Returns:
            Selected files based on strategy
        """
        if strategy == "priority":
            return self._priority_strategy(files, max_files)
        elif strategy == "sample":
            return self._sample_strategy(files, max_files)
        elif strategy == "all":
            return files
        else:
            self.logger.warning(f"Unknown strategy {strategy}, using priority")
            return self._priority_strategy(files, max_files)

    def _priority_strategy(
        self, files: List[Dict[str, Any]], max_files: int
    ) -> List[Dict[str, Any]]:
        """
        Priority strategy: Select most important files based on type and name.

        Files ranked by:
        1. README files
        2. Main entry points (main.py, app.py, index.js, etc.)
        3. Source files (in /src or /lib)
        4. Test files
        5. Configuration files
        6. Everything else
        """
        ranked_files = []

        # Rank files by priority level
        ranked_files.extend(self._rank_by_name(files, ["readme"], 1))
        ranked_files.extend(self._rank_by_name(files, ["main", "app", "index"], 2))
        ranked_files.extend(self._rank_by_path(files, ["/src/", "/lib/", "src/"], 3))
        ranked_files.extend(self._rank_by_path(files, ["/test", "test/"], 4))
        ranked_files.extend(self._rank_by_extension(files, [".json", ".yaml", ".yml", ".toml"], 5))

        # Add remaining files
        ranked_set = {f["file_path"] for f, _ in ranked_files}
        remaining = [(f, 6) for f in files if f["file_path"] not in ranked_set]
        ranked_files.extend(remaining)

        # Sort by priority and return top max_files
        ranked_files.sort(key=lambda x: x[1])
        return [f for f, _ in ranked_files[:max_files]]

    def _rank_by_name(
        self, files: List[Dict[str, Any]], names: List[str], priority: int
    ) -> List[tuple]:
        """Rank files by name."""
        return [
            (f, priority)
            for f in files
            if any(name.lower() in f.get("file_path", "").lower() for name in names)
        ]

    def _rank_by_path(
        self, files: List[Dict[str, Any]], paths: List[str], priority: int
    ) -> List[tuple]:
        """Rank files by path."""
        return [
            (f, priority) for f in files if any(path in f.get("file_path", "") for path in paths)
        ]

    def _rank_by_extension(
        self, files: List[Dict[str, Any]], extensions: List[str], priority: int
    ) -> List[tuple]:
        """Rank files by extension."""
        return [
            (f, priority)
            for f in files
            if any(f.get("file_path", "").endswith(ext) for ext in extensions)
        ]

    def _sample_strategy(self, files: List[Dict[str, Any]], max_files: int) -> List[Dict[str, Any]]:
        """
        Sample strategy: Random sampling with important files always included.

        Args:
            files: All available files
            max_files: Maximum files to select

        Returns:
            Selected files (mix of important + random)
        """
        # First apply priority to get important files
        important = self._priority_strategy(files, max(10, int(max_files * 0.2)))

        # Then add random files
        important_paths = {f["file_path"] for f in important}
        other_files = [f for f in files if f["file_path"] not in important_paths]

        sample_count = max_files - len(important)
        if sample_count > 0 and other_files:
            random_selection = random.sample(other_files, min(sample_count, len(other_files)))
            return important + random_selection

        return important[:max_files]

    def _filter_duplicates(
        self, files: List[Dict[str, Any]], project_id: str
    ) -> List[Dict[str, Any]]:
        """
        Filter out files that are already loaded in knowledge base.

        Args:
            files: Files to check
            project_id: Project ID

        Returns:
            Files not already in knowledge base
        """
        # For now, return all files as new
        # In production, would check knowledge_store for existing files
        new_files = files
        self.logger.debug(
            f"Processing {len(new_files)} files for project {project_id} (no deduplication yet)"
        )
        return new_files

    def _empty_files_response(self, strategy: str) -> Dict[str, Any]:
        """Return response when no files found."""
        return {
            "status": "success",
            "files_loaded": 0,
            "total_chunks": 0,
            "strategy_used": strategy,
            "message": "No files found to load",
        }

    def _already_loaded_response(self, strategy: str) -> Dict[str, Any]:
        """Return response when all files already loaded."""
        self.logger.info("All files already loaded in knowledge base")
        return {
            "status": "success",
            "files_loaded": 0,
            "total_chunks": 0,
            "strategy_used": strategy,
            "message": "All files already loaded",
        }
