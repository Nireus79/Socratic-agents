"""
Pure skill generation engine.

Provides a stateless, deterministic skill generation function that creates
targeted skills based on maturity phase and weak categories.
"""

from .generator import (
    AgentSkill,
    SkillGenerator,
    SkillRecommendation,
)

__all__ = [
    "SkillGenerator",
    "AgentSkill",
    "SkillRecommendation",
]
