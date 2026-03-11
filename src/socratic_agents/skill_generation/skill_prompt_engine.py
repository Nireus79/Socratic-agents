"""Prompt engineering engine for skill generation."""

import logging
from typing import Any, Dict


class SkillPromptEngine:
    """Creates effective prompts for Claude to generate skills."""

    def __init__(self):
        """Initialize the Skill Prompt Engine."""
        self.logger = logging.getLogger(f"socratic_agents.{self.__class__.__name__}")

    def build_generation_prompt(self, context: Dict[str, Any], weak_area: str) -> str:
        """Build a prompt for skill generation."""
        project_phase = context.get("maturity_phase", "unknown")
        completion = context.get("completion_percent", 0)
        category_score = context.get(f"{weak_area}_score", 0)

        prompt = f"""You are an AI skill generator for adaptive agent optimization.

PROJECT CONTEXT:
- Maturity Phase: {project_phase}
- Completion: {completion}%
- Weak Area: {weak_area}
- Area Effectiveness Score: {category_score}%

Your task: Generate a JSON skill configuration that helps improve this weak area.

The skill must be applicable to an agent (SocraticCounselor, CodeGenerator, etc.) and provide
concrete behavioral parameters or method adjustments.

Requirements:
1. Skill should directly address the {weak_area} weakness
2. Be specific and actionable
3. Include configuration parameters an agent can use
4. Estimate 70-85% effectiveness for the target scenario

RESPONSE FORMAT (valid JSON only):
{{
  "id": "skill_<weak_area>_<phase>",
  "target_agent": "general",
  "skill_type": "behavior_parameter",
  "maturity_phase": "{project_phase}",
  "confidence": 0.75,
  "config": {{
    "focus_area": "{weak_area}",
    "approach": "specific approach to address weakness",
    "parameters": {{"param_name": "param_value"}},
    "expected_impact": "expected improvement"
  }}
}}"""

        return prompt

    def build_refinement_prompt(self, skill_id: str, feedback: str) -> str:
        """Build a prompt for refining an existing skill."""
        prompt = f"""You are refining an agent skill based on user feedback.

ORIGINAL SKILL: {skill_id}
FEEDBACK: {feedback}

Analyze this feedback and suggest improvements to the skill configuration.

Requirements:
1. Maintain the original skill ID and purpose
2. Adjust parameters based on feedback
3. Increase confidence if feedback is positive
4. Suggest different approaches if feedback is negative

RESPONSE FORMAT (valid JSON only):
{{
  "id": "{skill_id}",
  "target_agent": "general",
  "skill_type": "behavior_parameter",
  "confidence": 0.75,
  "config": {{
    "focus_area": "area",
    "approach": "refined approach",
    "parameters": {{"param_name": "param_value"}},
    "feedback_incorporated": true
  }}
}}"""

        return prompt

    def build_evaluation_prompt(self, skill_id: str, results: Dict[str, Any]) -> str:
        """Build a prompt for evaluating skill effectiveness."""
        before_score = results.get("effectiveness_before", 0)
        after_score = results.get("effectiveness_after", 0)
        improvement = after_score - before_score

        prompt = f"""You are evaluating the effectiveness of an agent skill.

SKILL: {skill_id}
BEFORE EFFECTIVENESS: {before_score}%
AFTER EFFECTIVENESS: {after_score}%
IMPROVEMENT: {improvement:+.1f}%

Analyze this effectiveness data and provide an evaluation.

Requirements:
1. Assess if the improvement is significant
2. Identify what worked well
3. Suggest adjustments if improvement is low
4. Recommend confidence level adjustment

RESPONSE FORMAT (valid JSON only):
{{
  "skill_id": "{skill_id}",
  "effectiveness_score": {after_score},
  "improvement_percent": {improvement},
  "is_effective": {str(improvement > 10).lower()},
  "assessment": "qualitative assessment",
  "confidence_adjustment": 0.1,
  "recommendations": ["recommendation 1", "recommendation 2"]
}}"""

        return prompt

    def build_compatibility_prompt(self, skill_id_a: str, skill_id_b: str) -> str:
        """Build a prompt for checking compatibility between two skills."""
        prompt = f"""Check if these two agent skills are compatible and complementary.

SKILL A: {skill_id_a}
SKILL B: {skill_id_b}

Requirements:
1. Check for conflicting configuration parameters
2. Assess if they work well together
3. Identify any dependencies or order requirements
4. Rate compatibility 0-100

RESPONSE FORMAT (valid JSON only):
{{
  "skill_a": "{skill_id_a}",
  "skill_b": "{skill_id_b}",
  "compatible": true,
  "compatibility_score": 85,
  "conflicts": [],
  "synergies": ["synergy 1"],
  "order_dependent": false,
  "recommendations": []
}}"""

        return prompt
