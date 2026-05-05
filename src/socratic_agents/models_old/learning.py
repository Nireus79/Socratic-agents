"""Learning-related data models for user behavior tracking"""

from dataclasses import asdict, dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional


@dataclass
class QuestionEffectiveness:
    """Tracks how effective a question is for a specific user"""

    id: str
    user_id: str
    question_template_id: str
    role: str
    times_asked: int = 0
    times_answered_well: int = 0
    average_answer_length: int = 0
    average_spec_extraction_count: Decimal = field(default_factory=lambda: Decimal("0.0"))
    effectiveness_score: Decimal = field(default_factory=lambda: Decimal("0.5"))
    last_asked_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now())
    updated_at: datetime = field(default_factory=lambda: datetime.now())


@dataclass
class UserBehaviorPattern:
    """Stores learned behavior patterns about a user"""

    id: str
    user_id: str
    pattern_type: str
    pattern_data: Dict[str, Any] = field(default_factory=dict)
    confidence: Decimal = field(default_factory=lambda: Decimal("0.5"))
    learned_from_projects: List[str] = field(default_factory=list)
    learned_at: datetime = field(default_factory=lambda: datetime.now())
    updated_at: datetime = field(default_factory=lambda: datetime.now())


@dataclass
class KnowledgeBaseDocument:
    """Stores uploaded knowledge base documents for semantic search"""

    id: str
    project_id: str
    user_id: str
    filename: str
    file_size: int
    content_type: str
    content: str
    embedding: Optional[bytes] = None
    uploaded_at: datetime = field(default_factory=lambda: datetime.now())
