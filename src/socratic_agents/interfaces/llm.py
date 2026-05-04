"""LLM service interface - abstraction for language model interactions."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class LLMService(ABC):
    """Abstract interface for LLM operations."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> str:
        """Generate text using the LLM."""
        pass

    @abstractmethod
    async def generate_with_context(
        self,
        prompt: str,
        context: Dict[str, Any],
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Generate text with additional context."""
        pass

    @abstractmethod
    async def extract_insights(
        self,
        text: str,
        project_context: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Extract insights from text."""
        pass

    @abstractmethod
    async def analyze_code(
        self,
        code: str,
        language: str,
        analysis_type: str = "general",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Analyze code for quality, security, style, etc."""
        pass

    @abstractmethod
    async def generate_code(
        self,
        description: str,
        language: str,
        context: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> str:
        """Generate code based on description."""
        pass

    @abstractmethod
    async def get_usage_stats(self) -> Dict[str, Any]:
        """Get LLM usage statistics."""
        pass
