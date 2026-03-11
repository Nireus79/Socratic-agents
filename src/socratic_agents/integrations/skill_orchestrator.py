import uuid
from typing import Any, Dict

from ..agents.learning_agent import LearningAgent
from ..agents.quality_controller import QualityController
from ..agents.skill_generator_agent import SkillGeneratorAgent
from ..models.skill_models import AgentSkill
from ..skill_generation.compatibility_checker import CompatibilityChecker
from ..skill_generation.skill_version_manager import SkillVersionManager


class SkillOrchestrator:
    def __init__(
        self,
        llm_client=None,
        quality_controller=None,
        skill_generator=None,
        learning_agent=None,
        version_manager=None,
        compatibility_checker=None,
    ):
        self.name = "SkillOrchestrator"
        self.llm_client = llm_client
        self.quality_controller = quality_controller or QualityController(llm_client=llm_client)
        self.skill_generator = skill_generator or SkillGeneratorAgent(llm_client=llm_client)
        self.learning_agent = learning_agent or LearningAgent(llm_client=llm_client)

        # Phase 6: Version management
        self.version_manager = version_manager or SkillVersionManager()
        self.compatibility_checker = compatibility_checker or CompatibilityChecker(
            version_manager=self.version_manager
        )
        self._register_agent_capabilities()

        self.skills_history = []
        self.applied_skills = {}
        self.effectiveness_metrics = {}
        self.current_session_id = str(uuid.uuid4())

    def _register_agent_capabilities(self) -> None:
        """Register what skill types each agent can handle."""
        # Example: Register core agent capabilities
        self.compatibility_checker.register_agent_capability(
            "socratic_counselor", "behavior_parameter", "1.0"
        )
        self.compatibility_checker.register_agent_capability("socratic_counselor", "method", "1.0")
        self.compatibility_checker.register_agent_capability("code_generator", "method", "1.0")

    def process_quality_issue(self, code: str) -> Dict[str, Any]:
        if not code:
            return {"status": "error", "agent": self.name, "message": "Code required"}

        quality_check = self.quality_controller.process(
            {"action": "detect_weak_areas", "code": code}
        )
        if quality_check.get("status") != "success":
            return {"status": "error", "agent": self.name}

        weak_areas = quality_check.get("weak_areas", [])
        quality_score = quality_check.get("quality_score", 0)
        issues = quality_check.get("issues", [])

        skill_generation = self.skill_generator.process(
            {
                "action": "generate",
                "maturity_data": {
                    "current_phase": "Phase2",
                    "completion_percent": quality_score,
                    "weak_categories": weak_areas,
                },
                "learning_data": {"code_length": len(code), "issue_count": len(issues)},
                "context": {"session_id": self.current_session_id},
            }
        )

        generated_skills = skill_generation.get("skills", [])
        user_profile = self.learning_agent.get_user_learning_profile()
        personalization = self.learning_agent.process(
            {
                "action": "personalize_skills",
                "skills": generated_skills,
                "user_profile": user_profile,
            }
        )
        personalized_skills = personalization.get("personalized_skills", generated_skills)

        self.skills_history.append(
            {
                "session_id": self.current_session_id,
                "timestamp": self._get_timestamp(),
                "code_analyzed": len(code),
                "weak_areas": weak_areas,
                "quality_score": quality_score,
            }
        )

        return {
            "status": "success",
            "agent": self.name,
            "session_id": self.current_session_id,
            "generated_skills": generated_skills,
            "personalized_skills": personalized_skills,
            "quality_analysis": {
                "score": quality_score,
                "issues": issues,
                "weak_areas": weak_areas,
            },
        }

    def apply_and_track_skill(
        self, skill_id: str, skill: Dict[str, Any], feedback: str = "applied"
    ) -> Dict[str, Any]:
        if not skill_id or not skill:
            return {"status": "error", "agent": self.name}

        # Phase 6: Try to check compatibility (for versioned skills)
        # Fall back to old behavior for legacy/minimal skill dicts
        skill_obj = None
        compat_warnings = []

        try:
            skill_obj = AgentSkill.from_dict(skill)

            # Check compatibility
            compat_result = self.compatibility_checker.check_compatibility(skill_obj)

            if not compat_result.is_compatible:
                return {
                    "status": "error",
                    "agent": self.name,
                    "message": "Skill not compatible",
                    "compatibility_issues": compat_result.issues,
                }

            # Check dependencies
            dep_result = self.compatibility_checker.check_dependencies(skill_obj)
            if not dep_result.is_compatible:
                return {
                    "status": "error",
                    "agent": self.name,
                    "message": "Dependency requirements not met",
                    "missing_dependencies": dep_result.missing_dependencies,
                }

            compat_warnings = compat_result.warnings

        except Exception:
            # Backward compatibility: if skill dict is minimal/legacy format,
            # proceed without version management
            pass

        tracking_id = str(uuid.uuid4())
        self.applied_skills[skill_id] = {
            "skill": skill,
            "applied_at": self._get_timestamp(),
            "feedback": feedback,
            "tracking_id": tracking_id,
            "effectiveness_scores": [],
            "version": skill_obj.version if skill_obj else None,
        }

        # Phase 6: Register version with manager (if available)
        if skill_obj:
            self.version_manager.register_version(skill_obj, created_by="orchestrator")

        if skill_id not in self.effectiveness_metrics:
            self.effectiveness_metrics[skill_id] = []

        self.learning_agent.process(
            {"action": "track_feedback", "skill_id": skill_id, "feedback": feedback}
        )

        result = {
            "status": "success",
            "agent": self.name,
            "skill_id": skill_id,
            "applied": True,
        }

        # Add version info if available
        if skill_obj:
            result["version"] = skill_obj.version
            if compat_warnings:
                result["compatibility_warnings"] = compat_warnings

        return result

    def get_skills_history(self, phase=None) -> Dict[str, Any]:
        filtered_history = self.skills_history
        if phase:
            filtered_history = [h for h in self.skills_history if phase in h.get("session_id", "")]

        return {
            "status": "success",
            "agent": self.name,
            "total_skills_generated": (
                len(self.applied_skills.values()) if self.applied_skills else 0
            ),
            "history": filtered_history,
            "applied_skills": list(self.applied_skills.keys()),
        }

    def get_learning_profile(self) -> Dict[str, Any]:
        profile_result = self.learning_agent.process({"action": "get_profile"})
        return {
            "status": "success",
            "agent": self.name,
            "profile": profile_result.get("user_profile", {}),
            "patterns": self.learning_agent.patterns,
        }

    def analyze_skill_effectiveness(self) -> Dict[str, Any]:
        if not self.effectiveness_metrics:
            return {"status": "success", "agent": self.name, "overall_effectiveness": 0}

        all_scores = []
        skill_metrics = {}
        for skill_id, scores in self.effectiveness_metrics.items():
            if scores:
                avg = sum(scores) / len(scores)
                skill_metrics[skill_id] = {"average": avg, "count": len(scores)}
                all_scores.extend(scores)

        overall = sum(all_scores) / len(all_scores) if all_scores else 0
        return {
            "status": "success",
            "agent": self.name,
            "overall_effectiveness": round(overall, 2),
            "skill_metrics": skill_metrics,
        }

    def record_effectiveness_feedback(
        self, skill_id: str, effectiveness_score: float, notes=None
    ) -> Dict[str, Any]:
        if not skill_id or effectiveness_score < 0 or effectiveness_score > 1:
            return {"status": "error", "agent": self.name}

        if skill_id not in self.effectiveness_metrics:
            self.effectiveness_metrics[skill_id] = []

        self.effectiveness_metrics[skill_id].append(effectiveness_score)
        if skill_id in self.applied_skills:
            self.applied_skills[skill_id]["effectiveness_scores"].append(effectiveness_score)

        return {"status": "success", "agent": self.name, "skill_id": skill_id}

    def _get_timestamp(self) -> str:
        from datetime import datetime

        return datetime.now().isoformat()

    def get_orchestration_status(self) -> Dict[str, Any]:
        return {
            "status": "success",
            "agent": self.name,
            "total_sessions": len(self.skills_history),
            "total_skills_applied": len(self.applied_skills),
        }
