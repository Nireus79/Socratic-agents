"""Constitutional AI governance integration for agents."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from socratic_morality.governor import Governor
from socratic_morality.governor.decision import DecisionType, GovernorDecision


class GovernedAgent:
    """Wrapper that adds constitutional governance to any agent."""

    def __init__(self, agent: Any, governor: Governor, agent_name: Optional[str] = None):
        """
        Wrap an agent with Governor constraints.

        Args:
            agent: The agent to wrap
            governor: Governor instance for constitutional checks
            agent_name: Name for governance context (defaults to agent.name)
        """
        self.agent = agent
        self.governor = governor
        self.agent_name = agent_name or getattr(agent, "name", "unknown_agent")
        self.logger = logging.getLogger(f"socratic_agents.governance.{self.agent_name}")

    async def evaluate_action(
        self,
        action: str,
        purpose: str = "",
        context: Optional[Dict[str, Any]] = None,
        high_impact: bool = False,
    ) -> GovernorDecision:
        """
        Evaluate an action against the constitution.

        Args:
            action: Description of the action to evaluate
            purpose: Purpose/intent of the action
            context: Additional context for evaluation
            high_impact: Whether this is a high-impact decision

        Returns:
            GovernorDecision with allow/deny/escalate/block status
        """
        decision = await self.governor.evaluate(
            action=action,
            purpose=purpose,
            actor=self.agent_name,
            context=context or {},
            high_impact=high_impact,
        )
        return decision

    async def process_with_governance(
        self,
        request: Dict[str, Any],
        action_description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Process a request with constitutional checks.

        Args:
            request: The request to process
            action_description: Optional description of the action for governance

        Returns:
            Response with constitutional evaluation included

        Raises:
            PermissionError: If action is blocked by constitution
        """
        # Generate action description from request if not provided
        if not action_description:
            action_type = request.get("action", "unknown_action")
            action_description = f"Agent {self.agent_name} performing {action_type}"

        # Evaluate action against constitution
        decision = await self.evaluate_action(
            action=action_description,
            context={"request_type": request.get("action", "unknown")},
            high_impact=request.get("high_impact", False),
        )

        # Handle decision based on type
        if decision.is_blocked():
            self.logger.error(f"Constitutional violation blocked: {decision.reasoning}")
            raise PermissionError(f"Constitutional violation: {decision.reasoning}")

        if decision.requires_escalation():
            self.logger.warning(f"Escalation required: {decision.reasoning}")
            # For now, log escalation. In production, would notify governance team
            # response = await decision.escalate()

        # If allowed, proceed with action
        if decision.allowed:
            self.logger.info(f"Action approved by Governor: {action_description}")
            # Proceed with original agent processing
            if hasattr(self.agent, "process_async"):
                response = await self.agent.process_async(request)
            else:
                response = self.agent.process(request)

            # Add governance metadata to response
            response["__governance__"] = {
                "decision_id": decision.decision_id,
                "allowed": True,
                "decision_type": decision.decision_type.value,
                "confidence": decision.confidence,
            }
            return response
        else:
            self.logger.warning(f"Action denied by Governor: {decision.reasoning}")
            return {
                "status": "error",
                "message": f"Action denied: {decision.reasoning}",
                "__governance__": {
                    "decision_id": decision.decision_id,
                    "allowed": False,
                    "decision_type": decision.decision_type.value,
                    "violations": [
                        {
                            "principle": v.principle,
                            "severity": v.severity,
                            "description": v.description,
                        }
                        for v in decision.violations
                    ],
                },
            }

    async def process_async(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process request asynchronously with governance."""
        return await self.process_with_governance(request)

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process request synchronously (wraps async for sync compatibility)."""
        import asyncio

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self.process_async(request))

    def __getattr__(self, name: str) -> Any:
        """Delegate unknown attributes to wrapped agent."""
        return getattr(self.agent, name)


class GovernanceAdapter:
    """Adapter for integrating Governor with agent orchestration."""

    def __init__(self, governor: Governor):
        """
        Initialize governance adapter.

        Args:
            governor: Governor instance for constitutional checks
        """
        self.governor = governor
        self.logger = logging.getLogger("socratic_agents.governance.adapter")

    def wrap_agent(self, agent: Any, agent_name: Optional[str] = None) -> GovernedAgent:
        """
        Wrap an agent with governance.

        Args:
            agent: Agent to wrap
            agent_name: Optional agent name for governance context

        Returns:
            GovernedAgent wrapper with constitutional checks
        """
        governed = GovernedAgent(agent, self.governor, agent_name)
        self.logger.info(f"Wrapped agent {agent_name or getattr(agent, 'name', 'unknown')}")
        return governed

    async def evaluate_and_execute(
        self,
        agent: Any,
        request: Dict[str, Any],
        action_description: Optional[str] = None,
        agent_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate action and execute if approved.

        Args:
            agent: Agent to execute
            request: Request to process
            action_description: Optional action description
            agent_name: Optional agent name for context

        Returns:
            Response with governance metadata
        """
        governed = self.wrap_agent(agent, agent_name)
        return await governed.process_with_governance(request, action_description)
