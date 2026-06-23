"""
Maturity tracking models for phase-specific project assessment
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List


@dataclass
class CategoryScore:
    """Score for a specific category within a phase"""

    category: str
    current_score: float
    target_score: float
    confidence: float
    spec_count: int

    @property
    def percentage(self) -> float:
        """Calculate percentage of target achieved"""
        if self.target_score == 0:
            return 0.0
        return min(100.0, (self.current_score / self.target_score) * 100)

    @property
    def is_complete(self) -> bool:
        """Check if category has reached target"""
        return self.current_score >= self.target_score

    @staticmethod
    def from_dict(data: dict) -> "CategoryScore":
        """Deserialize from dictionary."""
        return CategoryScore(**data)

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return asdict(self)


@dataclass
class PhaseMaturity:
    """Complete maturity information for a phase"""

    phase: str
    overall_score: float  # 0-100%
    category_scores: Dict[str, CategoryScore]
    total_specs: int
    missing_categories: List[str]
    strongest_categories: List[str]
    weakest_categories: List[str]
    is_ready_to_advance: bool
    warnings: List[str] = field(default_factory=list)

    @staticmethod
    def from_dict(data: dict) -> "PhaseMaturity":
        """Deserialize from dictionary."""
        data = dict(data)
        # Convert category_scores dict to CategoryScore objects if needed
        if 'category_scores' in data and data['category_scores']:
            data['category_scores'] = {
                k: CategoryScore.from_dict(v) if isinstance(v, dict) else v
                for k, v in data['category_scores'].items()
            }
        return PhaseMaturity(**data)

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        data = asdict(self)
        # Convert CategoryScore objects to dicts
        if 'category_scores' in data and data['category_scores']:
            data['category_scores'] = {
                k: v.to_dict() if hasattr(v, 'to_dict') else v
                for k, v in data['category_scores'].items()
            }
        return data


@dataclass
class MaturityEvent:
    """Event in maturity history"""

    timestamp: datetime
    phase: str
    score_before: float
    score_after: float
    delta: float
    event_type: str  # 'question_answered', 'spec_added', 'phase_advanced', etc.
    details: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def from_dict(data: dict) -> "MaturityEvent":
        """Deserialize from dictionary."""
        data = dict(data)
        if 'timestamp' in data and isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return MaturityEvent(**data)

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        data = asdict(self)
        if 'timestamp' in data and isinstance(data['timestamp'], datetime):
            data['timestamp'] = data['timestamp'].isoformat()
        return data
