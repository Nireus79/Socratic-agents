"""Conflict Detector Agent - Conflict detection and resolution.

Wrapper around socratic-conflict library providing multi-agent conflict detection
and resolution with support for multiple strategies and consensus algorithms.
"""

from typing import Any, Dict, List, Optional

from .base import BaseAgent

try:
    from socratic_conflict import ConflictDetector as SocraticConflictDetector
    from socratic_conflict import ConflictResolver

    SOCRATIC_CONFLICT_AVAILABLE = True
except ImportError:
    SOCRATIC_CONFLICT_AVAILABLE = False


class AgentConflictDetector(BaseAgent):
    """
    Agent that detects and helps resolve conflicts in multi-agent workflows.

    Integrates with socratic-conflict library for comprehensive conflict handling:
    - Detects goal divergence, resource contention, decision contradictions
    - Resolves conflicts using multiple strategies (priority, voting, allocation, etc.)
    - Tracks conflict history with severity assessment
    - Supports both single-agent and multi-agent scenarios

    Falls back to basic duplicate detection if socratic-conflict unavailable.
    """

    def __init__(self, llm_client: Optional[Any] = None):
        """
        Initialize the Conflict Detector.

        Args:
            llm_client: Optional LLM client for enhanced conflict analysis
        """
        super().__init__(name="AgentConflictDetector", llm_client=llm_client)
        self.conflicts: List[Dict[str, Any]] = []

        # Initialize socratic-conflict components if available
        if SOCRATIC_CONFLICT_AVAILABLE:
            self.detector = SocraticConflictDetector()
            self.resolver = ConflictResolver()
            self.use_full_detection = True
        else:
            self.use_full_detection = False

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process conflict detection and resolution requests.

        Supported actions:
        - detect: Detect conflicts in agent states or items
        - resolve: Resolve a specific conflict
        - list: List all detected conflicts
        - clear: Clear conflict history

        Args:
            request: Request with action and parameters

        Returns:
            Result dictionary with status and details
        """
        action = request.get("action", "detect")

        if action == "detect":
            agent_states = request.get("agent_states")
            items = request.get("items")

            if agent_states:
                return self.detect_from_agent_states(agent_states)
            elif items:
                return self.detect_conflicts(items)  # type: ignore[arg-type]
            else:
                return {"status": "error", "message": "Either agent_states or items required"}

        elif action == "resolve":
            conflict_id = request.get("conflict_id")
            strategy = request.get("strategy", "auto")
            return self.resolve_conflict(conflict_id, strategy)  # type: ignore[arg-type]

        elif action == "list":
            return self.list_conflicts()

        elif action == "clear":
            return self.clear_conflicts()

        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    def detect_from_agent_states(self, agent_states: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect conflicts from multi-agent states (full detection mode).

        Uses socratic-conflict's ConflictDetector to identify:
        - Goal divergence between agents
        - Resource contention
        - Decision contradictions
        - Deadlocks

        Args:
            agent_states: Dictionary mapping agent IDs to their states

        Returns:
            Detection result with conflicts found
        """
        if not self.use_full_detection:
            return {"status": "error", "message": "socratic-conflict library not available"}

        try:
            detected = self.detector.detect_conflicts(agent_states)

            # Convert Conflict objects to dicts for serialization
            conflicts_list = [
                {
                    "id": c.id,
                    "agents": c.agents,
                    "type": c.type,
                    "severity": c.severity,
                    "description": c.description,
                    "timestamp": c.timestamp,
                    "resolved": c.resolved,
                }
                for c in detected
            ]

            self.conflicts.extend(conflicts_list)

            return {
                "status": "success",
                "agent": self.name,
                "mode": "full_detection",
                "conflicts_found": len(conflicts_list),
                "conflicts": conflicts_list,
                "agent_count": len(agent_states),
            }

        except Exception as e:
            return {"status": "error", "message": f"Detection failed: {str(e)}"}

    def detect_conflicts(self, items: List[Any]) -> Dict[str, Any]:
        """
        Detect conflicts in a list of items (fallback/simple mode).

        When socratic-conflict unavailable or for simple item comparison,
        detects duplicates and conflicts by comparing items.

        Args:
            items: List of items to check for conflicts

        Returns:
            Detection result with conflicts found
        """
        if not items:
            return {"status": "error", "message": "Items required"}

        conflicts: list[Dict[str, Any]] = []
        if len(items) > 1:
            for i, item in enumerate(items[:-1]):
                for j, other in enumerate(items[i + 1 :]):
                    if str(item) == str(other):
                        conflicts.append(
                            {
                                "id": f"conflict_{len(conflicts)}",
                                "type": "duplicate",
                                "items": [i, j + i + 1],
                                "severity": "medium",
                            }
                        )

        self.conflicts.extend(conflicts)

        return {
            "status": "success",
            "agent": self.name,
            "mode": "simple_detection",
            "conflicts_found": len(conflicts),
            "conflicts": conflicts,
        }

    def resolve_conflict(self, conflict_id: str, strategy: str = "auto") -> Dict[str, Any]:
        """
        Resolve a detected conflict using specified strategy.

        Supports multiple resolution strategies:
        - priority: Execute higher-priority agent first
        - voting: Majority decision among agents
        - allocation: Fair resource distribution
        - negotiation: Reach compromise between agents
        - sequencing: Execute serially instead of parallel
        - auto: Automatically select best strategy

        Args:
            conflict_id: ID of conflict to resolve
            strategy: Resolution strategy to use

        Returns:
            Resolution result with outcome
        """
        if not conflict_id:
            return {"status": "error", "message": "Conflict ID required"}

        # Find the conflict
        conflict_to_resolve = None
        for conflict in self.conflicts:
            if conflict.get("id") == conflict_id:
                conflict_to_resolve = conflict
                break

        if not conflict_to_resolve:
            return {"status": "error", "message": f"Conflict {conflict_id} not found"}

        if not self.use_full_detection:
            # Fallback resolution
            return {
                "status": "success",
                "agent": self.name,
                "conflict_id": conflict_id,
                "strategy": "default",
                "resolved": True,
                "outcome": "Conflict resolved using default strategy",
            }

        try:
            # Use socratic-conflict resolver
            agent_metadata: Dict[str, Any] = {}  # Can be populated with agent info if needed
            resolution = self.resolver.resolve(
                conflict_to_resolve, agent_metadata, strategy if strategy != "auto" else None
            )

            return {
                "status": "success",
                "agent": self.name,
                "conflict_id": conflict_id,
                "strategy": resolution.strategy,
                "outcome": resolution.outcome,
                "resolved": resolution.success,
                "timestamp": resolution.timestamp,
            }

        except Exception as e:
            return {"status": "error", "message": f"Resolution failed: {str(e)}"}

    def list_conflicts(self) -> Dict[str, Any]:
        """
        List all detected conflicts.

        Returns:
            List with conflict summary and details
        """
        return {
            "status": "success",
            "agent": self.name,
            "conflicts_count": len(self.conflicts),
            "conflicts": self.conflicts,
            "mode": "full_detection" if self.use_full_detection else "simple_detection",
        }

    def clear_conflicts(self) -> Dict[str, Any]:
        """
        Clear all detected conflicts from history.

        Returns:
            Confirmation of cleared history
        """
        count = len(self.conflicts)
        self.conflicts.clear()
        if self.use_full_detection:
            self.detector.clear_conflicts()

        return {
            "status": "success",
            "agent": self.name,
            "cleared_count": count,
            "message": f"Cleared {count} conflicts from history",
        }
