"""Data models for Skill Generator Agent."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class AgentSkill:
    """A generated skill for an agent.

    Skills are configuration/behavioral instructions that agents
    can apply to modify their behavior based on context.
    """

    id: str
    """Unique identifier for the skill."""

    target_agent: str
    """Which agent this skill is intended for (e.g., 'socratic_counselor')."""

    skill_type: str
    """Type of skill: 'behavior_parameter', 'method', 'workflow', etc."""

    config: Dict[str, Any]
    """Configuration for the skill (agent-specific)."""

    confidence: float
    """Confidence score (0.0-1.0) in this skill's effectiveness."""

    maturity_phase: str
    """Which maturity phase generated this skill."""

    category_focus: Optional[str] = None
    """Which weak category this skill addresses (if any)."""

    generated_at: datetime = field(default_factory=datetime.utcnow)
    """When the skill was generated."""

    effectiveness_score: Optional[float] = None
    """Effectiveness score (0.0-1.0) after being applied (set by feedback)."""

    applied: bool = False
    """Whether this skill has been applied to an agent."""

    feedback: Optional[str] = None
    """Feedback on the skill (e.g., 'helped', 'no effect', 'harmful')."""

    def to_dict(self) -> Dict[str, Any]:
        """Convert skill to dictionary format."""
        return {
            "id": self.id,
            "target_agent": self.target_agent,
            "skill_type": self.skill_type,
            "config": self.config,
            "confidence": self.confidence,
            "maturity_phase": self.maturity_phase,
            "category_focus": self.category_focus,
            "generated_at": self.generated_at.isoformat(),
            "effectiveness_score": self.effectiveness_score,
            "applied": self.applied,
            "feedback": self.feedback,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentSkill":
        """Create AgentSkill from dictionary."""
        if isinstance(data.get("generated_at"), str):
            data["generated_at"] = datetime.fromisoformat(data["generated_at"])
        return cls(**data)


@dataclass
class SkillApplicationResult:
    """Result of applying a skill to an agent.

    Tracks before/after metrics to measure skill effectiveness.
    """

    skill_id: str
    """ID of the skill that was applied."""

    agent_name: str
    """Name of the agent that received the skill."""

    before_metrics: Dict[str, Any]
    """Metrics before applying the skill."""

    after_metrics: Dict[str, Any]
    """Metrics after applying the skill."""

    effectiveness: float
    """Effectiveness score (0.0-1.0) indicating how much the skill helped."""

    timestamp: datetime = field(default_factory=datetime.utcnow)
    """When the result was recorded."""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "skill_id": self.skill_id,
            "agent_name": self.agent_name,
            "before_metrics": self.before_metrics,
            "after_metrics": self.after_metrics,
            "effectiveness": self.effectiveness,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class SkillRecommendation:
    """A skill recommendation with priority and rationale."""

    skill: AgentSkill
    """The skill being recommended."""

    priority: str
    """Priority level: 'high', 'medium', 'low'."""

    reason: str
    """Why this skill is recommended."""

    expected_impact: float
    """Expected impact (0.0-1.0) on addressing weak areas."""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "skill": self.skill.to_dict(),
            "priority": self.priority,
            "reason": self.reason,
            "expected_impact": self.expected_impact,
        }
