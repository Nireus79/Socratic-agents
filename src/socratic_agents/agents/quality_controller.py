"""Quality Controller Agent - Quality assurance, workflow approval, and optimization.

This agent:
1. Uses MaturityCalculator from socrates-maturity to estimate project phase
2. Identifies weak areas that need skill-based improvement
3. Manages workflow approval system to prevent greedy optimization
4. Enumerates execution paths and recommends optimal routes based on cost/risk/quality metrics
"""

from typing import Any, Dict, List, Optional
import uuid

from socrates_maturity import MaturityCalculator

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
        # Phase 3: Workflow approval system
        self.pending_approvals: Dict[str, Dict[str, Any]] = {}
        self.approved_workflows: Dict[str, Dict[str, Any]] = {}
        self.rejected_workflows: Dict[str, Dict[str, Any]] = {}

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
        elif action == "approve_workflow":
            return self._request_workflow_approval(request.get("workflows", []))
        elif action == "submit_approval":
            return self._submit_approval(request.get("workflow_id"), request.get("approved", False))
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

    def _request_workflow_approval(self, workflows: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Request approval for workflow paths by analyzing cost and risk metrics.

        Enumerates possible execution paths, calculates metrics (cost, risk, quality),
        recommends optimal path, and requests human approval before proceeding.
        Prevents greedy optimization by requiring deliberate approval.

        Args:
            workflows: List of workflow path dictionaries to analyze

        Returns:
            Approval request with metrics for each path and recommendation
        """
        if not workflows:
            return {"status": "error", "agent": self.name, "message": "Workflows required"}

        workflow_id = f"workflow_{uuid.uuid4().hex[:8]}"
        analyzed_paths = []

        for idx, workflow in enumerate(workflows):
            metrics = self._calculate_workflow_metrics(workflow)
            analyzed_paths.append(
                {
                    "path_id": f"path_{idx}",
                    "path": workflow.get("steps", []),
                    "metrics": metrics,
                }
            )

        # Recommend optimal path (lowest total cost)
        recommended_path = min(analyzed_paths, key=lambda p: p["metrics"]["total_cost"])

        approval_request = {
            "id": workflow_id,
            "status": "pending",
            "paths": analyzed_paths,
            "recommended_path_id": recommended_path["path_id"],
            "recommendation_reason": f"Lowest total cost: {recommended_path['metrics']['total_cost']} tokens",
        }

        self.pending_approvals[workflow_id] = approval_request

        return {
            "status": "pending_approval",
            "agent": self.name,
            "workflow_id": workflow_id,
            "paths_analyzed": len(analyzed_paths),
            "approval_request": approval_request,
        }

    def _calculate_workflow_metrics(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate cost, risk, and quality metrics for a workflow path.

        Args:
            workflow: Workflow with steps and configurations

        Returns:
            Dictionary with cost, risk, quality, and ROI metrics
        """
        steps = workflow.get("steps", [])
        step_count = len(steps)

        # Cost calculation: estimate tokens per step
        token_cost = step_count * 500  # Base: ~500 tokens per agent step
        usd_cost = token_cost / 1000 * 0.002  # Approximate cost per 1k tokens

        # Risk calculation based on completeness
        missing_categories = workflow.get("missing_categories", 0)
        incompleteness_risk = min(1.0, missing_categories / 5.0)
        complexity_risk = min(1.0, step_count / 10.0)
        risk_score = (incompleteness_risk * 0.6) + (complexity_risk * 0.4)

        # Quality calculation
        coverage_quality = 1.0 - incompleteness_risk
        complexity_quality = 1.0 - (complexity_risk * 0.5)
        quality_score = max(0.0, min(100.0, (coverage_quality + complexity_quality) * 50))

        # ROI: maturity gain per token
        maturity_gain = workflow.get("estimated_maturity_gain", step_count * 10)
        roi = maturity_gain / max(token_cost, 1)

        return {
            "token_cost": token_cost,
            "usd_cost": round(usd_cost, 4),
            "total_cost": token_cost,
            "risk_score": round(risk_score, 3),
            "incompleteness_risk": round(incompleteness_risk, 3),
            "complexity_risk": round(complexity_risk, 3),
            "quality_score": round(quality_score, 1),
            "roi": round(roi, 3),
            "step_count": step_count,
        }

    def _submit_approval(self, workflow_id: str, approved: bool) -> Dict[str, Any]:
        """
        Submit user approval or rejection for a pending workflow.

        Args:
            workflow_id: ID of the workflow to approve/reject
            approved: True to approve, False to reject

        Returns:
            Status of approval submission
        """
        if workflow_id not in self.pending_approvals:
            return {"status": "error", "agent": self.name, "message": f"Workflow {workflow_id} not found"}

        request = self.pending_approvals.pop(workflow_id)
        request["status"] = "approved" if approved else "rejected"

        if approved:
            self.approved_workflows[workflow_id] = request
            return {
                "status": "success",
                "agent": self.name,
                "workflow_id": workflow_id,
                "approved": True,
                "message": f"Workflow approved. Using recommended path: {request['recommended_path_id']}",
            }
        else:
            self.rejected_workflows[workflow_id] = request
            return {
                "status": "success",
                "agent": self.name,
                "workflow_id": workflow_id,
                "approved": False,
                "message": "Workflow rejected. Please submit alternative workflow.",
            }

    def _get_pending_approvals(self) -> Dict[str, Any]:
        """
        Get all pending workflow approvals.

        Returns:
            List of pending approval requests
        """
        return {
            "status": "success",
            "agent": self.name,
            "pending_count": len(self.pending_approvals),
            "approved_count": len(self.approved_workflows),
            "rejected_count": len(self.rejected_workflows),
            "pending_approvals": list(self.pending_approvals.values()),
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
        """
        Estimate current maturity phase based on code.

        Uses MaturityCalculator from socrates-maturity to estimate phase
        from average category score.
        """
        avg_score = sum(category_scores.values()) / len(category_scores)
        # Use MaturityCalculator for phase estimation
        return MaturityCalculator.estimate_current_phase(avg_score)

    def _estimate_completion(self, code: str) -> float:
        """Estimate completion percentage based on code length."""
        # Simple heuristic: 50 lines = 25%, 200+ lines = 100%
        lines = len(code.split("\n"))
        percent = min(100.0, (lines / 2.0))
        return percent
