"""Unit tests for Effectiveness Trend Analyzer."""

import pytest
from socratic_agents.analytics import EffectivenessTrendAnalyzer


class TestEffectivenessTrendAnalyzer:
    """Test EffectivenessTrendAnalyzer functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = EffectivenessTrendAnalyzer()

    def test_record_effectiveness_data(self):
        """Test recording effectiveness data."""
        self.analyzer.record_effectiveness_data("skill_a", 0.75)
        data = self.analyzer.get_effectiveness_data("skill_a")
        assert len(data) == 1
        assert data[0]["effectiveness"] == 0.75

    def test_record_effectiveness_data_validation(self):
        """Test validation of effectiveness values."""
        with pytest.raises(ValueError, match="effectiveness must be between"):
            self.analyzer.record_effectiveness_data("skill_a", 1.5)
        with pytest.raises(ValueError, match="effectiveness must be between"):
            self.analyzer.record_effectiveness_data("skill_a", -0.1)

    def test_calculate_trend_improving(self):
        """Test trend calculation for improving skill."""
        values = [0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8]
        for val in values:
            self.analyzer.record_effectiveness_data("skill_improving", val)
        trend = self.analyzer.calculate_trend("skill_improving")
        assert trend["trend"] == "improving"
        assert trend["slope"] > 0

    def test_calculate_trend_declining(self):
        """Test trend calculation for declining skill."""
        values = [0.8, 0.75, 0.7, 0.65, 0.6, 0.55, 0.5]
        for val in values:
            self.analyzer.record_effectiveness_data("skill_declining", val)
        trend = self.analyzer.calculate_trend("skill_declining")
        assert trend["trend"] == "declining"
        assert trend["slope"] < 0

    def test_calculate_trend_stable(self):
        """Test trend calculation for stable skill."""
        values = [0.65, 0.65, 0.66, 0.65, 0.65, 0.64, 0.65]
        for val in values:
            self.analyzer.record_effectiveness_data("skill_stable", val)
        trend = self.analyzer.calculate_trend("skill_stable")
        assert trend["trend"] == "stable"

    def test_detect_anomalies(self):
        """Test anomaly detection."""
        values = [0.5, 0.51, 0.52, 0.5, 0.51, 0.95, 0.51, 0.52]
        for val in values:
            self.analyzer.record_effectiveness_data("skill_a", val)
        anomalies = self.analyzer.detect_anomalies("skill_a", threshold=2.0)
        assert len(anomalies) > 0

    def test_detect_anomalies_empty_data(self):
        """Test anomaly detection with no data."""
        anomalies = self.analyzer.detect_anomalies("nonexistent")
        assert anomalies == []

    def test_forecast_effectiveness(self):
        """Test effectiveness forecasting."""
        values = [0.5, 0.55, 0.6, 0.65, 0.7]
        for val in values:
            self.analyzer.record_effectiveness_data("skill_a", val)
        forecast = self.analyzer.forecast_effectiveness("skill_a", periods=3)
        assert len(forecast) == 3
        assert all(0.0 <= f <= 1.0 for f in forecast)

    def test_forecast_effectiveness_insufficient_data(self):
        """Test forecasting with insufficient data."""
        self.analyzer.record_effectiveness_data("skill_a", 0.75)
        with pytest.raises(ValueError, match="Need at least 2"):
            self.analyzer.forecast_effectiveness("skill_a")

    def test_get_effectiveness_statistics(self):
        """Test getting effectiveness statistics."""
        values = [0.5, 0.6, 0.7, 0.8, 0.9]
        for val in values:
            self.analyzer.record_effectiveness_data("skill_a", val)
        stats = self.analyzer.get_effectiveness_statistics("skill_a")
        assert stats["min"] == 0.5
        assert stats["max"] == 0.9
        assert stats["mean"] == 0.7
        assert stats["std_dev"] > 0

    def test_compare_skills(self):
        """Test comparing multiple skills."""
        for val in [0.5, 0.6, 0.7]:
            self.analyzer.record_effectiveness_data("skill_a", val)
        for val in [0.7, 0.8, 0.9]:
            self.analyzer.record_effectiveness_data("skill_b", val)
        comparison = self.analyzer.compare_skills(["skill_a", "skill_b"])
        assert "comparison" in comparison
        assert "best_performer" in comparison
        assert comparison["best_performer"] == "skill_b"

    def test_compare_skills_empty_list(self):
        """Test comparing with empty skill list."""
        with pytest.raises(ValueError, match="skill_ids cannot be empty"):
            self.analyzer.compare_skills([])

    def test_clear_data_specific_skill(self):
        """Test clearing data for specific skill."""
        self.analyzer.record_effectiveness_data("skill_a", 0.75)
        self.analyzer.record_effectiveness_data("skill_b", 0.8)
        self.analyzer.clear_data("skill_a")
        assert len(self.analyzer.get_effectiveness_data("skill_a")) == 0
        assert len(self.analyzer.get_effectiveness_data("skill_b")) == 1

    def test_get_all_skills(self):
        """Test getting list of all skills."""
        skills = ["skill_a", "skill_b", "skill_c"]
        for skill in skills:
            self.analyzer.record_effectiveness_data(skill, 0.75)
        all_skills = self.analyzer.get_all_skills()
        assert set(all_skills) == set(skills)

    def test_insufficient_data_handling(self):
        """Test insufficient data handling across methods."""
        self.analyzer.record_effectiveness_data("skill_a", 0.5)
        with pytest.raises(ValueError):
            self.analyzer.calculate_trend("skill_a", window_size=5)
        with pytest.raises(ValueError):
            self.analyzer.forecast_effectiveness("skill_a", periods=5)
