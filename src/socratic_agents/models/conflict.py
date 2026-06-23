"""
Conflict detection models for Socrates AI
"""

from dataclasses import asdict, dataclass
from typing import List


@dataclass
class ConflictInfo:
    """Represents a conflict detected in project specifications"""

    conflict_id: str
    conflict_type: str  # 'tech_stack', 'requirements', 'goals', 'constraints'
    old_value: str
    new_value: str
    old_author: str
    new_author: str
    old_timestamp: str
    new_timestamp: str
    severity: str  # 'low', 'medium', 'high'
    suggestions: List[str]

    @staticmethod
    def from_dict(data: dict) -> "ConflictInfo":
        """Deserialize from dictionary."""
        return ConflictInfo(**data)

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return asdict(self)
