"""Base Agent class for Socratic Agents."""

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional


class BaseAgent(ABC):
    """
    Abstract base class for all agents in Socratic Agents.

    Agents are specialized components that handle different aspects of AI workflows.
    Each agent has a specific purpose and can work independently or be orchestrated
    with other agents.
    """

    def __init__(self, name: str, llm_client: Optional[Any] = None):
        """
        Initialize an agent.

        Args:
            name: Display name for the agent
            llm_client: Optional LLMClient from Socrates Nexus for LLM operations
        """
        self.name = name
        self.llm_client = llm_client
        self.logger = logging.getLogger(f"socratic_agents.{name}")
        self.created_at = datetime.utcnow()

    @abstractmethod
    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a request and return a response (synchronous).

        Args:
            request: Dictionary containing the request parameters

        Returns:
            Dictionary containing the response data
        """
        pass

    async def process_async(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a request asynchronously (default wraps sync).

        Args:
            request: Dictionary containing the request parameters

        Returns:
            Dictionary containing the response data
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.process, request)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"
