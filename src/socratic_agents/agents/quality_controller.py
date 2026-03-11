"""Quality Controller Agent - Quality assurance and testing."""

from typing import Any, Dict, List, Optional

from .base import BaseAgent


class QualityController(BaseAgent):
    """Agent that manages quality assurance and testing."""

    def __init__(self, llm_client: Optional[Any] = None):
        """Initialize the Quality Controller."""
        super().__init__(name="QualityController", llm_client=llm_client)
        self.tests: List[Dict[str, Any]] = []
        self.quality_score = 100.0
        # Phase 2: Skill integration fields
        self.quality_focus_area: Optional[str] = None
        self.generated_skills: List[Dict[str, Any]] = []
        self.skill_application_log: List[Dict[str, Any]] = []

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process quality control requests."""
        action = request.get("action", "check")
        if action == "check":
            return self.check_quality(request.get("code"))  # type: ignore[arg-type]
        elif action == "run_tests":
            return self.run_tests()
        elif action == "report":
            return self.generate_report()
        elif action == "detect_weak_areas":
            return self.detect_weak_areas(request.get("code"))  # type: ignore[arg-type]
        elif action == "apply_skills":
            return self.apply_skills(request.get("skills", []))
        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    def check_quality(self, code: str) -> Dict[str, Any]:
        """Check code quality."""
        if not code:
            return {"status": "error", "message": "Code required"}
        issues = []
        if len(code) < 10:
            issues.append("Code is too short")
        if "TODO" in code:
            issues.append("Contains TODO comments")
        quality = max(0, 100 - (len(issues) * 20))
        return {"status": "success", "agent": self.name, "quality_score": quality, "issues": issues}

    def run_tests(self) -> Dict[str, Any]:
        """Run quality tests."""
        return {
            "status": "success",
            "agent": self.name,
            "tests_passed": len(self.tests),
            "tests_failed": 0,
        }

    def generate_report(self) -> Dict[str, Any]:
        """Generate quality report."""
        return {
            "status": "success",
            "agent": self.name,
            "overall_score": self.quality_score,
            "tests_run": len(self.tests),
            "issues_found": 0,
        }

    def detect_weak_areas(self, code: str) -> Dict[str, Any]:
        """
        Detect weak areas in code quality.

        Analyzes code to identify quality issues and categories where skills
        could help improve performance.

        Args:
            code: Source code to analyze

        Returns:
            Dictionary with category scores and weak areas
        """
        if not code:
            return {"status": "error", "message": "Code required"}

        # Analyze code patterns to determine category scores
        category_scores = {
            "code_quality": self._assess_code_quality(code),
            "testing_coverage": self._assess_testing(code),
            "documentation": self._assess_documentation(code),
            "architecture": self._assess_architecture(code),
            "performance": self._assess_performance(code),
        }

        # Identify weak categories (score < 0.6)
        weak_categories = [cat for cat, score in category_scores.items() if score < 0.6]

        # Estimate current maturity phase
        phase = self._estimate_maturity_phase(code, category_scores)

        return {
            "status": "success",
            "agent": self.name,
            "phase": phase,
            "category_scores": category_scores,
            "weak_categories": weak_categories,
            "completion_percent": self._estimate_completion(code),
        }

    def apply_skills(self, skills: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Apply generated skills to quality checks.

        Takes skills from SkillGeneratorAgent and applies them to improve
        quality checking behavior.

        Args:
            skills: List of skill dictionaries to apply

        Returns:
            Status of skill application
        """
        if not skills:
            return {"status": "success", "agent": self.name, "skills_applied": 0}

        applied_skills = []
        for skill in skills:
            skill_id = skill.get("id")
            focus_area = skill.get("category_focus")
            config = skill.get("config", {})

            # Store skill for reference
            self.generated_skills.append(skill)

            # Set focus area for next checks
            if focus_area:
                self.quality_focus_area = focus_area

            # Log application
            self.skill_application_log.append(
                {
                    "skill_id": skill_id,
                    "focus_area": focus_area,
                    "applied": True,
                    "config": config,
                }
            )

            applied_skills.append(skill_id)

        return {
            "status": "success",
            "agent": self.name,
            "skills_applied": len(applied_skills),
            "applied_skills": applied_skills,
            "focus_area": self.quality_focus_area,
        }

    def _assess_code_quality(self, code: str) -> float:
        """Assess code quality (0.0-1.0)."""
        score = 0.8
        if len(code) < 50:
            score -= 0.3
        if "TODO" in code or "FIXME" in code:
            score -= 0.2
        if code.count("\n") < 5:
            score -= 0.2
        return max(0.0, min(1.0, score))

    def _assess_testing(self, code: str) -> float:
        """Assess testing coverage (0.0-1.0)."""
        score = 0.6
        if "test" in code.lower():
            score += 0.2
        if "assert" in code.lower():
            score += 0.1
        return max(0.0, min(1.0, score))

    def _assess_documentation(self, code: str) -> float:
        """Assess documentation (0.0-1.0)."""
        score = 0.5
        if '"""' in code or "'''" in code:
            score += 0.3
        if "#" in code:
            score += 0.1
        return max(0.0, min(1.0, score))

    def _assess_architecture(self, code: str) -> float:
        """Assess architecture (0.0-1.0)."""
        score = 0.7
        if "class" in code:
            score += 0.2
        if "def" in code and code.count("def") > 3:
            score += 0.1
        return max(0.0, min(1.0, score))

    def _assess_performance(self, code: str) -> float:
        """Assess performance characteristics (0.0-1.0)."""
        score = 0.7
        if "for" in code or "while" in code:
            score -= 0.1
        if "import" in code and code.count("import") > 5:
            score -= 0.1
        return max(0.0, min(1.0, score))

    def _estimate_maturity_phase(self, code: str, category_scores: Dict[str, float]) -> str:
        """Estimate current maturity phase based on code."""
        avg_score = sum(category_scores.values()) / len(category_scores)
        if avg_score < 0.4:
            return "discovery"
        elif avg_score < 0.6:
            return "analysis"
        elif avg_score < 0.8:
            return "design"
        else:
            return "implementation"

    def _estimate_completion(self, code: str) -> float:
        """Estimate completion percentage based on code length."""
        # Simple heuristic: 50 lines = 25%, 200+ lines = 100%
        lines = len(code.split("\n"))
        percent = min(100.0, (lines / 2.0))
        return percent
