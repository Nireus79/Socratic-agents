"""
Phase 5: Pure Orchestration Layer

Coordinates agents with maturity-driven workflow gating and feedback loops.

Key responsibilities:
1. Route requests to agents (with caching)
2. Apply maturity-driven workflow gating (QualityController gates based on thresholds)
3. Manage skill application and effectiveness feedback
4. Orchestrate multi-agent workflows
5. Emit coordination events
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import logging

from socrates_maturity import MaturityCalculator
from .skill_applier import SkillApplier


class CoordinationEvent(Enum):
    """Events emitted during coordination."""
    WORKFLOW_STARTED = "workflow_started"
    PHASE_GATING_CHECK = "phase_gating_check"
    PHASE_GATE_PASSED = "phase_gate_passed"
    PHASE_GATE_FAILED = "phase_gate_failed"
    SKILLS_GENERATED = "skills_generated"
    SKILLS_APPLIED = "skills_applied"
    AGENT_EXECUTED = "agent_executed"
    FEEDBACK_RECORDED = "feedback_recorded"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"


# Maturity thresholds for workflow gating
MATURITY_PHASE_THRESHOLDS = {
    "discovery": (0.0, 0.25),      # 0-25%
    "analysis": (0.25, 0.50),       # 25-50%
    "design": (0.50, 0.75),         # 50-75%
    "implementation": (0.75, 1.0),  # 75-100%
}

# Quality thresholds for agent gating
QUALITY_GATE_THRESHOLDS = {
    "discovery": 0.0,           # No bar - focus on understanding problem
    "analysis": 0.2,            # Very low bar - requirement gathering
    "design": 0.4,              # Moderate bar - architecture matters
    "implementation": 0.6,      # High bar - code quality critical
}


@dataclass
class AgentRequest:
    """Structured request to execute an agent."""
    agent_name: str
    action: str
    data: Dict[str, Any]
    workflow_id: Optional[str] = None
    user_id: Optional[str] = None


@dataclass
class AgentResponse:
    """Response from agent execution."""
    status: str  # "success", "error", "gated"
    agent: str
    action: str
    data: Dict[str, Any]
    gated: bool = False  # True if blocked by workflow gating
    gating_reason: Optional[str] = None


class PureOrchestrator:
    """
    Pure orchestration logic without infrastructure dependencies.

    Takes agents and utilities as dependencies, implements maturity-driven
    coordination without direct database or filesystem access.
    """

    def __init__(
        self,
        agents: Dict[str, Any],
        get_maturity: Callable[[str, str], float],
        get_learning_effectiveness: Callable[[str], float],
        on_event: Optional[Callable[[CoordinationEvent, Dict[str, Any]], None]] = None,
    ):
        """
        Initialize pure orchestrator.

        Args:
            agents: Dict mapping agent names to agent instances
            get_maturity: Callable that returns maturity for (user_id, phase)
            get_learning_effectiveness: Callable that returns effectiveness for agent
            on_event: Optional callback for coordination events
        """
        self.agents = agents
        self.get_maturity = get_maturity
        self.get_learning_effectiveness = get_learning_effectiveness
        self.on_event = on_event or (lambda _event, _data: None)
        self.logger = logging.getLogger(__name__)

        # Track active workflows
        self._workflows: Dict[str, Dict[str, Any]] = {}

    # =========================================================================
    # CORE REQUEST ROUTING
    # =========================================================================

    def can_execute_request(
        self, agent_name: str, current_phase: str, current_maturity: float
    ) -> tuple[bool, Optional[str]]:
        """
        Check if request can be executed based on maturity gating.

        Args:
            agent_name: Name of agent to execute
            current_phase: Current maturity phase ("discovery", "analysis", etc.)
            current_maturity: Overall maturity score (0.0-1.0)

        Returns:
            (can_execute, reason_if_blocked)
        """
        # Quality-based gating: agent must be above quality threshold for phase
        quality_threshold = QUALITY_GATE_THRESHOLDS.get(current_phase, 0.4)

        # Phase-based gating: agent only available in certain phases
        phase_gates = self._get_phase_gates(agent_name)

        if current_phase not in phase_gates:
            reason = (
                f"Agent {agent_name} not available in {current_phase} phase. "
                f"Available in: {', '.join(phase_gates)}"
            )
            return False, reason

        # Quality threshold: overall maturity must exceed threshold
        if current_maturity < quality_threshold:
            reason = (
                f"Code quality too low ({current_maturity:.2f}) "
                f"for {current_phase} phase (requires {quality_threshold:.2f})"
            )
            return False, reason

        return True, None

    def execute_request(
        self, request: AgentRequest, current_maturity: float = None, current_phase: str = None
    ) -> AgentResponse:
        """
        Execute agent request with maturity-driven gating.

        Args:
            request: AgentRequest object
            current_maturity: Overall maturity (0.0-1.0). If None, assume ready.
            current_phase: Current phase. If None, estimate from maturity.

        Returns:
            AgentResponse with result or gating reason
        """
        self._emit_event(
            CoordinationEvent.WORKFLOW_STARTED,
            {"agent": request.agent_name, "action": request.action},
        )

        # Estimate phase if not provided
        if current_phase is None:
            current_phase = MaturityCalculator.estimate_current_phase(
                current_maturity or 0.5
            )

        # Check gating
        can_execute, gating_reason = self.can_execute_request(
            request.agent_name, current_phase, current_maturity or 0.5
        )

        self._emit_event(
            CoordinationEvent.PHASE_GATING_CHECK,
            {
                "agent": request.agent_name,
                "phase": current_phase,
                "maturity": current_maturity or 0.5,
                "can_execute": can_execute,
            },
        )

        if not can_execute:
            self._emit_event(
                CoordinationEvent.PHASE_GATE_FAILED,
                {"agent": request.agent_name, "reason": gating_reason},
            )
            return AgentResponse(
                status="gated",
                agent=request.agent_name,
                action=request.action,
                data={},
                gated=True,
                gating_reason=gating_reason,
            )

        self._emit_event(
            CoordinationEvent.PHASE_GATE_PASSED,
            {"agent": request.agent_name},
        )

        # Execute agent
        agent = self.agents.get(request.agent_name)
        if not agent:
            return AgentResponse(
                status="error",
                agent=request.agent_name,
                action=request.action,
                data={"error": f"Agent not found: {request.agent_name}"},
            )

        try:
            result = agent.process({"action": request.action, **request.data})

            self._emit_event(
                CoordinationEvent.AGENT_EXECUTED,
                {"agent": request.agent_name, "status": result.get("status")},
            )

            return AgentResponse(
                status=result.get("status", "unknown"),
                agent=request.agent_name,
                action=request.action,
                data=result,
            )
        except Exception as e:
            self.logger.error(f"Agent {request.agent_name} error: {e}")
            self._emit_event(
                CoordinationEvent.WORKFLOW_FAILED,
                {"agent": request.agent_name, "error": str(e)},
            )
            return AgentResponse(
                status="error",
                agent=request.agent_name,
                action=request.action,
                data={"error": str(e)},
            )

    # =========================================================================
    # SKILL APPLICATION AND FEEDBACK
    # =========================================================================

    def apply_skills_to_agents(
        self, skills: List[Any], agents_state: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """
        Apply generated skills to target agents.

        Args:
            skills: List of AgentSkill objects from SkillGenerator
            agents_state: Current state of agents (for validation)

        Returns:
            Dict mapping agent names to list of applied skill IDs
        """
        applied: Dict[str, List[str]] = {}
        applier = SkillApplier()

        for skill in skills:
            target_agent = skill.target_agent

            # Validate agent exists
            if target_agent not in self.agents:
                self.logger.warning(f"Skill target agent not found: {target_agent}")
                continue

            # Apply skill
            agent = self.agents[target_agent]
            if applier.apply_skill(agent, skill):
                if target_agent not in applied:
                    applied[target_agent] = []
                applied[target_agent].append(skill.id)

        self._emit_event(
            CoordinationEvent.SKILLS_APPLIED,
            {"agents_affected": list(applied.keys()), "total_skills": len(skills)},
        )

        return applied

    def record_feedback(
        self,
        agent_name: str,
        action: str,
        effectiveness: float,
        user_id: str,
    ) -> bool:
        """
        Record feedback about agent execution effectiveness.

        This allows the system to track which skills/agents are actually helping
        and should inform future skill generation.

        Args:
            agent_name: Agent that was executed
            action: Action that was performed
            effectiveness: Score 0.0-1.0 of how well it worked
            user_id: User ID for tracking

        Returns:
            True if recorded successfully
        """
        feedback = {
            "agent": agent_name,
            "action": action,
            "effectiveness": effectiveness,
            "user_id": user_id,
        }

        self._emit_event(CoordinationEvent.FEEDBACK_RECORDED, feedback)

        return True

    # =========================================================================
    # WORKFLOW COMPOSITION
    # =========================================================================

    def start_workflow(
        self, workflow_id: str, initial_data: Dict[str, Any]
    ) -> str:
        """
        Start a new multi-agent workflow.

        Args:
            workflow_id: Unique ID for this workflow
            initial_data: Initial data for the workflow

        Returns:
            Workflow ID
        """
        self._workflows[workflow_id] = {
            "id": workflow_id,
            "data": initial_data,
            "executed_agents": [],
            "results": {},
        }

        return workflow_id

    def execute_workflow_step(
        self, workflow_id: str, request: AgentRequest
    ) -> AgentResponse:
        """
        Execute a step in a multi-agent workflow.

        Args:
            workflow_id: ID of the workflow
            request: AgentRequest to execute

        Returns:
            AgentResponse with result
        """
        if workflow_id not in self._workflows:
            return AgentResponse(
                status="error",
                agent=request.agent_name,
                action=request.action,
                data={"error": f"Workflow not found: {workflow_id}"},
            )

        response = self.execute_request(request)

        # Track execution
        workflow = self._workflows[workflow_id]
        workflow["executed_agents"].append(request.agent_name)
        workflow["results"][request.agent_name] = response.data

        return response

    def complete_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Complete a workflow and return results.

        Args:
            workflow_id: ID of the workflow

        Returns:
            Workflow results
        """
        workflow = self._workflows.pop(workflow_id, None)
        if not workflow:
            return {"error": f"Workflow not found: {workflow_id}"}

        self._emit_event(
            CoordinationEvent.WORKFLOW_COMPLETED,
            {
                "workflow_id": workflow_id,
                "agents_executed": workflow["executed_agents"],
                "results_count": len(workflow["results"]),
            },
        )

        return workflow

    # =========================================================================
    # COORDINATION QUERIES
    # =========================================================================

    def get_available_agents_for_phase(self, phase: str) -> List[str]:
        """
        Get list of agents available in a specific phase.

        Args:
            phase: Maturity phase ("discovery", "analysis", "design", "implementation")

        Returns:
            List of available agent names
        """
        available = []
        for agent_name in self.agents.keys():
            phase_gates = self._get_phase_gates(agent_name)
            if phase in phase_gates:
                available.append(agent_name)
        return available

    def get_required_quality_for_phase(self, phase: str) -> float:
        """
        Get minimum quality threshold required for a phase.

        Args:
            phase: Maturity phase

        Returns:
            Quality threshold (0.0-1.0)
        """
        return QUALITY_GATE_THRESHOLDS.get(phase, 0.4)

    def estimate_phase(self, maturity: float) -> str:
        """
        Estimate current phase from maturity score.

        Args:
            maturity: Overall maturity (0.0-1.0)

        Returns:
            Phase name
        """
        return MaturityCalculator.estimate_current_phase(maturity)

    # =========================================================================
    # PRIVATE HELPERS
    # =========================================================================

    def _get_phase_gates(self, agent_name: str) -> List[str]:
        """
        Get which phases an agent is available in.

        This is a simple mapping - in production, this could be configurable.
        """
        # Agents available in all phases
        all_phases = ["discovery", "analysis", "design", "implementation"]

        # Phase-specific mappings
        phase_specific = {
            "socratic_counselor": ["discovery", "analysis"],
            "code_generator": ["analysis", "design", "implementation"],
            "quality_controller": ["analysis", "design", "implementation"],
            "code_validator": ["design", "implementation"],
            "knowledge_manager": all_phases,  # Always available
            "learning_agent": all_phases,     # Always available
            "skill_generator": all_phases,    # Always available
        }

        return phase_specific.get(agent_name, all_phases)

    def _emit_event(self, event: CoordinationEvent, data: Dict[str, Any]) -> None:
        """Emit a coordination event."""
        try:
            self.on_event(event, data)
        except Exception as e:
            self.logger.error(f"Error emitting event {event}: {e}")
