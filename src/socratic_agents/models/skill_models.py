"""Data models for Skill Generator Agent."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


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

    # Phase 6: Version and compatibility fields
    version: str = "1.0.0"
    """Semantic version: MAJOR.MINOR.PATCH."""

    schema_version: str = "1.0"
    """Config schema version (for compatibility checking)."""

    parent_skill_id: Optional[str] = None
    """ID of parent skill if this is a refined version."""

    parent_version: Optional[str] = None
    """Version of parent skill."""

    dependencies: List[Dict[str, Any]] = field(default_factory=list)
    """List of {skill_id, min_version, max_version, optional}."""

    compatible_agents: List[str] = field(default_factory=list)
    """Agents this skill can be applied to (empty = all)."""

    deprecated: bool = False
    """Whether this skill version is deprecated."""

    deprecation_reason: Optional[str] = None
    """Why this version was deprecated."""

    replacement_skill_id: Optional[str] = None
    """ID of skill that replaces this one."""

    replacement_version: Optional[str] = None
    """Version of replacement skill."""

    migration_guide: Optional[str] = None
    """How to migrate from this skill to replacement."""

    def get_version_tuple(self) -> Tuple[int, int, int]:
        """Parse version string to tuple for comparison."""
        parts = self.version.split(".")
        return (int(parts[0]), int(parts[1]), int(parts[2]))

    def is_compatible_with(self, other: "AgentSkill") -> bool:
        """Check if this skill is compatible with another skill."""
        # Check schema compatibility
        if self.schema_version != other.schema_version:
            return False

        # Check agent compatibility
        if self.compatible_agents and other.target_agent not in self.compatible_agents:
            return False

        return True

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
            # Phase 6 version fields
            "version": self.version,
            "schema_version": self.schema_version,
            "parent_skill_id": self.parent_skill_id,
            "parent_version": self.parent_version,
            "dependencies": self.dependencies,
            "compatible_agents": self.compatible_agents,
            "deprecated": self.deprecated,
            "deprecation_reason": self.deprecation_reason,
            "replacement_skill_id": self.replacement_skill_id,
            "replacement_version": self.replacement_version,
            "migration_guide": self.migration_guide,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentSkill":
        """Create AgentSkill from dictionary."""
        if isinstance(data.get("generated_at"), str):
            data["generated_at"] = datetime.fromisoformat(data["generated_at"])
        return cls(**data)


@dataclass
class SkillVersion:
    """Metadata about a specific skill version."""

    skill_id: str
    """Base skill ID (without version)."""

    version: str
    """Version string: MAJOR.MINOR.PATCH."""

    skill: AgentSkill
    """The actual skill object."""

    created_at: datetime = field(default_factory=datetime.utcnow)
    """When this version was created."""

    created_by: str = "system"
    """Who/what created this version."""

    changelog: Optional[str] = None
    """What changed in this version."""

    download_count: int = 0
    """How many times this version was retrieved."""

    application_count: int = 0
    """How many times this version was applied."""


@dataclass
class DependencyConstraint:
    """A dependency constraint for a skill."""

    skill_id: str
    """Required skill ID."""

    min_version: Optional[str] = None
    """Minimum required version (inclusive)."""

    max_version: Optional[str] = None
    """Maximum allowed version (exclusive)."""

    optional: bool = False
    """Whether this dependency is optional."""

    def is_satisfied_by(self, version: str) -> bool:
        """Check if a version satisfies this constraint."""
        v_tuple = self._parse_version(version)

        if self.min_version:
            min_tuple = self._parse_version(self.min_version)
            if v_tuple < min_tuple:
                return False

        if self.max_version:
            max_tuple = self._parse_version(self.max_version)
            if v_tuple >= max_tuple:
                return False

        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "skill_id": self.skill_id,
            "min_version": self.min_version,
            "max_version": self.max_version,
            "optional": self.optional,
        }

    @staticmethod
    def _parse_version(v: str) -> Tuple[int, int, int]:
        """Parse version string to tuple."""
        parts = v.split(".")
        return (int(parts[0]), int(parts[1]), int(parts[2]))


@dataclass
class CompatibilityResult:
    """Result of a compatibility check."""

    is_compatible: bool
    """Whether the skill is compatible."""

    skill_id: str
    """Skill being checked."""

    version: str
    """Version being checked."""

    issues: List[str] = field(default_factory=list)
    """Compatibility issues found."""

    warnings: List[str] = field(default_factory=list)
    """Non-fatal warnings."""

    missing_dependencies: List[str] = field(default_factory=list)
    """Dependencies that couldn't be resolved."""

    version_conflicts: List[Tuple[str, str, str]] = field(default_factory=list)
    """(skill_id, required_version, actual_version)."""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "is_compatible": self.is_compatible,
            "skill_id": self.skill_id,
            "version": self.version,
            "issues": self.issues,
            "warnings": self.warnings,
            "missing_dependencies": self.missing_dependencies,
            "version_conflicts": [
                {"skill_id": s, "required": r, "actual": a} for s, r, a in self.version_conflicts
            ],
        }


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
