"""System Monitor Agent - System health, performance, and resource monitoring.

This agent:
1. Monitors system health and performance metrics
2. Tracks resource usage (CPU, memory, disk, network)
3. Detects performance anomalies
4. Manages system alerts and notifications
5. Tracks uptime and availability
6. Monitors API response times
7. Reports system diagnostics
8. Manages system thresholds and limits
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, cast

from .base import BaseAgent


class HealthMetric:
    """Represents a health metric."""

    def __init__(self, name: str, unit: str, threshold_warning: float, threshold_critical: float):
        self.name = name
        self.unit = unit
        self.threshold_warning = threshold_warning
        self.threshold_critical = threshold_critical
        self.current_value = 0.0
        self.history: List[float] = []
        self.last_updated = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "unit": self.unit,
            "current_value": self.current_value,
            "threshold_warning": self.threshold_warning,
            "threshold_critical": self.threshold_critical,
            "status": self._get_status(),
        }

    def _get_status(self) -> str:
        """Get metric status."""
        if self.current_value >= self.threshold_critical:
            return "critical"
        elif self.current_value >= self.threshold_warning:
            return "warning"
        else:
            return "healthy"


class SystemMonitor(BaseAgent):
    """
    Agent that monitors system health and performance.

    Provides:
    - Real-time system metrics monitoring
    - Resource usage tracking (CPU, memory, disk, network)
    - Performance anomaly detection
    - Alert management and notification
    - Uptime and availability tracking
    - System diagnostics and reporting
    - Threshold management
    - Historical metrics tracking
    """

    def __init__(self, llm_client: Optional[Any] = None):
        """Initialize the System Monitor."""
        super().__init__(name="SystemMonitor", llm_client=llm_client)
        self.metrics: Dict[str, HealthMetric] = {}
        self.health_score = 100.0
        self.alerts: List[Dict[str, Any]] = []
        self.start_time = datetime.utcnow()
        self.uptime_percent = 100.0

        # Initialize default metrics
        self._init_metrics()

    def _init_metrics(self) -> None:
        """Initialize default system metrics."""
        self.metrics["cpu"] = HealthMetric("CPU Usage", "%", 70.0, 90.0)
        self.metrics["memory"] = HealthMetric("Memory Usage", "%", 75.0, 95.0)
        self.metrics["disk"] = HealthMetric("Disk Usage", "%", 80.0, 95.0)
        self.metrics["response_time"] = HealthMetric("Response Time", "ms", 200.0, 500.0)
        self.metrics["error_rate"] = HealthMetric("Error Rate", "%", 5.0, 10.0)

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process system monitoring requests."""
        action = request.get("action", "status")

        if action == "status":
            return self.get_status()
        elif action == "metrics":
            return self.get_metrics()
        elif action == "health":
            return self.get_health()
        elif action == "alerts":
            return self.check_alerts()
        elif action == "update_metric":
            return self.update_metric(cast(str, request.get("metric_name")), cast(float, request.get("value")))
        elif action == "get_metric":
            return self.get_metric(cast(str, request.get("metric_name")))
        elif action == "uptime":
            return self.get_uptime()
        elif action == "diagnostics":
            return self.get_diagnostics()
        elif action == "set_threshold":
            return self.set_threshold(
                cast(str, request.get("metric_name")),
                cast(float, request.get("warning")),
                cast(float, request.get("critical")),
            )
        elif action == "clear_alerts":
            return self.clear_alerts()
        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    def get_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        self._recalculate_health()

        return {
            "status": "success",
            "agent": self.name,
            "health_score": round(self.health_score, 1),
            "system_status": (
                "healthy"
                if self.health_score > 80
                else "degraded" if self.health_score > 60 else "critical"
            ),
            "uptime_percent": round(self.uptime_percent, 2),
            "active_alerts": len(self.alerts),
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Get all system metrics."""
        metrics_dict = {name: m.to_dict() for name, m in self.metrics.items()}

        return {
            "status": "success",
            "agent": self.name,
            "metrics_count": len(self.metrics),
            "metrics": metrics_dict,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def get_health(self) -> Dict[str, Any]:
        """Get health report."""
        self._recalculate_health()

        healthy_metrics = [m for m in self.metrics.values() if m._get_status() == "healthy"]
        warning_metrics = [m for m in self.metrics.values() if m._get_status() == "warning"]
        critical_metrics = [m for m in self.metrics.values() if m._get_status() == "critical"]

        return {
            "status": "success",
            "agent": self.name,
            "health_score": round(self.health_score, 1),
            "healthy_metrics": len(healthy_metrics),
            "warning_metrics": len(warning_metrics),
            "critical_metrics": len(critical_metrics),
            "summary": self._health_summary(),
        }

    def check_alerts(self) -> Dict[str, Any]:
        """Check and return system alerts."""
        self._generate_alerts()

        return {
            "status": "success",
            "agent": self.name,
            "alert_count": len(self.alerts),
            "alerts": self.alerts,
        }

    def update_metric(self, metric_name: str, value: float) -> Dict[str, Any]:
        """Update a system metric."""
        if not metric_name:
            return {"status": "error", "message": "Metric name required"}

        if metric_name not in self.metrics:
            return {"status": "error", "message": f"Metric {metric_name} not found"}

        metric = self.metrics[metric_name]
        metric.current_value = value
        metric.history.append(value)
        metric.last_updated = datetime.utcnow()

        # Keep history limited
        if len(metric.history) > 100:
            metric.history = metric.history[-100:]

        return {
            "status": "success",
            "agent": self.name,
            "metric": metric_name,
            "value": value,
            "metric_status": metric._get_status(),
        }

    def get_metric(self, metric_name: str) -> Dict[str, Any]:
        """Get specific metric details."""
        if not metric_name:
            return {"status": "error", "message": "Metric name required"}

        if metric_name not in self.metrics:
            return {"status": "error", "message": f"Metric {metric_name} not found"}

        metric = self.metrics[metric_name]

        return {
            "status": "success",
            "agent": self.name,
            "metric": metric.to_dict(),
            "history_length": len(metric.history),
        }

    def get_uptime(self) -> Dict[str, Any]:
        """Get system uptime information."""
        runtime = datetime.utcnow() - self.start_time
        hours = runtime.total_seconds() / 3600

        return {
            "status": "success",
            "agent": self.name,
            "start_time": self.start_time.isoformat(),
            "uptime_hours": round(hours, 2),
            "uptime_percent": round(self.uptime_percent, 2),
            "runtime_formatted": self._format_duration(runtime),
        }

    def get_diagnostics(self) -> Dict[str, Any]:
        """Get system diagnostics."""
        diagnostic_info = {
            "start_time": self.start_time.isoformat(),
            "current_time": datetime.utcnow().isoformat(),
            "health_score": round(self.health_score, 1),
            "metrics_count": len(self.metrics),
            "alert_count": len(self.alerts),
            "metric_details": {name: m.to_dict() for name, m in self.metrics.items()},
        }

        return {
            "status": "success",
            "agent": self.name,
            "diagnostics": diagnostic_info,
        }

    def set_threshold(self, metric_name: str, warning: float, critical: float) -> Dict[str, Any]:
        """Set metric thresholds."""
        if not metric_name:
            return {"status": "error", "message": "Metric name required"}

        if metric_name not in self.metrics:
            return {"status": "error", "message": f"Metric {metric_name} not found"}

        metric = self.metrics[metric_name]
        metric.threshold_warning = warning
        metric.threshold_critical = critical

        return {
            "status": "success",
            "agent": self.name,
            "metric": metric_name,
            "warning_threshold": warning,
            "critical_threshold": critical,
        }

    def clear_alerts(self) -> Dict[str, Any]:
        """Clear all alerts."""
        cleared_count = len(self.alerts)
        self.alerts.clear()

        return {
            "status": "success",
            "agent": self.name,
            "cleared_alerts": cleared_count,
        }

    # Helper methods
    def _recalculate_health(self) -> None:
        """Recalculate overall health score."""
        if not self.metrics:
            self.health_score = 100.0
            return

        scores = []
        for metric in self.metrics.values():
            if metric._get_status() == "critical":
                scores.append(0)
            elif metric._get_status() == "warning":
                scores.append(50)
            else:
                scores.append(100)

        self.health_score = sum(scores) / len(scores) if scores else 100.0

    def _generate_alerts(self) -> None:
        """Generate alerts based on current metrics."""
        self.alerts.clear()

        for name, metric in self.metrics.items():
            if metric._get_status() == "critical":
                self.alerts.append(
                    {
                        "severity": "critical",
                        "metric": name,
                        "message": f"{name} at {metric.current_value}{metric.unit} (critical: {metric.threshold_critical})",
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )
            elif metric._get_status() == "warning":
                self.alerts.append(
                    {
                        "severity": "warning",
                        "metric": name,
                        "message": f"{name} at {metric.current_value}{metric.unit} (warning: {metric.threshold_warning})",
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )

    def _health_summary(self) -> str:
        """Get health summary text."""
        if self.health_score >= 90:
            return "System operating normally"
        elif self.health_score >= 70:
            return "System experiencing minor issues"
        elif self.health_score >= 50:
            return "System degraded, attention needed"
        else:
            return "System critical, immediate action required"

    def _format_duration(self, duration: timedelta) -> str:
        """Format duration for display."""
        total_seconds = int(duration.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours}h {minutes}m {seconds}s"
