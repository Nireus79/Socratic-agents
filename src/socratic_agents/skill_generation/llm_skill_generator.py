"""LLM-based skill generator using Claude API for dynamic skill creation."""

import json
import logging
from typing import Any, Dict, List, Optional

from ..models.skill_models import AgentSkill


class LLMSkillGenerator:
    """Generate skills dynamically using Claude API via Socrates Nexus LLMClient."""

    def __init__(self, llm_client: Any):
        """Initialize the LLM Skill Generator."""
        self.llm_client = llm_client
        self.logger = logging.getLogger(f"socratic_agents.{self.__class__.__name__}")
        self.skill_cache: Dict[str, AgentSkill] = {}
        self.generation_costs: List[float] = []

    def generate_skill(
        self, context: Dict[str, Any], weak_area: str, prompt: str
    ) -> Optional[AgentSkill]:
        """Generate a single skill using Claude API."""
        if not self.llm_client:
            self.logger.warning("LLMClient not available")
            return None

        try:
            response = self.llm_client.chat(
                messages=[{"role": "user", "content": prompt}],
                model="claude-3-5-sonnet",
            )
            skill = self._parse_skill_response(response, weak_area, context)
            if skill:
                cache_key = f"{weak_area}_{skill.target_agent}"
                self.skill_cache[cache_key] = skill
            return skill
        except Exception as e:
            self.logger.error(f"Error generating skill for {weak_area}: {str(e)}")
            return None

    def generate_skill_batch(
        self, contexts: List[Dict[str, Any]], weak_areas: List[str], prompts: List[str]
    ) -> List[AgentSkill]:
        """Generate multiple skills in batch."""
        skills = []
        for context, weak_area, prompt in zip(contexts, weak_areas, prompts):
            skill = self.generate_skill(context, weak_area, prompt)
            if skill:
                skills.append(skill)
        return skills

    def refine_skill(
        self, skill: AgentSkill, feedback: str, refinement_prompt: str
    ) -> Optional[AgentSkill]:
        """Refine an existing skill based on feedback."""
        if not self.llm_client:
            self.logger.warning("LLMClient not available")
            return None

        try:
            response = self.llm_client.chat(
                messages=[
                    {
                        "role": "user",
                        "content": f"{refinement_prompt}\n\nOriginal: {skill.id}\n\nFeedback: {feedback}",
                    }
                ],
                model="claude-3-5-sonnet",
            )
            refined_skill = self._parse_skill_response(response, skill.category_focus or "", {})
            if refined_skill:
                refined_skill.id = skill.id
            return refined_skill
        except Exception as e:
            self.logger.error(f"Error refining skill {skill.id}: {str(e)}")
            return None

    def estimate_cost(self, context: Dict[str, Any]) -> float:
        """Estimate cost of skill generation."""
        estimated_input_tokens = 500
        estimated_output_tokens = 300
        input_cost = (estimated_input_tokens / 1_000_000) * 3.0
        output_cost = (estimated_output_tokens / 1_000_000) * 15.0
        total_cost = input_cost + output_cost
        self.generation_costs.append(total_cost)
        return round(total_cost, 6)

    def get_average_cost(self) -> float:
        """Get average cost of generated skills."""
        if not self.generation_costs:
            return 0.0
        return sum(self.generation_costs) / len(self.generation_costs)

    def clear_cache(self) -> None:
        """Clear the skill cache."""
        self.skill_cache.clear()

    def _parse_skill_response(
        self, response: Any, weak_area: str, context: Dict[str, Any]
    ) -> Optional[AgentSkill]:
        """Parse Claude response into AgentSkill object."""
        try:
            if hasattr(response, "content"):
                text = response.content
            else:
                text = str(response)

            skill_data = self._extract_json(text)
            if not skill_data:
                return None

            skill = AgentSkill(
                id=skill_data.get("id", f"llm_{weak_area}"),
                target_agent=skill_data.get("target_agent", "general"),
                skill_type=skill_data.get("skill_type", "behavior_parameter"),
                config=skill_data.get("config", {}),
                confidence=skill_data.get("confidence", 0.7),
                maturity_phase=skill_data.get("maturity_phase", "discovery"),
                category_focus=weak_area or None,
            )
            return skill
        except Exception as e:
            self.logger.error(f"Error parsing skill response: {str(e)}")
            return None

    @staticmethod
    def _extract_json(text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from text."""
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        if "```json" in text:
            try:
                start = text.index("```json") + 7
                end = text.index("```", start)
                json_str = text[start:end].strip()
                return json.loads(json_str)
            except (ValueError, json.JSONDecodeError):
                pass

        if "```" in text:
            parts = text.split("```")
            for part in parts:
                try:
                    return json.loads(part.strip())
                except json.JSONDecodeError:
                    continue

        return None
