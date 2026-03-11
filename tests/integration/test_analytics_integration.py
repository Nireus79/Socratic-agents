import pytest
from socratic_agents.analytics.skill_interaction_tracker import SkillInteractionTracker
from socratic_agents.analytics.skill_recommendation_predictor import SkillRecommendationPredictor
from socratic_agents.analytics.skill_parameter_optimizer import SkillParameterOptimizer
from socratic_agents.analytics.analytics_module import AnalyticsModule


class TestAnalyticsIntegration:
    def test_interaction_optimization_flow(self):
        tracker = SkillInteractionTracker()
        optimizer = SkillParameterOptimizer()

        for _ in range(3):
            tracker.record_skill_interaction(["skill_a", "skill_b"], 0.9)
        synergies = tracker.identify_skill_synergies(threshold=0.7)

        effectiveness_data = {
            "effectiveness_values": [0.85 + (i * 0.01) for i in range(10)],
            "trend": {"trend": "improving"},
            "current_parameters": {"difficulty": 0.5, "priority": "medium", "confidence": 0.75},
        }
        result = optimizer.auto_adjust_skill_parameters("skill_a", effectiveness_data)
        assert "applied" in result

    def test_analytics_metrics_collection(self):
        analytics = AnalyticsModule()
        for i in range(5):
            analytics.record_skill_metric(f"skill_{i}", 0.6 + (i * 0.05))
        analytics.record_user_metric("engagement_score", 0.85)
        analytics.record_recommendation_result("skill1", 0.85, 0.88)

        dashboard = analytics.generate_analytics_dashboard()
        assert "metrics" in dashboard
        assert dashboard["metrics"]["total_skills_applied"] == 5

    def test_dashboard_export(self):
        analytics = AnalyticsModule()
        analytics.record_skill_metric("skill1", 0.85)
        json_export = analytics.export_analytics("json")
        assert isinstance(json_export, str)
        assert "metrics" in json_export

    def test_multi_component_scenario(self):
        tracker = SkillInteractionTracker()
        analytics = AnalyticsModule()

        tracker.record_skill_interaction(["s1", "s2"], 0.88)
        analytics.record_skill_metric("s1", 0.88)

        dashboard = analytics.generate_analytics_dashboard()
        assert dashboard["status"] == "success"
        assert dashboard["metrics"]["average_skill_effectiveness"] > 0.8

    def test_optimizer_with_analytics(self):
        optimizer = SkillParameterOptimizer()
        analytics = AnalyticsModule()

        effectiveness_data = {
            "effectiveness_values": [0.8, 0.82, 0.84, 0.86, 0.88],
            "trend": {"trend": "improving"},
            "current_parameters": {"difficulty": 0.5, "priority": "medium", "confidence": 0.75},
        }
        result = optimizer.auto_adjust_skill_parameters("skill_test", effectiveness_data)

        if result.get("applied"):
            analytics.record_skill_metric("skill_test", 0.88)
            dashboard = analytics.generate_analytics_dashboard()
            assert dashboard["status"] == "success"
