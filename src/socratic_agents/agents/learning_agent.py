"""Learning Agent - Continuous learning and performance improvement."""

from typing import Any, Dict, Optional, List
from .base import BaseAgent


class LearningAgent(BaseAgent):
    """Agent that learns from interactions and improves over time."""

    def __init__(self, llm_client: Optional[Any] = None):
        """Initialize the Learning Agent."""
        super().__init__(name="LearningAgent", llm_client=llm_client)
        self.interactions: List[Dict[str, Any]] = []
        self.patterns: List[str] = []

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process learning requests."""
        action = request.get("action", "record")
        if action == "record":
            return self.record_interaction(request.get("interaction"))
        elif action == "analyze":
            return self.analyze_patterns()
        elif action == "suggest":
            return self.suggest_improvements()
        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    def record_interaction(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """Record an interaction for learning."""
        if not interaction:
            return {"status": "error", "message": "Interaction required"}
        self.interactions.append({"data": interaction})
        return {"status": "success", "agent": self.name, "recorded": True, "total_interactions": len(self.interactions)}

    def analyze_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in recorded interactions."""
        if not self.interactions:
            return {"status": "success", "agent": self.name, "patterns": [], "message": "No interactions recorded"}
        self.patterns = [f"{len(self.interactions)} interactions recorded", "Learning system active"]
        return {"status": "success", "agent": self.name, "patterns_found": len(self.patterns), "patterns": self.patterns}

    def suggest_improvements(self) -> Dict[str, Any]:
        """Suggest improvements based on learning."""
        suggestions = ["Record more interactions for patterns", "Analyze recent interactions", "Share learnings with agents"]
        return {"status": "success", "agent": self.name, "suggestions": suggestions}
