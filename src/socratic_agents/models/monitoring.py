"""
Monitoring and token usage models for Socrates AI
"""

import datetime
from dataclasses import asdict, dataclass


@dataclass
class TokenUsage:
    """Tracks API token usage and costs"""

    input_tokens: int
    output_tokens: int
    total_tokens: int
    timestamp: datetime.datetime
    model: str = "claude-opus-4-5-20251101"
    cost_estimate: float = 0.0

    @staticmethod
    def from_dict(data: dict) -> "TokenUsage":
        """Deserialize from dictionary."""
        data = dict(data)
        if "timestamp" in data and isinstance(data["timestamp"], str):
            data["timestamp"] = datetime.datetime.fromisoformat(data["timestamp"])
        return TokenUsage(**data)

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        data = asdict(self)
        if "timestamp" in data and isinstance(data["timestamp"], datetime.datetime):
            data["timestamp"] = data["timestamp"].isoformat()
        return data
