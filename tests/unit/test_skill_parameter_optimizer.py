import pytest

from socratic_agents.analytics.skill_parameter_optimizer import SkillParameterOptimizer


class TestSkillParameterOptimizer:
    @pytest.fixture
    def optimizer(self):
        return SkillParameterOptimizer()

    def test_optimize_difficulty_increase(self, optimizer):
        trend = {"current_effectiveness": 0.90}
        result = optimizer.optimize_skill_difficulty("skill_a", "moderate", trend)
        assert result == "increase"

    def test_optimize_difficulty_decrease(self, optimizer):
        trend = {"current_effectiveness": 0.30}
        result = optimizer.optimize_skill_difficulty("skill_a", "moderate", trend)
        assert result == "decrease"

    def test_optimize_difficulty_maintain(self, optimizer):
        trend = {"current_effectiveness": 0.60}
        result = optimizer.optimize_skill_difficulty("skill_a", "moderate", trend)
        assert result == "maintain"

    def test_optimize_priority_high(self, optimizer):
        result = optimizer.optimize_skill_priority("skill_a", 0.80)
        assert result == "high"

    def test_optimize_priority_medium(self, optimizer):
        result = optimizer.optimize_skill_priority("skill_a", 0.60)
        assert result == "medium"

    def test_optimize_priority_low(self, optimizer):
        result = optimizer.optimize_skill_priority("skill_a", 0.30)
        assert result == "low"

    def test_optimize_confidence_improving(self, optimizer):
        trend = {"trend": "improving", "standard_deviation": 0.10}
        result = optimizer.optimize_skill_confidence("skill_a", trend)
        assert result == 0.95

    def test_optimize_confidence_stable(self, optimizer):
        trend = {"trend": "stable", "standard_deviation": 0.20}
        result = optimizer.optimize_skill_confidence("skill_a", trend)
        assert result == 0.80

    def test_optimize_confidence_declining(self, optimizer):
        trend = {"trend": "declining", "standard_deviation": 0.25}
        result = optimizer.optimize_skill_confidence("skill_a", trend)
        assert result == 0.60

    def test_auto_adjust_parameters(self, optimizer):
        data = {
            "effectiveness_values": [0.5, 0.6, 0.7, 0.75, 0.80],
            "trend": {"trend": "improving"},
            "current_parameters": {"difficulty": 0.5, "priority": "medium", "confidence": 0.75},
        }
        result = optimizer.auto_adjust_skill_parameters("skill_a", data)
        assert result["applied"]
        assert "difficulty" in result

    def test_auto_adjust_locked_skill(self, optimizer):
        data = {"effectiveness_values": [0.5], "trend": {}, "current_parameters": {}}
        optimizer.auto_adjust_skill_parameters("skill_locked", data)
        result = optimizer.auto_adjust_skill_parameters("skill_locked", data)
        assert not result["applied"]

    def test_analyze_optimization_impact(self, optimizer):
        before = {"difficulty": 0.5, "confidence": 0.75}
        after = {"difficulty": 0.575, "confidence": 0.80}
        result = optimizer.analyze_optimization_impact("skill_a", before, after)
        assert "changes" in result
        assert "magnitude" in result
        assert "safety_status" in result

    def test_get_optimization_history_empty(self, optimizer):
        history = optimizer.get_optimization_history("unknown")
        assert history == []

    def test_get_optimization_history(self, optimizer):
        data = {"effectiveness_values": [0.5], "trend": {}, "current_parameters": {}}
        optimizer.auto_adjust_skill_parameters("skill_hist", data)
        history = optimizer.get_optimization_history("skill_hist")
        assert len(history) > 0
