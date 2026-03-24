"""
Applies generated skills to agents.

Skills from SkillGenerator are applied to target agents to improve their
behavior in specific areas.
"""

from typing import Any
import logging


class SkillApplier:
    """Applies AgentSkill objects to agents."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def apply_skill(self, agent: Any, skill: Any) -> bool:
        """
        Apply a skill to an agent.

        Args:
            agent: Agent instance to receive the skill
            skill: AgentSkill object to apply

        Returns:
            True if applied successfully, False otherwise
        """
        try:
            # Check if agent supports apply_skill method
            if not hasattr(agent, "apply_skill"):
                self.logger.warning(
                    f"Agent {agent.name if hasattr(agent, 'name') else 'unknown'} "
                    f"does not support apply_skill()"
                )
                return False

            # Apply the skill
            agent.apply_skill(skill)
            self.logger.info(f"Applied skill {skill.id} to {skill.target_agent}")
            return True

        except Exception as e:
            self.logger.error(f"Error applying skill {skill.id}: {e}")
            return False

    def apply_skills_batch(self, agent: Any, skills: list) -> int:
        """
        Apply multiple skills to an agent.

        Args:
            agent: Agent instance
            skills: List of AgentSkill objects

        Returns:
            Number of skills successfully applied
        """
        applied_count = 0
        for skill in skills:
            if self.apply_skill(agent, skill):
                applied_count += 1
        return applied_count
