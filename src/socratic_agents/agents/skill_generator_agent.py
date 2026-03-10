"""Skill Generator Agent for adaptive skill generation based on maturity and learning data."""

import uuid
from typing import Any, Dict, List, Optional

from ..models.skill_models import AgentSkill, SkillRecommendation


class SkillGeneratorAgent:
    """
    Generates adaptive skills for agents based on maturity and learning data.

    This agent takes maturity phase data and learning metrics, then generates
    targeted behavioral skills to improve agent performance in weak areas.
    Pure data transformation: no agent dependencies, works standalone.
    """

    def __init__(self, llm_client: Optional[Any] = None, skill_templates: Optional[Dict] = None):
        """
        Initialize the Skill Generator Agent.

        Args:
            llm_client: Optional LLMClient for future LLM-based skill generation
            skill_templates: Optional custom skill templates (uses defaults if None)
        """
        self.name = "SkillGeneratorAgent"
        self.llm_client = llm_client
        self.skill_templates = skill_templates or self._load_default_templates()
        self.generated_skills: Dict[str, AgentSkill] = {}
        self.skill_effectiveness: Dict[str, float] = {}

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process skill generation requests with action routing.

        Args:
            request: Dictionary with action and parameters:
                {
                    "action": "generate" | "evaluate" | "list",
                    "maturity_data": {...},  # For generate action
                    "learning_data": {...},  # For generate action
                    "context": {...},         # Optional context
                    "skill_id": "...",       # For evaluate action
                    "feedback": "...",       # For evaluate action
                    "agent_name": "...",     # For list action
                    "phase": "..."           # For list action
                }

        Returns:
            Dictionary with status, agent name, and action-specific results
        """
        action = request.get("action", "generate")

        if action == "generate":
            return self.generate_skills(
                maturity_data=request.get("maturity_data"),
                learning_data=request.get("learning_data"),
                context=request.get("context", {}),
            )
        elif action == "evaluate":
            return self.evaluate_skill_effectiveness(
                skill_id=request.get("skill_id"),
                feedback=request.get("feedback"),
                effectiveness_score=request.get("effectiveness_score"),
            )
        elif action == "list":
            return self.list_active_skills(
                agent_name=request.get("agent_name"), phase=request.get("phase")
            )
        else:
            return {"status": "error", "agent": self.name, "message": f"Unknown action: {action}"}

    def generate_skills(
        self,
        maturity_data: Optional[Dict[str, Any]],
        learning_data: Optional[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate skills based on maturity and learning data.

        Pure data transformation: analyzes weak categories and maturity phase,
        returns applicable skills without modifying state.

        Args:
            maturity_data: Maturity system data with phase, completion, categories
            learning_data: Learning engine data with velocity, engagement, patterns
            context: Additional context (agent info, project info, etc.)

        Returns:
            Dictionary with status, generated skills, and recommendations
        """
        if not maturity_data:
            return {"status": "error", "agent": self.name, "message": "maturity_data required"}

        phase = maturity_data.get("current_phase", "unknown")
        completion = maturity_data.get("completion_percent", 0)
        weak_categories = maturity_data.get("weak_categories", [])
        category_scores = maturity_data.get("category_scores", {})

        skills: List[AgentSkill] = []

        # Get skill templates for this phase
        phase_skills = self.skill_templates.get(phase, [])

        # Generate skills for weak categories
        for skill_template in phase_skills:
            trigger_category = skill_template.get("trigger_category")

            # Skill is applicable if its trigger category is weak
            if trigger_category in weak_categories:
                skill = self._create_skill_from_template(
                    template=skill_template,
                    phase=phase,
                    learning_data=learning_data or {},
                    context=context,
                )
                skills.append(skill)
                self.generated_skills[skill.id] = skill

        # Prioritize skills based on category weakness score and learning velocity
        recommendations = self._prioritize_skills(
            skills=skills, category_scores=category_scores, learning_data=learning_data or {}
        )

        return {
            "status": "success",
            "agent": self.name,
            "phase": phase,
            "completion_percent": completion,
            "skills_generated": len(skills),
            "skills": [self._skill_to_dict(s) for s in skills],
            "recommendations": [rec.to_dict() for rec in recommendations],
        }

    def _create_skill_from_template(
        self,
        template: Dict[str, Any],
        phase: str,
        learning_data: Dict[str, Any],
        context: Dict[str, Any],
    ) -> AgentSkill:
        """
        Create an AgentSkill from a template.

        Customizes skill based on learning velocity and engagement patterns.

        Args:
            template: Skill template with base configuration
            phase: Maturity phase this skill is for
            learning_data: Learning metrics to customize skill
            context: Additional context

        Returns:
            Configured AgentSkill instance
        """
        skill_id = f"{phase}_{template['id']}_{uuid.uuid4().hex[:8]}"
        config = template.get("config", {}).copy()

        # Customize intensity based on learning velocity
        learning_velocity = learning_data.get("learning_velocity", "medium")
        if learning_velocity == "high":
            config["intensity"] = "high"
        elif learning_velocity == "low":
            config["intensity"] = "low"

        # Add engagement-based boost to confidence
        engagement = learning_data.get("engagement_score", 0.5)
        base_confidence = template.get("confidence", 0.75)
        adjusted_confidence = base_confidence * (0.8 + (engagement * 0.4))  # 0.8-1.2 multiplier

        skill = AgentSkill(
            id=skill_id,
            target_agent=template.get("target_agent", "unknown"),
            skill_type=template.get("skill_type", "behavior_parameter"),
            config=config,
            confidence=min(adjusted_confidence, 1.0),  # Cap at 1.0
            maturity_phase=phase,
            category_focus=template.get("trigger_category"),
        )

        return skill

    def _load_default_templates(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Load default skill templates for all maturity phases.

        Returns dictionary with 12 hardcoded skills (3 per phase).

        Returns:
            Dictionary mapping phase -> list of skill templates
        """
        return {
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

    def _prioritize_skills(
        self,
        skills: List[AgentSkill],
        category_scores: Dict[str, float],
        learning_data: Dict[str, Any],
    ) -> List[SkillRecommendation]:
        """
        Prioritize skills based on weakness severity and engagement.

        Higher priority for skills targeting lowest-scoring categories
        and when learning engagement is high.

        Args:
            skills: Generated skills to prioritize
            category_scores: Scores for each category (0.0-1.0, lower = weaker)
            learning_data: Learning metrics

        Returns:
            List of SkillRecommendation objects sorted by priority
        """
        recommendations = []
        engagement = learning_data.get("engagement_score", 0.5)

        for skill in skills:
            category = skill.category_focus or "unknown"
            category_score = category_scores.get(category, 0.5)

            # Calculate weakness (1.0 - score)
            weakness = 1.0 - category_score
            expected_impact = weakness * (0.5 + (engagement * 0.5))  # 0.5-1.0 range

            # Determine priority based on weakness and impact
            if expected_impact >= 0.7:
                priority = "high"
            elif expected_impact >= 0.4:
                priority = "medium"
            else:
                priority = "low"

            reason = (
                f"Addresses weak category '{category}' "
                f"({category_score:.1%} score) with "
                f"expected impact {expected_impact:.0%}"
            )

            recommendation = SkillRecommendation(
                skill=skill, priority=priority, reason=reason, expected_impact=expected_impact
            )
            recommendations.append(recommendation)

        # Sort by priority (high -> medium -> low)
        priority_order = {"high": 0, "medium": 1, "low": 2}
        recommendations.sort(key=lambda r: (priority_order.get(r.priority, 3), -r.expected_impact))

        return recommendations

    def evaluate_skill_effectiveness(
        self,
        skill_id: str,
        feedback: Optional[str] = None,
        effectiveness_score: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate a skill's effectiveness after application.

        Updates skill with feedback and effectiveness metrics for learning.

        Args:
            skill_id: ID of skill to evaluate
            feedback: Qualitative feedback (e.g., "helped", "no effect", "harmful")
            effectiveness_score: Quantitative effectiveness (0.0-1.0)

        Returns:
            Dictionary with evaluation result and updated skill info
        """
        if skill_id not in self.generated_skills:
            return {"status": "error", "agent": self.name, "message": f"Skill {skill_id} not found"}

        skill = self.generated_skills[skill_id]

        # Update skill with feedback
        skill.feedback = feedback
        if effectiveness_score is not None:
            skill.effectiveness_score = min(max(effectiveness_score, 0.0), 1.0)  # Clamp to [0, 1]
            self.skill_effectiveness[skill_id] = skill.effectiveness_score

        return {
            "status": "success",
            "agent": self.name,
            "skill_id": skill_id,
            "feedback": feedback,
            "effectiveness_score": skill.effectiveness_score,
            "skill": self._skill_to_dict(skill),
        }

    def list_active_skills(
        self, agent_name: Optional[str] = None, phase: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List all generated skills with optional filtering.

        Args:
            agent_name: Filter by target agent name
            phase: Filter by maturity phase

        Returns:
            Dictionary with filtered skill list
        """
        filtered_skills = []

        for skill in self.generated_skills.values():
            if agent_name and skill.target_agent != agent_name:
                continue
            if phase and skill.maturity_phase != phase:
                continue
            filtered_skills.append(skill)

        return {
            "status": "success",
            "agent": self.name,
            "agent_filter": agent_name,
            "phase_filter": phase,
            "skills_count": len(filtered_skills),
            "skills": [self._skill_to_dict(s) for s in filtered_skills],
        }

    def _skill_to_dict(self, skill: AgentSkill) -> Dict[str, Any]:
        """Convert AgentSkill to dictionary for JSON serialization."""
        return skill.to_dict()
