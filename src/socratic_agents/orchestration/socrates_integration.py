"""
Phase 7: Socrates System Integration

Integrates PureOrchestrator and MaturityAwareOrchestrator into the main
Socrates AgentOrchestrator, enabling maturity-driven workflow gating and
skill application across the entire system.

This module provides methods that can be added to or wrapped around the
existing AgentOrchestrator to enable Phase 5-6 functionality.
"""

from typing import Any, Dict, Optional, Callable
import logging

from .orchestrator import PureOrchestrator, AgentRequest
from .integration import MaturityAwareOrchestrator, OrchestratorAdapter
from socrates_maturity import MaturityCalculator


class SocratesIntegration:
    """
    Integration helpers for adding maturity-driven orchestration to Socrates.

    This class provides methods to:
    1. Get user maturity from database
    2. Get agent effectiveness scores
    3. Apply maturity-driven gating
    4. Manage skill application
    5. Track workflow progression
    """

    def __init__(
        self,
        database: Any,  # Socrates database singleton
        user_manager: Any = None,  # Optional user manager agent
    ):
        """
        Initialize Socrates integration.

        Args:
            database: Socrates database singleton
            user_manager: Optional UserManager agent instance
        """
        self.database = database
        self.user_manager = user_manager
        self.logger = logging.getLogger(__name__)

        # Track user maturity progression
        self._user_maturity_cache: Dict[str, Dict[str, float]] = {}

        # Track agent effectiveness
        self._agent_effectiveness: Dict[str, float] = {}

    def get_user_maturity(
        self,
        user_id: str,
        phase: Optional[str] = None,
    ) -> float:
        """
        Get user's maturity score.

        Args:
            user_id: User ID
            phase: Optional specific phase. If None, returns overall maturity.

        Returns:
            Maturity score (0.0-1.0)
        """
        try:
            # Try to get from cache first
            if user_id in self._user_maturity_cache:
                if phase is None:
                    return self._calculate_overall_maturity(self._user_maturity_cache[user_id])
                return self._user_maturity_cache[user_id].get(phase, 0.5)

            # Get from database if available
            user = self.database.load_user(user_id)
            if user and hasattr(user, "maturity_scores"):
                self._user_maturity_cache[user_id] = user.maturity_scores
                if phase is None:
                    return self._calculate_overall_maturity(user.maturity_scores)
                return user.maturity_scores.get(phase, 0.5)

            # Default: return moderate maturity
            return 0.5

        except Exception as e:
            self.logger.warning(f"Error getting user maturity: {e}")
            return 0.5  # Default fallback

    def get_user_phase(self, user_id: str) -> str:
        """
        Get current maturity phase for user.

        Args:
            user_id: User ID

        Returns:
            Current phase ("discovery", "analysis", "design", "implementation")
        """
        overall_maturity = self.get_user_maturity(user_id)
        return MaturityCalculator.estimate_current_phase(overall_maturity)

    def get_agent_effectiveness(self, agent_name: str) -> float:
        """
        Get effectiveness score for an agent.

        Args:
            agent_name: Agent name

        Returns:
            Effectiveness score (0.0-1.0)
        """
        return self._agent_effectiveness.get(agent_name, 0.7)

    def record_agent_execution(
        self,
        user_id: str,
        agent_name: str,
        action: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        effectiveness: float,
        duration_ms: float = 0.0,
    ) -> bool:
        """
        Record an agent execution for learning and tracking.

        Args:
            user_id: User who triggered execution
            agent_name: Agent that was executed
            action: Action performed
            input_data: Input to the agent
            output_data: Output from the agent
            effectiveness: Effectiveness score (0.0-1.0)
            duration_ms: Execution duration in milliseconds

        Returns:
            True if recorded successfully
        """
        try:
            # Update effectiveness score (running average)
            current_eff = self.get_agent_effectiveness(agent_name)
            new_eff = (current_eff + effectiveness) / 2
            self._agent_effectiveness[agent_name] = new_eff

            # Log to learning agent if available
            # This would integrate with socratic-learning
            self.logger.info(f"Recorded {agent_name}.{action} effectiveness={effectiveness:.2f}")

            return True

        except Exception as e:
            self.logger.error(f"Error recording execution: {e}")
            return False

    def update_user_maturity(
        self,
        user_id: str,
        phase_scores: Dict[str, float],
    ) -> bool:
        """
        Update user's maturity scores.

        Args:
            user_id: User ID
            phase_scores: Dict mapping phase names to scores

        Returns:
            True if updated successfully
        """
        try:
            # Update cache
            self._user_maturity_cache[user_id] = phase_scores

            # Save to database
            user = self.database.load_user(user_id)
            if user:
                user.maturity_scores = phase_scores
                self.database.save_user(user)

            self.logger.info(f"Updated maturity for {user_id}: {phase_scores}")
            return True

        except Exception as e:
            self.logger.error(f"Error updating maturity: {e}")
            return False

    def create_maturity_aware_orchestrator(
        self,
        existing_orchestrator: Any,
        pure_orchestrator: PureOrchestrator,
    ) -> MaturityAwareOrchestrator:
        """
        Create a maturity-aware wrapper around the existing orchestrator.

        Args:
            existing_orchestrator: The Socrates AgentOrchestrator
            pure_orchestrator: The PureOrchestrator instance

        Returns:
            MaturityAwareOrchestrator wrapping both
        """
        return MaturityAwareOrchestrator(
            existing_orchestrator=existing_orchestrator,
            pure_orchestrator=pure_orchestrator,
            maturity_tracker=self.get_user_maturity,
        )

    def get_recommended_next_steps(
        self,
        user_id: str,
    ) -> Dict[str, Any]:
        """
        Get recommended next steps based on user maturity.

        Args:
            user_id: User ID

        Returns:
            Dict with recommendations
        """
        current_phase = self.get_user_phase(user_id)
        current_maturity = self.get_user_maturity(user_id)

        recommendations = {
            "current_phase": current_phase,
            "current_maturity": f"{current_maturity:.0%}",
            "next_phase": self._get_next_phase(current_phase),
            "maturity_to_next_phase": self._get_maturity_to_next_phase(current_phase),
            "focus_areas": self._get_focus_areas(user_id, current_phase),
            "available_agents": self._get_available_agents(current_phase),
        }

        return recommendations

    # =========================================================================
    # PRIVATE HELPERS
    # =========================================================================

    def _calculate_overall_maturity(self, phase_scores: Dict[str, float]) -> float:
        """Calculate overall maturity from phase scores."""
        return MaturityCalculator.calculate_overall_maturity(phase_scores)

    def _get_next_phase(self, current_phase: str) -> str:
        """Get the next phase in progression."""
        phases = ["discovery", "analysis", "design", "implementation"]
        if current_phase in phases:
            idx = phases.index(current_phase)
            return phases[min(idx + 1, len(phases) - 1)]
        return "implementation"

    def _get_maturity_to_next_phase(self, current_phase: str) -> str:
        """Get maturity score needed for next phase."""
        phase_thresholds = {
            "discovery": "25%",
            "analysis": "50%",
            "design": "75%",
            "implementation": "100%",
        }
        return phase_thresholds.get(current_phase, "unknown")

    def _get_focus_areas(
        self,
        user_id: str,
        current_phase: str,
    ) -> list:
        """Get focus areas for user."""
        # This would be populated from QualityController analysis
        return [
            "Code quality",
            "Testing coverage",
            "Documentation",
        ]

    def _get_available_agents(self, phase: str) -> list:
        """Get agents available in phase."""
        agents_by_phase = {
            "discovery": [
                "SocraticCounselor",
                "ContextAnalyzer",
                "KnowledgeManager",
            ],
            "analysis": [
                "CodeGenerator",
                "QualityController",
                "ContextAnalyzer",
            ],
            "design": [
                "CodeGenerator",
                "QualityController",
                "ProjectManager",
            ],
            "implementation": [
                "CodeValidator",
                "CodeGenerator",
                "QualityController",
            ],
        }
        return agents_by_phase.get(phase, [])


class WorkflowManager:
    """
    Manages complete workflows across multiple agents.

    A workflow is a sequence of agent executions that guide a user through
    one or more maturity phases.
    """

    def __init__(
        self,
        orchestrator: MaturityAwareOrchestrator,
        integration: SocratesIntegration,
    ):
        """
        Initialize workflow manager.

        Args:
            orchestrator: MaturityAwareOrchestrator instance
            integration: SocratesIntegration instance
        """
        self.orchestrator = orchestrator
        self.integration = integration
        self.logger = logging.getLogger(__name__)
        self._workflows: Dict[str, Dict[str, Any]] = {}

    def start_discovery_workflow(
        self,
        user_id: str,
        project_id: str,
        project_description: str,
    ) -> str:
        """
        Start discovery phase workflow.

        Args:
            user_id: User ID
            project_id: Project ID
            project_description: Description of project

        Returns:
            Workflow ID
        """
        workflow_id = f"discovery_{user_id}_{project_id}"

        workflow = {
            "phase": "discovery",
            "user_id": user_id,
            "project_id": project_id,
            "steps": [
                {
                    "agent": "socratic_counselor",
                    "action": "guide",
                    "data": {"topic": "problem_definition"},
                },
                {
                    "agent": "context_analyzer",
                    "action": "analyze",
                    "data": {"description": project_description},
                },
            ],
            "completed_steps": [],
            "results": {},
        }

        self._workflows[workflow_id] = workflow
        self.logger.info(f"Started discovery workflow: {workflow_id}")
        return workflow_id

    def start_analysis_workflow(
        self,
        user_id: str,
        project_id: str,
        code: str,
    ) -> str:
        """
        Start analysis phase workflow.

        Args:
            user_id: User ID
            project_id: Project ID
            code: Code to analyze

        Returns:
            Workflow ID
        """
        workflow_id = f"analysis_{user_id}_{project_id}"

        workflow = {
            "phase": "analysis",
            "user_id": user_id,
            "project_id": project_id,
            "steps": [
                {
                    "agent": "quality_controller",
                    "action": "detect_weak_areas",
                    "data": {"code": code},
                },
                {
                    "agent": "code_generator",
                    "action": "suggest_improvements",
                    "data": {"code": code},
                },
            ],
            "completed_steps": [],
            "results": {},
        }

        self._workflows[workflow_id] = workflow
        self.logger.info(f"Started analysis workflow: {workflow_id}")
        return workflow_id

    def execute_workflow_step(
        self,
        workflow_id: str,
    ) -> bool:
        """
        Execute next step in a workflow.

        Args:
            workflow_id: Workflow ID

        Returns:
            True if step executed successfully
        """
        if workflow_id not in self._workflows:
            self.logger.error(f"Workflow not found: {workflow_id}")
            return False

        workflow = self._workflows[workflow_id]
        if len(workflow["completed_steps"]) >= len(workflow["steps"]):
            self.logger.info(f"Workflow complete: {workflow_id}")
            return False

        step_idx = len(workflow["completed_steps"])
        step = workflow["steps"][step_idx]

        # Execute step
        try:
            response = self.orchestrator.process_request(
                agent_name=step["agent"],
                request={
                    "action": step["action"],
                    "user_id": workflow["user_id"],
                    **step["data"],
                },
                enforce_gating=True,
            )

            workflow["completed_steps"].append(step)
            workflow["results"][step["agent"]] = response

            self.logger.info(f"Completed step in workflow: {workflow_id}")
            return True

        except Exception as e:
            self.logger.error(f"Error executing workflow step: {e}")
            return False

    def complete_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Complete a workflow and return results.

        Args:
            workflow_id: Workflow ID

        Returns:
            Workflow results
        """
        if workflow_id not in self._workflows:
            return {"error": f"Workflow not found: {workflow_id}"}

        workflow = self._workflows.pop(workflow_id)
        return {
            "workflow_id": workflow_id,
            "phase": workflow["phase"],
            "completed_steps": len(workflow["completed_steps"]),
            "results": workflow["results"],
        }
