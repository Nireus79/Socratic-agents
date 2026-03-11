"""Unit tests for AnalyticsModule."""

import pytest
from socratic_agents.analytics.analytics_module import AnalyticsModule


class TestAnalyticsModule:
    @pytest.fixture
    def analytics(self):
        return AnalyticsModule()

    def test_get_user_learning_progress_empty(self, analytics):
        result = analytics.get_user_learning_progress()
        assert result["status"] == "success"
        assert result["total_skills_applied"] == 0
        assert result["average_effectiveness"] == 0.5

    def test_get_user_learning_progress_with_skills(self, analytics):
        analytics.record_skill_metric("skill1", 0.8)
        analytics.record_skill_metric("skill2", 0.6)
        result = analytics.get_user_learning_progress()
        assert result["total_skills_applied"] == 2
        assert result["average_effectiveness"] == 0.7

    def test_get_skill_effectiveness_report_all(self, analytics):
        analytics.record_skill_metric("skill1", 0.8)
        result = analytics.get_skill_effectiveness_report()
        assert result["status"] == "success"
        assert "skills_report" in result

    def test_get_skill_effectiveness_report_single(self, analytics):
        analytics.record_skill_metric("skill1", 0.85)
        result = analytics.get_skill_effectiveness_report("skill1")
        assert result["status"] == "success"
        assert result["skill_id"] == "skill1"
        assert result["effectiveness"] == 0.85

    def test_get_system_health_score(self, analytics):
        analytics.record_skill_metric("skill1", 0.8)
        analytics.record_user_metric("engagement_score", 0.9)
        score = analytics.get_system_health_score()
        assert 0 <= score <= 100

    def test_get_recommendation_accuracy(self, analytics):
        analytics.record_recommendation_result("skill1", 0.8, 0.75)
        analytics.record_recommendation_result("skill2", 0.7, 0.65)
        accuracy = analytics.get_recommendation_accuracy()
        assert 0 <= accuracy <= 100

    def test_generate_analytics_dashboard(self, analytics):
        analytics.record_skill_metric("skill1", 0.8)
        analytics.record_skill_metric("skill2", 0.7)
        analytics.record_user_metric("engagement_score", 0.8)
        result = analytics.generate_analytics_dashboard()
        assert result["status"] == "success"
        assert "metrics" in result
        assert "user_learning_progress" in result["metrics"]
        assert "system_health_score" in result["metrics"]

    def test_export_analytics_json(self, analytics):
        analytics.record_skill_metric("skill1", 0.8)
        result = analytics.export_analytics("json")
        assert isinstance(result, str)
        assert "metrics" in result

    def test_export_analytics_csv(self, analytics):
        analytics.record_skill_metric("skill1", 0.8)
        result = analytics.export_analytics("csv")
        assert isinstance(result, str)

    def test_record_user_metric(self, analytics):
        analytics.record_user_metric("engagement_score", 0.85)
        assert analytics._user_data["engagement_score"] == 0.85

    def test_record_skill_metric(self, analytics):
        analytics.record_skill_metric("skill1", 0.9, "improving")
        assert "skill1" in analytics._skill_metrics
        assert analytics._skill_metrics["skill1"]["effectiveness"] == 0.9
        assert analytics._skill_metrics["skill1"]["trend"] == "improving"

    def test_record_recommendation_result(self, analytics):
        analytics.record_recommendation_result("skill1", 0.8, 0.75)
        assert len(analytics._recommendation_accuracy_data) == 1
        assert analytics._recommendation_accuracy_data[0]["predicted"] == 0.8
        assert analytics._recommendation_accuracy_data[0]["actual"] == 0.75

    def test_calculate_average_effectiveness(self, analytics):
        analytics.record_skill_metric("skill1", 0.8)
        analytics.record_skill_metric("skill2", 0.6)
        avg = analytics._calculate_average_effectiveness()
        assert avg == 0.7

    def test_calculate_recommendation_accuracy(self, analytics):
        analytics.record_recommendation_result("skill1", 0.9, 0.8)
        analytics.record_recommendation_result("skill2", 0.7, 0.6)
        acc = analytics._calculate_recommendation_accuracy()
        assert 0 <= acc <= 1
