"""
Phase 6: Integration Layer

Adapts PureOrchestrator to work with the existing Socrates orchestrator.
Bridges pure coordination logic with infrastructure-aware request handling.
"""

import logging
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from socrates_maturity import MaturityCalculator

from .orchestrator import AgentRequest, PureOrchestrator


class IntegrationMode(Enum):
    """Integration modes for orchestrator."""

    PURE = "pure"  # Use PureOrchestrator only
    HYBRID = "hybrid"  # Use PureOrchestrator with gating
    LEGACY = "legacy"  # Use existing orchestrator (no gating)


class OrchestratorAdapter:
    """
    Adapts PureOrchestrator for use with existing Socrates infrastructure.

    This adapter:
    1. Routes maturity/effectiveness data to PureOrchestrator
    2. Translates between request formats
    3. Handles gating decisions
    4. Records feedback
    5. Manages workflow state
    """

    def __init__(
        self,
        pure_orchestrator: PureOrchestrator,
        mode: IntegrationMode = IntegrationMode.HYBRID,
    ):
        """
        Initialize the adapter.

        Args:
            pure_orchestrator: PureOrchestrator instance
            mode: Integration mode (pure, hybrid, or legacy)
        """
        self.pure_orchestrator = pure_orchestrator
        self.mode = mode
        self.logger = logging.getLogger(__name__)

        # Track maturity scores per user
        self._maturity_cache: Dict[str, Dict[str, float]] = {}

        # Track feedback for learning
        self._feedback_log: list = []

    def execute_with_gating(
        self,
        agent_name: str,
        action: str,
        data: Dict[str, Any],
        user_id: Optional[str] = None,
        current_maturity: Optional[float] = None,
        current_phase: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute agent request with maturity-driven gating.

        Args:
            agent_name: Target agent name
            action: Agent action to perform
            data: Request data
            user_id: User ID (for tracking maturity)
            current_maturity: Overall maturity (0.0-1.0). If None, estimated.
            current_phase: Current phase. If None, estimated from maturity.

        Returns:
            Response dict with status, data, and gating info
        """
        if self.mode == IntegrationMode.LEGACY:
            # Legacy mode: skip gating, just execute
            return self._execute_agent_directly(agent_name, action, data)

        # Estimate maturity if not provided
        if current_maturity is None:
            current_maturity = self._get_maturity(user_id, current_phase or "analysis")

        # Estimate phase if not provided
        if current_phase is None:
            current_phase = MaturityCalculator.estimate_current_phase(current_maturity)

        # Create request
        request = AgentRequest(
            agent_name=agent_name,
            action=action,
            data=data,
            user_id=user_id,
        )

        # Execute with gating
        response = self.pure_orchestrator.execute_request(
            request, current_maturity=current_maturity, current_phase=current_phase
        )

        # Handle gated response
        if response.gated:
            self.logger.warning(f"Request gated: {agent_name}.{action} - {response.gating_reason}")
            return {
                "status": "gated",
                "agent": agent_name,
                "action": action,
                "error": response.gating_reason,
                "suggestion": self._get_next_steps(user_id, current_phase, current_maturity),
            }

        # Execute agent directly if not gated
        return self._execute_agent_directly(agent_name, action, data, response)

    def apply_skills(
        self,
        skills: list,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Apply skills to agents.

        Args:
            skills: List of AgentSkill objects
            user_id: User ID

        Returns:
            Dict with applied skills info
        """
        applied = self.pure_orchestrator.apply_skills_to_agents(
            skills, self.pure_orchestrator.agents
        )

        return {
            "status": "success",
            "applied": applied,
            "total_skills": len(skills),
            "agents_affected": len(applied),
        }

    def record_effectiveness(
        self,
        agent_name: str,
        action: str,
        effectiveness: float,  # 0.0-1.0
        user_id: Optional[str] = None,
    ) -> bool:
        """
        Record how effective an agent action was.

        Args:
            agent_name: Agent that was executed
            action: Action performed
            effectiveness: Score 0.0-1.0 of effectiveness
            user_id: User ID

        Returns:
            True if recorded successfully
        """
        success = self.pure_orchestrator.record_feedback(
            agent_name=agent_name,
            action=action,
            effectiveness=effectiveness,
            user_id=user_id or "system",
        )

        if success:
            self._feedback_log.append(
                {
                    "agent": agent_name,
                    "action": action,
                    "effectiveness": effectiveness,
                    "user_id": user_id,
                }
            )

        return success

    def get_agent_availability(self, current_phase: str, current_maturity: float) -> Dict[str, Any]:
        """
        Get which agents are available for the current state.

        Args:
            current_phase: Current maturity phase
            current_maturity: Current maturity score

        Returns:
            Dict with available agents and gating reasons for unavailable ones
        """
        available = self.pure_orchestrator.get_available_agents_for_phase(current_phase)
        quality_threshold = self.pure_orchestrator.get_required_quality_for_phase(current_phase)

        return {
            "phase": current_phase,
            "maturity": current_maturity,
            "quality_threshold": quality_threshold,
            "available_agents": available,
            "can_execute": current_maturity >= quality_threshold,
            "agents_count": len(available),
        }

    # =========================================================================
    # PRIVATE HELPERS
    # =========================================================================

    def _execute_agent_directly(
        self,
        agent_name: str,
        action: str,
        data: Dict[str, Any],
        pure_response: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Execute agent directly (infrastructure layer)."""
        agent = self.pure_orchestrator.agents.get(agent_name)
        if not agent:
            return {"status": "error", "error": f"Agent not found: {agent_name}"}

        try:
            result = agent.process({"action": action, **data})
            return result
        except Exception as e:
            self.logger.error(f"Agent execution error: {e}")
            return {
                "status": "error",
                "agent": agent_name,
                "error": str(e),
            }

    def _get_maturity(self, user_id: Optional[str], phase: str) -> float:
        """Get maturity for a user/phase."""
        if user_id and user_id in self._maturity_cache:
            return self._maturity_cache[user_id].get(phase, 0.5)
        return 0.5  # Default maturity

    def _get_next_steps(
        self, user_id: Optional[str], current_phase: str, current_maturity: float
    ) -> str:
        """Suggest next steps when request is gated."""
        available = self.pure_orchestrator.get_available_agents_for_phase(current_phase)
        threshold = self.pure_orchestrator.get_required_quality_for_phase(current_phase)

        if current_maturity < threshold:
            return (
                f"Code quality ({current_maturity:.0%}) below {current_phase} threshold "
                f"({threshold:.0%}). Improve code quality with available agents: "
                f"{', '.join(available[:3])}"
            )
        else:
            return f"Try available agents in {current_phase} phase: {', '.join(available)}"


class MaturityAwareOrchestrator:
    """
    Wrapper around existing Socrates orchestrator that adds maturity awareness.

    This orchestrator:
    1. Delegates to the existing orchestrator for infrastructure
    2. Uses PureOrchestrator for coordination decisions
    3. Enforces maturity-driven workflow gating
    4. Manages skill application and feedback
    """

    def __init__(
        self,
        existing_orchestrator: Any,  # Type is the existing AgentOrchestrator
        pure_orchestrator: PureOrchestrator,
        maturity_tracker: Optional[Callable] = None,
    ):
        """
        Initialize the maturity-aware wrapper.

        Args:
            existing_orchestrator: The current Socrates orchestrator
            pure_orchestrator: PureOrchestrator for coordination
            maturity_tracker: Optional callback to get maturity (user_id, phase) -> float
        """
        self.existing_orchestrator = existing_orchestrator
        self.pure_orchestrator = pure_orchestrator
        self.maturity_tracker = maturity_tracker
        self.logger = logging.getLogger(__name__)

        # Tracking
        self._request_count = 0
        self._gated_count = 0
        self._applied_skills: List[Dict[str, Any]] = []

    def process_request(
        self,
        agent_name: str,
        request: Dict[str, Any],
        enforce_gating: bool = True,
    ) -> Dict[str, Any]:
        """
        Process request with optional maturity gating.

        Args:
            agent_name: Name of the agent
            request: Request dict
            enforce_gating: Whether to enforce maturity gating

        Returns:
            Response dict
        """
        self._request_count += 1

        if not enforce_gating:
            # Skip gating, use existing orchestrator
            return self.existing_orchestrator.process_request(agent_name, request)

        # Get current maturity
        user_id = request.get("user_id")
        current_maturity = self._get_user_maturity(user_id)
        current_phase = MaturityCalculator.estimate_current_phase(current_maturity)

        # Check gating
        can_execute, reason = self.pure_orchestrator.can_execute_request(
            agent_name=agent_name,
            current_phase=current_phase,
            current_maturity=current_maturity,
        )

        if not can_execute:
            self._gated_count += 1
            self.logger.info(f"Request gated: {agent_name} - {reason}")
            return {
                "status": "gated",
                "agent": agent_name,
                "error": reason,
                "suggestion": self._suggest_alternatives(current_phase),
            }

        # Not gated, proceed with existing orchestrator
        return self.existing_orchestrator.process_request(agent_name, request)

    def get_stats(self) -> Dict[str, Any]:
        """Get orchestration statistics."""
        return {
            "total_requests": self._request_count,
            "gated_requests": self._gated_count,
            "pass_rate": (
                1.0 - (self._gated_count / self._request_count) if self._request_count > 0 else 1.0
            ),
            "skills_applied": len(self._applied_skills),
        }

    # =========================================================================
    # PRIVATE HELPERS
    # =========================================================================

    def _get_user_maturity(self, user_id: Optional[str]) -> float:
        """Get user's current maturity."""
        if self.maturity_tracker and user_id:
            try:
                return self.maturity_tracker(user_id)
            except Exception as e:
                self.logger.warning(f"Error getting maturity: {e}")
        return 0.5  # Default

    def _suggest_alternatives(self, current_phase: str) -> str:
        """Suggest available agents for current phase."""
        available = self.pure_orchestrator.get_available_agents_for_phase(current_phase)
        return f"Available agents in {current_phase}: {', '.join(available[:5])}"
