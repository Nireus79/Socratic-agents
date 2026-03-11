import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class SkillRecommendationPredictor:
    def __init__(self):
        self.skill_effectiveness_history = {}
        self.skill_category_map = {}
        self.prediction_records = []
        self.interaction_bonuses = {}

    def predict_effectiveness(
        self, skill: Dict[str, Any], user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        skill_id = skill.get("id")
        if not skill_id:
            return {
                "status": "error",
                "message": "Skill ID required",
                "predicted_effectiveness": 0.0,
            }

        historical_avg = self._get_historical_average(skill_id)
        user_engagement = user_profile.get("engagement_score", 0.5)
        category = skill.get("category_focus", "general")
        category_effectiveness = self._get_category_average(category)
        interaction_bonus = self._get_interaction_bonus(skill_id)
        recency_weight = self._get_recency_weight(skill_id)

        prediction = (
            0.3 * historical_avg
            + 0.25 * user_engagement
            + 0.2 * category_effectiveness
            + 0.15 * interaction_bonus
            + 0.1 * recency_weight
        )
        prediction = max(0.0, min(1.0, prediction))

        confidence = self._calculate_prediction_confidence(skill_id)
        return {
            "status": "success",
            "skill_id": skill_id,
            "predicted_effectiveness": round(prediction, 3),
            "confidence": round(confidence, 3),
            "components": {
                "historical_avg": round(historical_avg, 3),
                "user_engagement": round(user_engagement, 3),
                "category_effectiveness": round(category_effectiveness, 3),
                "interaction_bonus": round(interaction_bonus, 3),
                "recency_weight": round(recency_weight, 3),
            },
        }

    def rank_skills_by_prediction(
        self, skills: List[Dict[str, Any]], user_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        if not skills:
            return []
        predictions = []
        for skill in skills:
            pred = self.predict_effectiveness(skill, user_profile)
            if pred.get("status") == "success":
                predictions.append(
                    {
                        "skill": skill,
                        "predicted_effectiveness": pred["predicted_effectiveness"],
                        "confidence": pred["confidence"],
                    }
                )
        predictions.sort(key=lambda x: x["predicted_effectiveness"], reverse=True)
        return predictions

    def predict_recommendation_success(self, skill_id: str) -> float:
        if not skill_id or skill_id not in self.skill_effectiveness_history:
            return 0.5
        history = self.skill_effectiveness_history[skill_id]
        if len(history) == 0:
            return 0.5
        successes = sum(1 for e in history if e >= 0.7)
        return round(successes / len(history), 3)

    def identify_high_impact_skills(
        self, category: Optional[str] = None, min_prediction: float = 0.7
    ) -> List[Dict[str, Any]]:
        high_impact = []
        for skill_id in self.skill_effectiveness_history:
            avg_effectiveness = self._get_historical_average(skill_id)
            if avg_effectiveness >= min_prediction:
                skill_category = self.skill_category_map.get(skill_id, "general")
                if category is None or skill_category == category:
                    high_impact.append(
                        {
                            "skill_id": skill_id,
                            "category": skill_category,
                            "effectiveness": round(avg_effectiveness, 3),
                            "applications": len(self.skill_effectiveness_history[skill_id]),
                        }
                    )
        high_impact.sort(key=lambda x: x["effectiveness"], reverse=True)
        return high_impact

    def train_prediction_model(self, training_data: List[Dict[str, Any]]) -> None:
        for record in training_data:
            skill_id = record.get("skill_id")
            effectiveness = record.get("effectiveness", 0.5)
            category = record.get("category", "general")
            if skill_id:
                if skill_id not in self.skill_effectiveness_history:
                    self.skill_effectiveness_history[skill_id] = []
                self.skill_effectiveness_history[skill_id].append(max(0.0, min(1.0, effectiveness)))
                self.skill_category_map[skill_id] = category

    def get_prediction_accuracy(self) -> Dict[str, float]:
        if not self.prediction_records:
            return {"mae": 0.0, "rmse": 0.0, "mape": 0.0, "sample_size": 0}
        total_error = sum(
            abs(r.get("predicted", 0.5) - r.get("actual", 0.5)) for r in self.prediction_records
        )
        squared_error = sum(
            (abs(r.get("predicted", 0.5) - r.get("actual", 0.5))) ** 2
            for r in self.prediction_records
        )
        n = len(self.prediction_records)
        mae = total_error / n if n > 0 else 0.0
        rmse = (squared_error / n) ** 0.5 if n > 0 else 0.0
        return {"mae": round(mae, 3), "rmse": round(rmse, 3), "mape": 0.0, "sample_size": n}

    def add_effectiveness_record(
        self,
        skill_id: str,
        effectiveness: float,
        user_profile: Optional[Dict[str, Any]] = None,
    ) -> None:
        if not skill_id:
            return
        effectiveness = max(0.0, min(1.0, effectiveness))
        if skill_id not in self.skill_effectiveness_history:
            self.skill_effectiveness_history[skill_id] = []
        self.skill_effectiveness_history[skill_id].append(effectiveness)

    def _get_historical_average(self, skill_id: str) -> float:
        if skill_id not in self.skill_effectiveness_history:
            return 0.5
        history = self.skill_effectiveness_history[skill_id]
        return sum(history) / len(history) if history else 0.5

    def _get_category_average(self, category: str) -> float:
        category_skills = [s for s, c in self.skill_category_map.items() if c == category]
        if not category_skills:
            return 0.5
        return sum(self._get_historical_average(s) for s in category_skills) / len(category_skills)

    def _get_interaction_bonus(self, skill_id: str) -> float:
        bonuses = [b for (s1, s2), b in self.interaction_bonuses.items() if skill_id in (s1, s2)]
        return min(0.2, sum(bonuses) / len(bonuses) if bonuses else 0.0)

    def _get_recency_weight(self, skill_id: str) -> float:
        if skill_id not in self.skill_effectiveness_history:
            return 0.5
        history = self.skill_effectiveness_history[skill_id]
        if not history:
            return 0.5
        decay = 0.9
        weighted_sum = sum(
            decay ** (len(history) - i - 1) * history[i] for i in range(len(history))
        )
        total_weight = sum(decay**i for i in range(len(history)))
        return weighted_sum / total_weight if total_weight > 0 else 0.5

    def _calculate_prediction_confidence(self, skill_id: str) -> float:
        if skill_id not in self.skill_effectiveness_history:
            return 0.3
        history_len = len(self.skill_effectiveness_history[skill_id])
        return round(min(0.95, 0.5 + (history_len * 0.05)), 3)
