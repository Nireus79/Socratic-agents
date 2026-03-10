"""Conflict Detector Agent - Conflict detection and resolution."""

from typing import Any, Dict, Optional, List
from .base import BaseAgent


class ConflictDetector(BaseAgent):
    """Agent that detects and helps resolve conflicts."""

    def __init__(self, llm_client: Optional[Any] = None):
        """Initialize the Conflict Detector."""
        super().__init__(name="ConflictDetector", llm_client=llm_client)
        self.conflicts: List[Dict[str, Any]] = []

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process conflict detection requests."""
        action = request.get("action", "detect")
        if action == "detect":
            return self.detect_conflicts(request.get("items"))
        elif action == "resolve":
            return self.resolve_conflict(request.get("conflict_id"))
        elif action == "list":
            return self.list_conflicts()
        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    def detect_conflicts(self, items: List[Any]) -> Dict[str, Any]:
        """Detect conflicts in items."""
        if not items:
            return {"status": "error", "message": "Items required"}
        conflicts = []
        if len(items) > 1:
            for i, item in enumerate(items[:-1]):
                for j, other in enumerate(items[i+1:]):
                    if str(item) == str(other):
                        conflicts.append({"type": "duplicate", "items": [i, j+i+1]})
        return {"status": "success", "agent": self.name, "conflicts_found": len(conflicts), "conflicts": conflicts}

    def resolve_conflict(self, conflict_id: str) -> Dict[str, Any]:
        """Resolve a conflict."""
        if not conflict_id:
            return {"status": "error", "message": "Conflict ID required"}
        return {"status": "success", "agent": self.name, "conflict_id": conflict_id, "resolved": True}

    def list_conflicts(self) -> Dict[str, Any]:
        """List detected conflicts."""
        return {"status": "success", "agent": self.name, "conflicts_count": len(self.conflicts), "conflicts": self.conflicts}
