"""Analytics Module for comprehensive system metrics."""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import defaultdict


class AnalyticsModule:
    """Comprehensive analytics and metrics for learning system."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._user_data = {}
        self._skill_metrics = defaultdict(dict)
        self._recommendation_accuracy_data = []

    def get_user_learning_progress(self) -> Dict[str, Any]:
        total_skills = len(self._skill_metrics)
        avg_eff = self._calculate_average_effectiveness()
        return {
            "status": "success",
            "total_skills_applied": total_skills,
            "average_effectiveness": round(avg_eff, 3),
            "completion_percent": min(100.0, total_skills * 5),
        }

    def get_skill_effectiveness_report(self, skill_id: Optional[str] = None) -> Dict[str, Any]:
        if skill_id:
            m = self._skill_metrics.get(skill_id, {})
            return {
                "status": "success",
                "skill_id": skill_id,
                "effectiveness": m.get("effectiveness", 0.0),
            }
        return {"status": "success", "skills_report": dict(self._skill_metrics)}

    def get_system_health_score(self) -> float:
        if not self._skill_metrics:
            return 50.0
        avg_eff = self._calculate_average_effectiveness()
        engagement = self._user_data.get("engagement_score", 0.5)
        acc = self._calculate_recommendation_accuracy()
        health = (avg_eff * 0.4) + (engagement * 0.35) + (acc * 0.25)
        return round(min(100.0, health * 100), 1)

    def get_recommendation_accuracy(self, period_days: int = 30) -> float:
        return round(self._calculate_recommendation_accuracy() * 100, 1)

    def generate_analytics_dashboard(self) -> Dict[str, Any]:
        progress = self.get_user_learning_progress()
        health = self.get_system_health_score()
        avg_eff = self._calculate_average_effectiveness()
        return {
            "status": "success",
            "metrics": {
                "user_learning_progress": progress.get("completion_percent", 0),
                "average_skill_effectiveness": round(avg_eff, 3),
                "system_health_score": health,
                "total_skills_applied": progress.get("total_skills_applied", 0),
                "recommendation_accuracy": self.get_recommendation_accuracy(),
            },
        }

    def export_analytics(self, format_type: str = "json") -> str:
        dashboard = self.generate_analytics_dashboard()
        if format_type == "json":
            import json

            return json.dumps(dashboard)
        return str(dashboard)

    def record_user_metric(self, metric_name: str, value: Any) -> None:
        self._user_data[metric_name] = value

    def record_skill_metric(
        self, skill_id: str, effectiveness: float, trend: str = "stable"
    ) -> None:
        if skill_id not in self._skill_metrics:
            self._skill_metrics[skill_id] = {}
        self._skill_metrics[skill_id]["effectiveness"] = effectiveness
        self._skill_metrics[skill_id]["trend"] = trend

    def record_recommendation_result(self, skill_id: str, predicted: float, actual: float) -> None:
        self._recommendation_accuracy_data.append(
            {"skill_id": skill_id, "predicted": predicted, "actual": actual}
        )

    def _calculate_average_effectiveness(self) -> float:
        if not self._skill_metrics:
            return 0.5
        total = sum(m.get("effectiveness", 0.5) for m in self._skill_metrics.values())
        return total / len(self._skill_metrics)

    def _calculate_recommendation_accuracy(self) -> float:
        if not self._recommendation_accuracy_data:
            return 0.5
        total_error = sum(
            abs(r["predicted"] - r["actual"]) for r in self._recommendation_accuracy_data
        )
        avg_error = total_error / len(self._recommendation_accuracy_data)
        return max(0.0, 1.0 - avg_error)
