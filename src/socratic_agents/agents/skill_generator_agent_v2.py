"""Phase 4.5: Extended SkillGeneratorAgent with LLM-Powered Skill Generation Integration."""

import logging
import uuid
from typing import Any, Dict, List, Optional

from ..models.skill_models import AgentSkill
from ..skill_generation.llm_skill_generator import LLMSkillGenerator
from ..skill_generation.skill_prompt_engine import SkillPromptEngine
from ..skill_generation.skill_validation_engine import SkillValidationEngine
from ..skill_generation.skill_version_manager import SkillVersionManager
from .skill_generator_agent import SkillGeneratorAgent


class SkillGeneratorAgentV2(SkillGeneratorAgent):
    """
    Extended SkillGeneratorAgent with Phase 4 LLM-powered skill generation.

    Supports three skill generation modes:
    - Hardcoded: Fast, deterministic skills from templates
    - LLM: Dynamic skills generated via Claude API
    - Hybrid: Combine hardcoded + LLM skills for best coverage
    """

    def __init__(
        self,
        llm_client: Optional[Any] = None,
        skill_templates: Optional[Dict] = None,
        enable_llm_generation: bool = True,
        generation_mode: str = "hybrid",
    ):
        """
        Initialize extended Skill Generator Agent.

        Args:
            llm_client: Socrates Nexus LLMClient for Claude API
            skill_templates: Custom skill templates (uses defaults if None)
            enable_llm_generation: Whether to enable LLM skill generation
            generation_mode: "hardcoded", "llm", or "hybrid" (default)
        """
        super().__init__(llm_client, skill_templates)
        self.logger = logging.getLogger(f"socratic_agents.{self.__class__.__name__}")

        # Phase 4 components
        self.enable_llm_generation = enable_llm_generation
        self.generation_mode = generation_mode
        self.llm_generator = LLMSkillGenerator(llm_client) if llm_client else None
        self.prompt_engine = SkillPromptEngine()
        self.validation_engine = SkillValidationEngine()

        # Phase 6: Version management
        self.version_manager = SkillVersionManager()

        # Tracking
        self.llm_skills_generated = 0
        self.validation_results: Dict[str, Any] = {}
        self.skill_costs: List[float] = []

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process skill generation requests with Phase 4 actions.

        Extended actions:
        - "generate": Use specified generation mode (hardcoded/llm/hybrid)
        - "generate_llm": Force LLM generation
        - "refine": Refine an existing skill
        - "validate": Validate a skill
        - Plus all Phase 1-3 actions
        """
        action = request.get("action", "generate")

        if action == "generate":
            return self._generate_with_mode(
                maturity_data=request.get("maturity_data"),
                learning_data=request.get("learning_data"),
                context=request.get("context", {}),
            )
        elif action == "generate_llm":
            return self._generate_llm_skills(
                maturity_data=request.get("maturity_data"),
                learning_data=request.get("learning_data"),
                context=request.get("context", {}),
            )
        elif action == "refine":
            return self._refine_skill(
                skill_id=request.get("skill_id"),
                feedback=request.get("feedback"),
            )
        elif action == "validate":
            return self._validate_skill(
                skill_id=request.get("skill_id"),
            )
        elif action == "estimate_cost":
            return self._estimate_generation_cost(
                context=request.get("context", {}),
            )
        else:
            # Fall back to parent class for Phase 1-3 actions
            return super().process(request)

    def _generate_with_mode(
        self,
        maturity_data: Optional[Dict[str, Any]],
        learning_data: Optional[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate skills using configured mode."""
        if self.generation_mode == "hardcoded":
            return super().generate_skills(maturity_data, learning_data, context)
        elif self.generation_mode == "llm":
            return self._generate_llm_skills(maturity_data, learning_data, context)
        elif self.generation_mode == "hybrid":
            return self._generate_hybrid_skills(maturity_data, learning_data, context)
        else:
            return {
                "status": "error",
                "agent": self.name,
                "message": f"Unknown generation mode: {self.generation_mode}",
            }

    def _generate_llm_skills(
        self,
        maturity_data: Optional[Dict[str, Any]],
        learning_data: Optional[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate skills using LLM (Phase 4)."""
        if not self.llm_generator:
            return {
                "status": "error",
                "agent": self.name,
                "message": "LLMClient not available for skill generation",
            }

        if not maturity_data:
            return {
                "status": "error",
                "agent": self.name,
                "message": "maturity_data required",
            }

        phase = maturity_data.get("current_phase", "unknown")
        weak_categories = maturity_data.get("weak_categories", [])
        completion = maturity_data.get("completion_percent", 0)

        skills: List[AgentSkill] = []
        generation_errors: List[str] = []

        # Generate one skill for each weak category
        for weak_area in weak_categories:
            try:
                # Build generation prompt
                prompt_context = {
                    "maturity_phase": phase,
                    "completion_percent": completion,
                    **maturity_data.get("category_scores", {}),
                }
                prompt = self.prompt_engine.build_generation_prompt(prompt_context, weak_area)

                # Generate skill
                skill = self.llm_generator.generate_skill(
                    context=context or {}, weak_area=weak_area, prompt=prompt
                )

                if skill:
                    # Validate before adding
                    validation = self.validation_engine.validate_skill(skill)
                    if validation.is_valid:
                        skills.append(skill)
                        self.generated_skills[skill.id] = skill
                        self.llm_skills_generated += 1
                        self.validation_results[skill.id] = validation.to_dict()
                    else:
                        generation_errors.append(f"{weak_area}: Validation failed")
                else:
                    generation_errors.append(f"{weak_area}: Generation failed")

            except Exception as e:
                self.logger.error(f"Error generating LLM skill for {weak_area}: {str(e)}")
                generation_errors.append(f"{weak_area}: {str(e)}")

        # Track costs
        if self.llm_generator:
            avg_cost = self.llm_generator.get_average_cost()
            self.skill_costs.append(avg_cost)

        return {
            "status": "success" if skills else "partial",
            "agent": self.name,
            "mode": "llm",
            "phase": phase,
            "completion_percent": completion,
            "skills_generated": len(skills),
            "skills": [self._skill_to_dict(s) for s in skills],
            "errors": generation_errors,
            "avg_cost_per_skill": (
                self.llm_generator.get_average_cost() if self.llm_generator else 0.0
            ),
        }

    def _generate_hybrid_skills(
        self,
        maturity_data: Optional[Dict[str, Any]],
        learning_data: Optional[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate skills using hybrid approach.

        Strategy:
        - First generate hardcoded skills (fast, deterministic)
        - Then add 1-2 LLM skills for novelty and context awareness
        """
        # Step 1: Get hardcoded skills
        hardcoded_result = super().generate_skills(maturity_data, learning_data, context)

        # Step 2: Generate limited LLM skills (1-2)
        llm_skills = []
        if self.llm_generator and maturity_data:
            weak_categories = maturity_data.get("weak_categories", [])
            # Take only first 1-2 weak categories for LLM generation
            llm_categories = weak_categories[:2]

            for weak_area in llm_categories:
                try:
                    prompt_context = {
                        "maturity_phase": maturity_data.get("current_phase", "unknown"),
                        "completion_percent": maturity_data.get("completion_percent", 0),
                    }
                    prompt = self.prompt_engine.build_generation_prompt(prompt_context, weak_area)

                    skill = self.llm_generator.generate_skill(
                        context=context or {}, weak_area=weak_area, prompt=prompt
                    )

                    if skill:
                        validation = self.validation_engine.validate_skill(skill)
                        if validation.is_valid:
                            llm_skills.append(skill)
                            self.llm_skills_generated += 1

                except Exception as e:
                    self.logger.error(f"Error in hybrid LLM generation: {str(e)}")

        # Combine results
        all_skills = list(self.generated_skills.values())

        return {
            "status": "success",
            "agent": self.name,
            "mode": "hybrid",
            "phase": maturity_data.get("current_phase", "unknown") if maturity_data else "unknown",
            "completion_percent": (
                maturity_data.get("completion_percent", 0) if maturity_data else 0
            ),
            "hardcoded_skills": len(
                [
                    s
                    for s in all_skills
                    if s.id in [sk.get("id") for sk in hardcoded_result.get("skills", [])]
                ]
            ),
            "llm_skills": len(llm_skills),
            "total_skills": len(all_skills),
            "skills": [self._skill_to_dict(s) for s in all_skills],
            "avg_cost_per_llm_skill": (
                self.llm_generator.get_average_cost() if self.llm_generator else 0.0
            ),
        }

    def _refine_skill(self, skill_id: Optional[str], feedback: Optional[str]) -> Dict[str, Any]:
        """
        Refine an existing skill based on feedback.

        Phase 4 feature: Uses LLM to improve skills iteratively.
        Phase 6 update: Creates new versions instead of overwriting.
        """
        if not skill_id:
            return {
                "status": "error",
                "agent": self.name,
                "message": "skill_id required for refinement",
            }

        if not feedback:
            return {
                "status": "error",
                "agent": self.name,
                "message": "feedback required for refinement",
            }

        if not self.llm_generator:
            return {
                "status": "error",
                "agent": self.name,
                "message": "LLMClient not available",
            }

        # Get the skill to refine
        skill = self.generated_skills.get(skill_id)
        if not skill:
            return {
                "status": "error",
                "agent": self.name,
                "message": f"Skill not found: {skill_id}",
            }

        try:
            # Build refinement prompt
            refinement_prompt = self.prompt_engine.build_refinement_prompt(skill_id, feedback)

            # Refine skill
            refined_skill = self.llm_generator.refine_skill(
                skill=skill, feedback=feedback, refinement_prompt=refinement_prompt
            )

            if refined_skill:
                # Phase 6: Determine version increment from feedback
                version_part = self._determine_version_increment(feedback)
                new_version = self.version_manager.increment_version(skill.version, version_part)

                # Update refined skill with version information
                refined_skill.version = new_version
                refined_skill.parent_skill_id = skill.id
                refined_skill.parent_version = skill.version

                # Generate new unique ID for refined skill version
                refined_skill.id = (
                    f"{skill.id}_v{new_version.replace('.', '_')}_{uuid.uuid4().hex[:8]}"
                )

                # Validate refined skill
                validation = self.validation_engine.validate_skill(refined_skill)

                if validation.is_valid:
                    # Register version with manager
                    self.version_manager.register_version(
                        refined_skill,
                        changelog=f"Refined based on feedback: {feedback[:50]}",
                        created_by="SkillGeneratorAgentV2",
                    )

                    # Store with new ID
                    self.generated_skills[refined_skill.id] = refined_skill

                    return {
                        "status": "success",
                        "agent": self.name,
                        "original_skill": skill_id,
                        "original_version": skill.version,
                        "refined_skill": self._skill_to_dict(refined_skill),
                        "refined_version": new_version,
                        "validation": validation.to_dict(),
                    }
                else:
                    return {
                        "status": "error",
                        "agent": self.name,
                        "message": "Refined skill failed validation",
                        "errors": validation.errors,
                    }
            else:
                return {
                    "status": "error",
                    "agent": self.name,
                    "message": "Refinement failed",
                }

        except Exception as e:
            self.logger.error(f"Error refining skill {skill_id}: {str(e)}")
            return {
                "status": "error",
                "agent": self.name,
                "message": f"Refinement error: {str(e)}",
            }

    def _determine_version_increment(self, feedback: str) -> str:
        """
        Determine which version part to increment based on feedback.

        Args:
            feedback: Feedback text

        Returns:
            "major", "minor", or "patch"
        """
        feedback_lower = feedback.lower()

        # Major version for breaking changes
        if any(word in feedback_lower for word in ["breaking", "incompatible", "redesign"]):
            return "major"

        # Minor version for new features
        if any(word in feedback_lower for word in ["feature", "enhancement", "add", "new"]):
            return "minor"

        # Patch for bug fixes and improvements
        return "patch"

    def _validate_skill(self, skill_id: Optional[str]) -> Dict[str, Any]:
        """
        Validate a skill using the Phase 4 validation engine.

        Checks structure, safety, and conventions.
        """
        if not skill_id:
            return {
                "status": "error",
                "agent": self.name,
                "message": "skill_id required",
            }

        skill = self.generated_skills.get(skill_id)
        if not skill:
            return {
                "status": "error",
                "agent": self.name,
                "message": f"Skill not found: {skill_id}",
            }

        validation = self.validation_engine.validate_skill(skill)

        return {
            "status": "success",
            "agent": self.name,
            "skill_id": skill_id,
            "validation": validation.to_dict(),
            "is_valid": validation.is_valid,
        }

    def _estimate_generation_cost(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estimate the cost of generating a skill.

        Phase 4 feature: Cost tracking for Claude API usage.
        """
        if not self.llm_generator:
            return {
                "status": "error",
                "agent": self.name,
                "message": "LLMClient not available",
            }

        estimated_cost = self.llm_generator.estimate_cost(context)
        average_cost = self.llm_generator.get_average_cost()

        return {
            "status": "success",
            "agent": self.name,
            "estimated_cost_usd": estimated_cost,
            "average_cost_usd": average_cost,
            "total_skills_generated": self.llm_skills_generated,
            "estimated_cost_for_10_skills": estimated_cost * 10,
        }

    def get_phase4_stats(self) -> Dict[str, Any]:
        """
        Get Phase 4 integration statistics.

        Returns metrics on LLM skill generation, validation, and costs.
        """
        total_hardcoded = len([s for s in self.generated_skills.values() if "llm" not in s.id])
        total_llm = self.llm_skills_generated

        return {
            "total_generated_skills": len(self.generated_skills),
            "hardcoded_skills": total_hardcoded,
            "llm_skills": total_llm,
            "generation_mode": self.generation_mode,
            "llm_generation_enabled": self.enable_llm_generation,
            "validated_skills": len(self.validation_results),
            "total_generation_cost_usd": sum(self.skill_costs),
            "average_cost_per_skill_usd": (
                sum(self.skill_costs) / len(self.skill_costs) if self.skill_costs else 0.0
            ),
            "llm_client_available": self.llm_generator is not None,
        }

    def _skill_to_dict(self, skill: AgentSkill) -> Dict[str, Any]:
        """Convert skill to dictionary (inherits parent functionality)."""
        return skill.to_dict()
