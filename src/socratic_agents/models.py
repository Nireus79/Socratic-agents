"""Data models for Socratic Agents."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class LLMProviderConfig:
    """Configuration for an LLM provider."""

    provider: str  # "claude", "openai", "gemini", "ollama"
    api_key: Optional[str] = None
    model: str = "default"
    base_url: Optional[str] = None  # For Ollama or custom endpoints
    temperature: float = 0.7
    max_tokens: int = 2048
    timeout: int = 30
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate configuration."""
        if self.provider not in ["claude", "openai", "gemini", "ollama"]:
            raise ValueError(f"Unknown provider: {self.provider}")
        if not 0 <= self.temperature <= 2:
            raise ValueError(f"Temperature must be between 0 and 2, got {self.temperature}")
        if self.max_tokens < 1:
            raise ValueError(f"Max tokens must be positive, got {self.max_tokens}")


@dataclass
class LLMUsageRecord:
    """Record of LLM API usage for billing and tracking."""

    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost_usd: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProviderMetadata:
    """Metadata about an LLM provider."""

    name: str
    display_name: str
    models: List[str]
    default_model: str
    requires_api_key: bool
    cost_per_1k_input_tokens: float
    cost_per_1k_output_tokens: float
    supports_streaming: bool = True
    supports_vision: bool = False
    max_context_tokens: int = 4096
    metadata: Dict[str, Any] = field(default_factory=dict)


def get_provider_metadata(provider: str) -> ProviderMetadata:
    """
    Get metadata for a specific LLM provider.

    Args:
        provider: Provider name ("claude", "openai", "gemini", "ollama")

    Returns:
        ProviderMetadata for the provider

    Raises:
        ValueError: If provider is unknown
    """
    metadata_map = {
        "claude": ProviderMetadata(
            name="claude",
            display_name="Anthropic Claude",
            models=[
                "claude-3-5-sonnet-20241022",
                "claude-3-5-haiku-20241022",
                "claude-3-opus-20250219",
            ],
            default_model="claude-3-5-sonnet-20241022",
            requires_api_key=True,
            cost_per_1k_input_tokens=0.003,
            cost_per_1k_output_tokens=0.015,
            supports_vision=True,
        ),
        "openai": ProviderMetadata(
            name="openai",
            display_name="OpenAI GPT",
            models=["gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"],
            default_model="gpt-4-turbo",
            requires_api_key=True,
            cost_per_1k_input_tokens=0.01,
            cost_per_1k_output_tokens=0.03,
            supports_vision=True,
        ),
        "gemini": ProviderMetadata(
            name="gemini",
            display_name="Google Gemini",
            models=["gemini-pro", "gemini-pro-vision"],
            default_model="gemini-pro",
            requires_api_key=True,
            cost_per_1k_input_tokens=0.0005,
            cost_per_1k_output_tokens=0.0015,
            supports_vision=True,
        ),
        "ollama": ProviderMetadata(
            name="ollama",
            display_name="Ollama (Local)",
            models=["llama2", "mistral", "neural-chat"],
            default_model="llama2",
            requires_api_key=False,
            cost_per_1k_input_tokens=0.0,
            cost_per_1k_output_tokens=0.0,
            supports_vision=False,
        ),
    }

    if provider not in metadata_map:
        raise ValueError(f"Unknown provider: {provider}")

    return metadata_map[provider]


def list_available_providers() -> List[str]:
    """
    List all available LLM providers.

    Returns:
        List of provider names
    """
    return ["claude", "openai", "gemini", "ollama"]


__all__ = [
    "LLMProviderConfig",
    "LLMUsageRecord",
    "ProviderMetadata",
    "get_provider_metadata",
    "list_available_providers",
]
