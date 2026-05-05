"""Universal team role definitions for all project types."""

from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class TeamMemberRole:
    """Represents a team member's role and metadata in a project."""

    username: str
    role: str
    skills: List[str]
    joined_at: datetime

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            "username": self.username,
            "role": self.role,
            "skills": self.skills,
            "joined_at": self.joined_at.isoformat(),
        }

    @staticmethod
    def from_dict(data):
        """Create from dictionary."""
        return TeamMemberRole(
            username=data["username"],
            role=data["role"],
            skills=data.get("skills", []),
            joined_at=datetime.fromisoformat(data["joined_at"]),
        )


# Universal role-specific question focus areas
ROLE_FOCUS_AREAS = {
    "lead": "overall vision, strategic goals, resource allocation, stakeholder management",
    "creator": "creating deliverables, building/writing/producing core outputs",
    "specialist": "domain expertise, specialized knowledge, technical/creative depth",
    "analyst": "research, analysis, evaluation, data interpretation, requirements gathering",
    "coordinator": "timelines, schedules, dependencies, process management, team coordination",
    "tester": "quality assurance, testing strategies, bug identification and reporting",
}

VALID_ROLES = [
    "lead", "creator", "specialist", "analyst", "coordinator", "tester",
    "owner", "editor", "viewer",
]

ROLE_EXAMPLES = {
    "software": {
        "lead": "Architect", "creator": "Developer", "specialist": "Security Expert",
        "analyst": "Business Analyst", "coordinator": "Project Manager", "tester": "QA Engineer",
    },
    "business": {
        "lead": "CEO/Owner", "creator": "Strategist", "specialist": "Financial Expert",
        "analyst": "Market Researcher", "coordinator": "Operations Manager", "tester": "Quality Auditor",
    },
}
