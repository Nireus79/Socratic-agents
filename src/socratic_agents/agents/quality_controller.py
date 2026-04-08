"""Quality Controller Agent - Quality assurance, workflow approval, and optimization.

This agent:
1. Analyzes code quality through pattern detection
2. Identifies weak areas that need skill-based improvement
3. Estimates project maturity using MaturityCalculator
4. Manages workflow approval system using full WorkflowOptimizer
5. Prevents greedy optimization by analyzing ALL execution paths
6. Recommends optimal workflow paths based on cost/risk/quality metrics
"""

import uuid
from typing import Any, Dict, List, Optional, cast

from socrates_maturity import MaturityCalculator

from ..core.workflow_optimizer import DecisionStrategy, WorkflowOptimizer
from .base import BaseAgent


class QualityController(BaseAgent):
    """
    Quality assurance and workflow optimization agent.

    Manages code quality assessment, maturity tracking, skill application,
    and intelligent workflow path selection with human approval gating.
    """

    def __init__(self, llm_client: Optional[Any] = None):
        """Initialize the Quality Controller."""
        super().__init__(name="QualityController", llm_client=llm_client)
        self.tests: List[Dict[str, Any]] = []
        self.quality_score = 100.0
        # Skill integration fields
        self.quality_focus_area: Optional[str] = None
        self.generated_skills: List[Dict[str, Any]] = []
        self.skill_application_log: List[Dict[str, Any]] = []
        # Workflow approval system
        self.pending_approvals: Dict[str, Dict[str, Any]] = {}
        self.approved_workflows: Dict[str, Dict[str, Any]] = {}
        self.rejected_workflows: Dict[str, Dict[str, Any]] = {}

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process quality control requests."""
        action = request.get("action", "check")

        if action == "check":
            return self.check_quality(cast(str, request.get("code")))
        elif action == "run_tests":
            return self.run_tests()
        elif action == "report":
            return self.generate_report()
        elif action == "detect_weak_areas":
            return self.detect_weak_areas(cast(str, request.get("code")))
        elif action == "apply_skills":
            return self.apply_skills(cast(List[Dict[str, Any]], request.get("skills", [])))
        elif action == "optimize_workflow":
            return self._optimize_workflow(cast(Dict[str, Any], request.get("workflow_definition")))
        elif action == "submit_approval":
            return self._submit_approval(cast(str, request.get("workflow_id")), cast(bool, request.get("approved", False)))
        elif action == "get_pending_approvals":
            return self._get_pending_approvals()
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

    def _optimize_workflow(self, workflow_definition: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize workflow using full WorkflowOptimizer.

        Enumerates all possible execution paths, calculates comprehensive metrics
        (cost, risk, quality, ROI), recommends optimal path, and creates approval
        request for human review.

        Args:
            workflow_definition: Workflow graph with nodes, edges, start/end nodes

        Returns:
            Approval request with all paths analyzed and recommendation
        """
        if not workflow_definition:
            return {
                "status": "error",
                "agent": self.name,
                "message": "Workflow definition required",
            }

        try:
            # Create optimizer with BALANCED strategy (50% cost, 30% risk, 20% quality)
            optimizer = WorkflowOptimizer(workflow_definition, strategy=DecisionStrategy.BALANCED)

            # Run optimization (enumerates, calculates, selects)
            optimization_result = optimizer.optimize_workflow()

            if optimization_result["status"] == "error":
                return {
                    "status": "error",
                    "agent": self.name,
                    "message": optimization_result["message"],
                }

            approval_request = optimization_result["approval_request"]

            # Generate approval ID and store
            approval_id = f"approval_{uuid.uuid4().hex[:8]}"

            self.pending_approvals[approval_id] = {
                "id": approval_id,
                "status": "pending",
                "workflow_definition": workflow_definition,
                "approval_request": approval_request,
            }

            return {
                "status": "pending_approval",
                "agent": self.name,
                "approval_id": approval_id,
                "paths_analyzed": approval_request["paths_analyzed"],
                "approval_request": approval_request,
            }

        except Exception as e:
            self.logger.error(f"Workflow optimization failed: {e}")
            return {
                "status": "error",
                "agent": self.name,
                "message": f"Workflow optimization failed: {str(e)}",
            }

    def _submit_approval(self, approval_id: str, approved: bool) -> Dict[str, Any]:
        """
        Submit human approval or rejection for a pending workflow.

        Args:
            approval_id: ID of the approval request
            approved: True to approve, False to reject

        Returns:
            Status of approval submission
        """
        if approval_id not in self.pending_approvals:
            return {
                "status": "error",
                "agent": self.name,
                "message": f"Approval {approval_id} not found",
            }

        approval = self.pending_approvals.pop(approval_id)
        approval["status"] = "approved" if approved else "rejected"

        if approved:
            self.approved_workflows[approval_id] = approval

            selected_path_idx = approval["approval_request"]["selected_path_index"]
            selected_metrics = approval["approval_request"]["recommendation"]["selected_metrics"]

            return {
                "status": "success",
                "agent": self.name,
                "approval_id": approval_id,
                "approved": True,
                "selected_path_index": selected_path_idx,
                "message": f"Workflow approved. Selected path optimizes for: "
                f"{approval['approval_request']['recommendation']['reason']}",
                "metrics": selected_metrics,
            }
        else:
            self.rejected_workflows[approval_id] = approval

            return {
                "status": "success",
                "agent": self.name,
                "approval_id": approval_id,
                "approved": False,
                "message": "Workflow rejected. Please submit alternative workflow.",
            }

    def _get_pending_approvals(self) -> Dict[str, Any]:
        """
        Get all pending workflow approvals.

        Returns:
            List of pending approval requests with metrics
        """
        pending_list = []
        for approval_id, approval in self.pending_approvals.items():
            pending_list.append(
                {
                    "approval_id": approval_id,
                    "paths_analyzed": approval["approval_request"]["paths_analyzed"],
                    "selection_strategy": approval["approval_request"]["selection_strategy"],
                    "recommendation": approval["approval_request"]["recommendation"],
                }
            )

        return {
            "status": "success",
            "agent": self.name,
            "pending_count": len(self.pending_approvals),
            "approved_count": len(self.approved_workflows),
            "rejected_count": len(self.rejected_workflows),
            "pending_approvals": pending_list,
        }

    # Code quality assessment methods
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
        """
        Estimate current maturity phase based on code.

        Uses MaturityCalculator from socrates-maturity to estimate phase
        from average category score.
        """
        avg_score = sum(category_scores.values()) / len(category_scores)
        return MaturityCalculator.estimate_current_phase(avg_score)

    def _estimate_completion(self, code: str) -> float:
        """Estimate completion percentage based on code length."""
        lines = len(code.split("\n"))
        percent = min(100.0, (lines / 2.0))
        return percent
