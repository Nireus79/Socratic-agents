"""System Monitor Agent - System health and performance monitoring."""

from typing import Any, Dict, Optional, List
from .base import BaseAgent


class SystemMonitor(BaseAgent):
    """Agent that monitors system health and performance."""

    def __init__(self, llm_client: Optional[Any] = None):
        """Initialize the System Monitor."""
        super().__init__(name="SystemMonitor", llm_client=llm_client)
        self.metrics: Dict[str, Any] = {}
        self.health_score = 100.0

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process system monitoring requests."""
        action = request.get("action", "status")
        if action == "status":
            return self.get_status()
        elif action == "metrics":
            return self.get_metrics()
        elif action == "alert":
            return self.check_alerts()
        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    def get_status(self) -> Dict[str, Any]:
        """Get system status."""
        return {
            "status": "success",
            "agent": self.name,
            "health_score": self.health_score,
            "system_status": "healthy",
            "uptime": "100%",
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Get system metrics."""
        self.metrics = {"cpu": "45%", "memory": "62%", "disk": "71%", "response_time": "125ms"}
        return {"status": "success", "agent": self.name, "metrics": self.metrics}

    def check_alerts(self) -> Dict[str, Any]:
        """Check for system alerts."""
        alerts = [] if self.health_score > 80 else ["System performance degraded"]
        return {
            "status": "success",
            "agent": self.name,
            "alerts": alerts,
            "alert_count": len(alerts),
        }
