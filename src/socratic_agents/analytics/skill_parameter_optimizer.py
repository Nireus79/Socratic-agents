from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List


class SkillParameterOptimizer:
    MAX_CHANGE_PERCENT = 0.15
    LOCK_PERIOD_DAYS = 7

    def __init__(self):
        self._optimization_history = defaultdict(list)
        self._locked_skills = {}

    def optimize_skill_difficulty(self, skill_id: str, user_velocity: str, trend: Dict) -> str:
        if not trend:
            return "maintain"
        if self._is_skill_locked(skill_id):
            return "maintain"
        eff = trend.get("current_effectiveness", 0.5)
        return "increase" if eff > 0.85 else ("decrease" if eff < 0.40 else "maintain")

    def optimize_skill_priority(self, skill_id: str, effectiveness: float) -> str:
        if not (0.0 <= effectiveness <= 1.0):
            return "medium"
        return "high" if effectiveness > 0.75 else ("medium" if effectiveness >= 0.40 else "low")

    def optimize_skill_confidence(self, skill_id: str, trend: Dict) -> float:
        if not trend:
            return 0.75
        td = trend.get("trend", "stable")
        sd = trend.get("standard_deviation", 0.0)
        if td == "improving" and sd < 0.15:
            return 0.95
        if td == "stable" and 0.15 <= sd <= 0.30:
            return 0.80
        if td == "declining" or sd > 0.30:
            return 0.60
        return 0.75

    def auto_adjust_skill_parameters(self, skill_id: str, data: Dict) -> Dict[str, Any]:
        if not data:
            return self._empty()
        if self._is_skill_locked(skill_id):
            return {"applied": False, "reason": "locked"}
        values = data.get("effectiveness_values", [])
        avg = sum(values) / len(values) if values else 0.5
        trend = data.get("trend", {})
        diff = self.optimize_skill_difficulty(skill_id, "moderate", trend)
        prio = self.optimize_skill_priority(skill_id, avg)
        conf = self.optimize_skill_confidence(skill_id, trend)
        self._lock_skill(skill_id)
        self._optimization_history[skill_id].append({"timestamp": datetime.now().isoformat()})
        return {"applied": True, "difficulty": diff, "priority": prio, "confidence": conf}

    def analyze_optimization_impact(self, skill_id: str, before: Dict, after: Dict) -> Dict:
        changes = [k for k in before if before.get(k) != after.get(k)]
        return {"changes": changes, "magnitude": len(changes) * 0.1, "safety_status": "safe"}

    def get_optimization_history(self, skill_id: str) -> List[Dict]:
        return self._optimization_history.get(skill_id, [])

    def _is_skill_locked(self, skill_id: str) -> bool:
        if skill_id not in self._locked_skills:
            return False
        return datetime.now() < self._locked_skills[skill_id]

    def _lock_skill(self, skill_id: str) -> None:
        self._locked_skills[skill_id] = datetime.now() + timedelta(days=self.LOCK_PERIOD_DAYS)

    def _empty(self) -> Dict:
        return {"applied": False}
