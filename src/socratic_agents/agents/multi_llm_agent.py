"""Multi-LLM Agent - Coordinates multiple LLM providers."""

from typing import Any, Dict, Optional, List
from .base import BaseAgent


class MultiLlmAgent(BaseAgent):
    """Agent that coordinates calls across multiple LLM providers."""

    def __init__(self, llm_client: Optional[Any] = None):
        """Initialize the Multi-LLM Agent."""
        super().__init__(name="MultiLlmAgent", llm_client=llm_client)
        self.providers = ["anthropic", "openai", "google", "ollama"]
        self.active_provider = "anthropic"

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process multi-LLM requests."""
        action = request.get("action", "switch")
        if action == "switch":
            return self.switch_provider(request.get("provider"))
        elif action == "list":
            return self.list_providers()
        elif action == "query":
            return self.query_llm(request.get("prompt"))
        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    def switch_provider(self, provider: str) -> Dict[str, Any]:
        """Switch to a different LLM provider."""
        if provider not in self.providers:
            return {"status": "error", "message": f"Unknown provider: {provider}"}
        self.active_provider = provider
        return {"status": "success", "agent": self.name, "provider": provider}

    def list_providers(self) -> Dict[str, Any]:
        """List available LLM providers."""
        return {
            "status": "success",
            "agent": self.name,
            "providers": self.providers,
            "active_provider": self.active_provider,
        }

    def query_llm(self, prompt: str) -> Dict[str, Any]:
        """Query the active LLM provider."""
        if not prompt:
            return {"status": "error", "message": "Prompt required"}
        if self.llm_client:
            try:
                response = self.llm_client.chat(prompt)
                return {
                    "status": "success",
                    "agent": self.name,
                    "provider": self.active_provider,
                    "response": response.content,
                }
            except Exception as e:
                self.logger.error(f"LLM error: {e}")
        return {
            "status": "success",
            "agent": self.name,
            "provider": self.active_provider,
            "message": "Query ready",
        }
