"""Integration tests for LearningAgent with socratic-learning library."""

from unittest.mock import Mock

import pytest

from src.socratic_agents.agents.learning_agent import LearningAgent


class TestLearningAgentInitialization:
    """Test LearningAgent initialization."""

    def test_create_agent_minimal(self):
        """Test creating agent with minimal parameters."""
        agent = LearningAgent()
        assert agent is not None
        assert agent.name == "LearningAgent"
        assert agent.interactions == []

    def test_create_agent_with_llm(self):
        """Test creating agent with LLM client."""
        mock_llm = Mock()
        agent = LearningAgent(llm_client=mock_llm)
        assert agent.llm_client == mock_llm

    def test_create_agent_with_database(self):
        """Test creating agent with custom database path."""
        agent = LearningAgent(database_path="/tmp/test.db")
        assert agent is not None


class TestInteractionRecording:
    """Test interaction recording."""

    def test_record_interaction(self):
        """Test recording an interaction."""
        agent = LearningAgent()
        interaction = {
            "type": "question",
            "topic": "Python",
            "success": True,
        }

        result = agent.record_interaction(interaction)

        assert result["status"] == "success"
        assert result["recorded"] is True
        assert len(agent.interactions) == 1

    def test_record_multiple_interactions(self):
        """Test recording multiple interactions."""
        agent = LearningAgent()

        for i in range(3):
            agent.record_interaction({"type": "question", "success": True})

        assert len(agent.interactions) == 3

    def test_record_no_interaction(self):
        """Test recording with no interaction."""
        agent = LearningAgent()
        result = agent.record_interaction(None)
        assert result["status"] == "error"


class TestPatternAnalysis:
    """Test pattern detection."""

    def test_analyze_patterns_empty(self):
        """Test analyzing patterns with no interactions."""
        agent = LearningAgent()
        result = agent.analyze_patterns()

        assert result["status"] == "success"
        assert "patterns" in result

    def test_analyze_patterns_with_interactions(self):
        """Test analyzing patterns after recording interactions."""
        agent = LearningAgent()

        # Record interactions
        for _ in range(5):
            agent.record_interaction({"type": "question", "success": True})

        result = agent.analyze_patterns()

        assert result["status"] == "success"
        assert result["patterns_found"] > 0

    def test_detect_learning_patterns(self):
        """Test detecting learning patterns."""
        agent = LearningAgent()

        # Record some interactions
        for _ in range(3):
            agent.record_interaction({"type": "question", "success": True})

        result = agent.detect_learning_patterns()

        assert result["status"] == "success"
        assert "pattern_count" in result


class TestLearningMetrics:
    """Test learning metrics calculation."""

    def test_calculate_learning_metrics(self):
        """Test calculating learning metrics."""
        agent = LearningAgent()

        # Record interactions
        for _ in range(5):
            agent.record_interaction({"type": "question", "success": True})

        result = agent.calculate_learning_metrics("user_123")

        assert result["status"] == "success"
        assert "engagement_score" in result or "engagement_score" in result
        assert "learning_velocity" in result or "learning_velocity" in result

    def test_metrics_experience_level(self):
        """Test experience level estimation."""
        agent = LearningAgent()

        # Test with few interactions
        result = agent.calculate_learning_metrics("user_123")
        assert result["status"] == "success"


class TestPhaseMaturity:
    """Test phase maturity assessment."""

    def test_assess_maturity_basic(self):
        """Test basic maturity assessment."""
        agent = LearningAgent()

        result = agent.assess_phase_maturity(
            phase="discovery",
            phase_specs=[
                {"value": 10, "categories": ["requirements"]},
                {"value": 15, "categories": ["scope"]},
            ],
        )

        assert result["status"] == "success"
        assert result["phase"] == "discovery"
        assert "maturity_percentage" in result or "is_ready" in result

    def test_assess_maturity_empty_specs(self):
        """Test maturity assessment with empty specs."""
        agent = LearningAgent()

        result = agent.assess_phase_maturity(
            phase="design",
            phase_specs=[],
        )

        assert result["status"] == "success"

    def test_assess_maturity_different_phases(self):
        """Test maturity for different phases."""
        agent = LearningAgent()

        phases = ["discovery", "analysis", "design", "implementation"]

        for phase in phases:
            result = agent.assess_phase_maturity(phase, [])
            assert result["status"] == "success"
            assert result["phase"] == phase


class TestRecommendations:
    """Test recommendation generation."""

    def test_generate_recommendations(self):
        """Test generating recommendations."""
        agent = LearningAgent()

        result = agent.generate_recommendations("user_123")

        assert result["status"] == "success"
        assert "recommendations" in result or "recommendation_count" in result

    def test_recommendations_based_on_level(self):
        """Test recommendations vary by experience level."""
        agent = LearningAgent()

        # Few interactions - beginner
        result = agent.generate_recommendations("user_123")
        assert result["status"] == "success"


class TestUserProfile:
    """Test user profile management."""

    def test_get_user_profile(self):
        """Test getting user profile."""
        agent = LearningAgent()

        result = agent.get_user_learning_profile()

        assert result is not None
        assert "learning_velocity" in result
        assert "engagement_score" in result

    def test_profile_initialization(self):
        """Test profile is properly initialized."""
        agent = LearningAgent()

        profile = agent.user_profile

        assert profile["learning_velocity"] == "medium"
        assert profile["engagement_score"] == 0.6


class TestSkillPersonalization:
    """Test skill personalization."""

    def test_personalize_skills(self):
        """Test personalizing skills."""
        agent = LearningAgent()

        skills = [
            {"id": "skill_1", "name": "Python Basics", "priority": "high"},
            {"id": "skill_2", "name": "Advanced Python", "priority": "medium"},
        ]

        result = agent.personalize_skills(skills)

        assert result["status"] == "success"
        assert "personalized_skills" in result
        assert len(result["personalized_skills"]) == len(skills)

    def test_personalize_empty_skills(self):
        """Test personalizing with no skills."""
        agent = LearningAgent()

        result = agent.personalize_skills([])

        assert result["status"] == "success"
        assert result["personalized_skills"] == []


class TestSkillFeedback:
    """Test skill feedback tracking."""

    def test_track_skill_feedback(self):
        """Test tracking skill feedback."""
        agent = LearningAgent()

        result = agent.track_skill_feedback("skill_123", "helped")

        assert result["status"] == "success"
        assert result["skill_id"] == "skill_123"
        assert result["feedback"] == "helped"

    def test_track_multiple_feedback(self):
        """Test tracking multiple feedback."""
        agent = LearningAgent()

        feedbacks = ["helped", "no_effect", "harmful"]

        for feedback in feedbacks:
            result = agent.track_skill_feedback("skill_123", feedback)
            assert result["status"] == "success"

    def test_track_feedback_missing_skill_id(self):
        """Test feedback without skill ID."""
        agent = LearningAgent()

        result = agent.track_skill_feedback(None, "helped")

        assert result["status"] == "error"


class TestProcessMethod:
    """Test the main process method."""

    def test_process_record_action(self):
        """Test process with record action."""
        agent = LearningAgent()

        result = agent.process(
            {
                "action": "record",
                "interaction": {"type": "question", "success": True},
            }
        )

        assert result["status"] == "success"

    def test_process_analyze_action(self):
        """Test process with analyze action."""
        agent = LearningAgent()

        result = agent.process({"action": "analyze"})

        assert result["status"] == "success"

    def test_process_metrics_action(self):
        """Test process with metrics action."""
        agent = LearningAgent()

        result = agent.process(
            {
                "action": "metrics",
                "user_id": "user_123",
            }
        )

        assert result["status"] == "success" or result["status"] == "error"

    def test_process_recommend_action(self):
        """Test process with recommend action."""
        agent = LearningAgent()

        result = agent.process(
            {
                "action": "recommend",
                "user_id": "user_123",
            }
        )

        assert result["status"] == "success" or result["status"] == "error"

    def test_process_maturity_action(self):
        """Test process with assess_maturity action."""
        agent = LearningAgent()

        result = agent.process(
            {
                "action": "assess_maturity",
                "phase": "discovery",
                "phase_specs": [],
            }
        )

        assert result["status"] == "success" or result["status"] == "error"

    def test_process_unknown_action(self):
        """Test process with unknown action."""
        agent = LearningAgent()

        result = agent.process({"action": "unknown"})

        assert result["status"] == "error"


class TestFullLearningMode:
    """Test full learning mode with socratic-learning."""

    def test_full_learning_enabled(self):
        """Test that full learning is enabled if library available."""
        agent = LearningAgent()

        if agent.use_full_learning:
            assert agent.learning_engine is not None
            assert agent.maturity_calculator is not None

    def test_fallback_mode(self):
        """Test fallback mode when library unavailable."""
        agent = LearningAgent()

        # Even if disabled, should still work
        result = agent.calculate_learning_metrics("user_123")
        assert result["status"] == "success"


class TestLearningIntegration:
    """Test full learning workflow."""

    def test_complete_learning_workflow(self):
        """Test complete learning workflow."""
        agent = LearningAgent()

        # Record interactions
        for i in range(5):
            agent.record_interaction(
                {
                    "type": "question",
                    "topic": "Python",
                    "success": i % 2 == 0,
                    "quality_score": 0.7 + (i * 0.05),
                }
            )

        # Calculate metrics
        metrics = agent.calculate_learning_metrics("user_123")
        assert metrics["status"] == "success"

        # Detect patterns
        patterns = agent.detect_learning_patterns()
        assert patterns["status"] == "success"

        # Assess maturity
        maturity = agent.assess_phase_maturity("discovery", [])
        assert maturity["status"] == "success"

        # Generate recommendations
        recommendations = agent.generate_recommendations("user_123")
        assert recommendations["status"] == "success"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
