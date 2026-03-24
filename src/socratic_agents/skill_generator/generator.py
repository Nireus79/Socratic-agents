"""
Pure skill generation engine for adaptive skill creation.

This module provides a pure, stateless skill generation function that takes
maturity and learning data, then produces targeted skills for agents to use.
No side effects, no dependencies beyond standard library.
"""

import uuid
from typing import Any, Dict, List, Optional


class AgentSkill:
    """Represents a skill that can be applied to an agent."""

    def __init__(
        self,
        id: str,
        target_agent: str,
        skill_type: str,
        config: Dict[str, Any],
        confidence: float,
        maturity_phase: str,
        category_focus: Optional[str] = None,
    ):
        """Initialize an agent skill."""
        self.id = id
        self.target_agent = target_agent
        self.skill_type = skill_type
        self.config = config
        self.confidence = confidence
        self.maturity_phase = maturity_phase
        self.category_focus = category_focus
        self.feedback: Optional[str] = None
        self.effectiveness_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert skill to dictionary."""
        return {
            "id": self.id,
            "target_agent": self.target_agent,
            "skill_type": self.skill_type,
            "config": self.config,
            "confidence": self.confidence,
            "maturity_phase": self.maturity_phase,
            "category_focus": self.category_focus,
            "effectiveness_score": self.effectiveness_score,
        }


class SkillRecommendation:
    """Represents a prioritized skill recommendation."""

    def __init__(
        self,
        skill: AgentSkill,
        priority: str,
        reason: str,
        expected_impact: float,
    ):
        """Initialize a skill recommendation."""
        self.skill = skill
        self.priority = priority
        self.reason = reason
        self.expected_impact = expected_impact

    def to_dict(self) -> Dict[str, Any]:
        """Convert recommendation to dictionary."""
        return {
            "skill": self.skill.to_dict(),
            "priority": self.priority,
            "reason": self.reason,
            "expected_impact": self.expected_impact,
        }


class SkillGenerator:
    """
    Pure skill generation engine for creating adaptive skills.

    This is a pure data transformation:
    Input: maturity_data (phase, weak_categories) + learning_data (velocity, engagement)
    Output: List of AgentSkill objects targeted at weak areas
    """

    # 12 hardcoded skill templates (3 per phase)
    SKILL_TEMPLATES = {
        "discovery": [
            {
                "id": "problem_definition_focus",
                "target_agent": "SocraticCounselor",
                "skill_type": "behavior_parameter",
                "trigger_category": "problem_definition",
                "config": {
                    "focus_category": "problem_definition",
                    "intensity": "high",
                    "question_style": "deep_exploration",
                },
                "confidence": 0.90,
            },
            {
                "id": "scope_refinement",
                "target_agent": "SocraticCounselor",
                "skill_type": "behavior_parameter",
                "trigger_category": "scope",
                "config": {
                    "focus_category": "scope",
                    "intensity": "medium",
                    "question_style": "boundary_clarification",
                },
                "confidence": 0.85,
            },
            {
                "id": "target_audience_analysis",
                "target_agent": "SocraticCounselor",
                "skill_type": "behavior_parameter",
                "trigger_category": "target_audience",
                "config": {
                    "focus_category": "target_audience",
                    "intensity": "medium",
                    "question_style": "stakeholder_discovery",
                },
                "confidence": 0.80,
            },
        ],
        "analysis": [
            {
                "id": "functional_requirements_deep_dive",
                "target_agent": "CodeGenerator",
                "skill_type": "behavior_parameter",
                "trigger_category": "functional_requirements",
                "config": {
                    "focus_category": "functional_requirements",
                    "detail_level": "high",
                    "include_edge_cases": True,
                },
                "confidence": 0.88,
            },
            {
                "id": "nonfunctional_requirements_focus",
                "target_agent": "CodeGenerator",
                "skill_type": "behavior_parameter",
                "trigger_category": "non_functional_requirements",
                "config": {
                    "focus_category": "non_functional_requirements",
                    "detail_level": "high",
                    "categories": ["performance", "scalability", "security"],
                },
                "confidence": 0.85,
            },
            {
                "id": "data_requirements_analysis",
                "target_agent": "CodeGenerator",
                "skill_type": "behavior_parameter",
                "trigger_category": "data_requirements",
                "config": {
                    "focus_category": "data_requirements",
                    "detail_level": "high",
                    "include_relationships": True,
                },
                "confidence": 0.82,
            },
        ],
        "design": [
            {
                "id": "technology_stack_optimization",
                "target_agent": "CodeGenerator",
                "skill_type": "behavior_parameter",
                "trigger_category": "technology_stack",
                "config": {
                    "focus_category": "technology_stack",
                    "optimization": "performance",
                    "consider_maintainability": True,
                },
                "confidence": 0.85,
            },
            {
                "id": "architecture_design_review",
                "target_agent": "QualityController",
                "skill_type": "behavior_parameter",
                "trigger_category": "architecture",
                "config": {
                    "focus_area": "architecture",
                    "review_depth": "comprehensive",
                    "check_coupling": True,
                },
                "confidence": 0.88,
            },
            {
                "id": "integration_strategy_focus",
                "target_agent": "CodeGenerator",
                "skill_type": "behavior_parameter",
                "trigger_category": "integrations",
                "config": {
                    "focus_category": "integrations",
                    "detail_level": "high",
                    "include_error_handling": True,
                },
                "confidence": 0.80,
            },
        ],
        "implementation": [
            {
                "id": "code_quality_enhancement",
                "target_agent": "QualityController",
                "skill_type": "behavior_parameter",
                "trigger_category": "code_quality",
                "config": {
                    "focus_area": "code_quality",
                    "standards": "strict",
                    "enforce_patterns": True,
                },
                "confidence": 0.87,
            },
            {
                "id": "testing_strategy",
                "target_agent": "CodeValidator",
                "skill_type": "behavior_parameter",
                "trigger_category": "testing_coverage",
                "config": {
                    "focus_area": "testing",
                    "coverage_target": 85,
                    "include_integration_tests": True,
                },
                "confidence": 0.85,
            },
            {
                "id": "documentation_focus",
                "target_agent": "DocumentProcessor",
                "skill_type": "behavior_parameter",
                "trigger_category": "documentation",
                "config": {
                    "focus_area": "documentation",
                    "completeness": "comprehensive",
                    "include_examples": True,
                },
                "confidence": 0.80,
            },
        ],
    }

    @staticmethod
    def generate(
        phase: str,
        weak_categories: List[str],
        category_scores: Dict[str, float],
        learning_velocity: str = "medium",
        engagement_score: float = 0.5,
    ) -> List[AgentSkill]:
        """
        Generate skills for weak categories based on maturity phase.

        Pure function: same input always produces same output structure.
        No side effects, fully deterministic.

        Args:
            phase: Maturity phase ("discovery", "analysis", "design", "implementation")
            weak_categories: List of weak category names to target
            category_scores: Dict of category -> score (0.0-1.0) for prioritization
            learning_velocity: "high", "medium", or "low"
            engagement_score: User engagement (0.0-1.0)

        Returns:
            List of AgentSkill objects sorted by priority

        Example:
            >>> skills = SkillGenerator.generate(
            ...     phase="analysis",
            ...     weak_categories=["functional_requirements", "documentation"],
            ...     category_scores={"functional_requirements": 0.4, "documentation": 0.3},
            ...     learning_velocity="high",
            ...     engagement_score=0.8
            ... )
            >>> # Returns 2 high-confidence skills targeting weak areas
        """
        if phase not in SkillGenerator.SKILL_TEMPLATES:
            return []

        phase_templates = SkillGenerator.SKILL_TEMPLATES[phase]
        skills = []

        # Generate skills for matching weak categories
        for template in phase_templates:
            trigger_category = template.get("trigger_category")

            # Skill applies only if category is weak
            if trigger_category in weak_categories:
                skill = SkillGenerator._create_skill_from_template(
                    template=template,
                    phase=phase,
                    learning_velocity=learning_velocity,
                    engagement_score=engagement_score,
                )
                skills.append(skill)

        # Prioritize by weakness and engagement
        skills_with_priority = SkillGenerator._prioritize(
            skills=skills,
            category_scores=category_scores,
            engagement_score=engagement_score,
        )

        return skills_with_priority

    @staticmethod
    def _create_skill_from_template(
        template: Dict[str, Any],
        phase: str,
        learning_velocity: str,
        engagement_score: float,
    ) -> AgentSkill:
        """Create and customize skill from template."""
        # Generate unique ID
        skill_id = f"{phase}_{template['id']}_{uuid.uuid4().hex[:8]}"

        # Copy and customize config
        config = template.get("config", {}).copy()

        # Customize intensity based on learning velocity
        if learning_velocity == "high":
            config["intensity"] = "high"
        elif learning_velocity == "low":
            config["intensity"] = "low"
        else:
            config["intensity"] = "medium"

        # Adjust confidence based on engagement
        base_confidence = template.get("confidence", 0.75)
        adjusted_confidence = base_confidence * (0.8 + (engagement_score * 0.4))
        adjusted_confidence = min(adjusted_confidence, 1.0)

        return AgentSkill(
            id=skill_id,
            target_agent=template.get("target_agent", "unknown"),
            skill_type=template.get("skill_type", "behavior_parameter"),
            config=config,
            confidence=adjusted_confidence,
            maturity_phase=phase,
            category_focus=template.get("trigger_category"),
        )

    @staticmethod
    def _prioritize(
        skills: List[AgentSkill],
        category_scores: Dict[str, float],
        engagement_score: float,
    ) -> List[AgentSkill]:
        """Prioritize skills by weakness severity and engagement."""
        # Calculate priority scores
        scored_skills = []
        for skill in skills:
            category = skill.category_focus or "unknown"
            category_score = category_scores.get(category, 0.5)

            # Calculate weakness (1.0 - score)
            weakness = 1.0 - category_score
            expected_impact = weakness * (0.5 + (engagement_score * 0.5))

            scored_skills.append((skill, expected_impact, category_score))

        # Sort by impact (descending)
        scored_skills.sort(key=lambda x: -x[1])

        # Return just skills in priority order
        return [skill for skill, _, _ in scored_skills]

    @staticmethod
    def get_templates(phase: Optional[str] = None) -> Dict[str, Any]:
        """
        Get skill templates for a phase or all phases.

        Args:
            phase: Optional phase name, or None for all phases

        Returns:
            Dictionary of templates
        """
        if phase:
            return {phase: SkillGenerator.SKILL_TEMPLATES.get(phase, [])}
        return SkillGenerator.SKILL_TEMPLATES

    @staticmethod
    def get_phases() -> List[str]:
        """Get list of all supported phases."""
        return list(SkillGenerator.SKILL_TEMPLATES.keys())

    @staticmethod
    def get_skills_for_phase(phase: str) -> List[Dict[str, Any]]:
        """Get all skill templates for a phase."""
        return SkillGenerator.SKILL_TEMPLATES.get(phase, [])
