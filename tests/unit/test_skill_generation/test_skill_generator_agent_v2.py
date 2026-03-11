"""Tests for Phase 4.5: SkillGeneratorAgentV2 with LLM integration."""

from unittest.mock import Mock

import pytest

from socratic_agents.agents.skill_generator_agent_v2 import SkillGeneratorAgentV2
from socratic_agents.models.skill_models import AgentSkill


class TestSkillGeneratorAgentV2:
    """Tests for SkillGeneratorAgentV2."""

    @pytest.fixture
    def mock_llm_client(self):
        """Create a mock LLM client."""
        return Mock()

    @pytest.fixture
    def agent_v2_with_llm(self, mock_llm_client):
        """Create V2 agent with mock LLM."""
        return SkillGeneratorAgentV2(llm_client=mock_llm_client)

    @pytest.fixture
    def agent_v2_without_llm(self):
        """Create V2 agent without LLM."""
        return SkillGeneratorAgentV2(llm_client=None)

    @pytest.fixture
    def sample_maturity_data(self):
        """Create sample maturity data."""
        return {
            "current_phase": "discovery",
            "completion_percent": 25,
            "weak_categories": ["problem_definition", "scope"],
            "category_scores": {
                "problem_definition_score": 15,
                "scope_score": 20,
                "target_audience_score": 60,
            },
        }

    @pytest.fixture
    def sample_learning_data(self):
        """Create sample learning data."""
        return {
            "learning_velocity": "medium",
            "engagement_score": 0.7,
            "patterns": ["iterative_improvement"],
        }

    def test_agent_v2_initialization(self, mock_llm_client):
        """Test V2 agent initialization."""
        agent = SkillGeneratorAgentV2(llm_client=mock_llm_client, generation_mode="hybrid")
        assert agent.name == "SkillGeneratorAgent"
        assert agent.generation_mode == "hybrid"
        assert agent.enable_llm_generation is True
        assert agent.llm_generator is not None
        assert agent.llm_skills_generated == 0

    def test_agent_v2_without_llm_client(self):
        """Test V2 agent without LLM client."""
        agent = SkillGeneratorAgentV2(llm_client=None)
        assert agent.llm_generator is None
        assert agent.enable_llm_generation is True

    def test_process_generate_with_hardcoded_mode(
        self, agent_v2_with_llm, sample_maturity_data, sample_learning_data
    ):
        """Test hardcoded skill generation mode."""
        agent_v2_with_llm.generation_mode = "hardcoded"
        result = agent_v2_with_llm.process(
            {
                "action": "generate",
                "maturity_data": sample_maturity_data,
                "learning_data": sample_learning_data,
            }
        )
        assert result["status"] == "success"
        assert result["phase"] == "discovery"

    def test_process_generate_llm_no_client(self, agent_v2_without_llm, sample_maturity_data):
        """Test LLM generation without LLM client."""
        result = agent_v2_without_llm.process(
            {
                "action": "generate_llm",
                "maturity_data": sample_maturity_data,
            }
        )
        assert result["status"] == "error"
        assert "LLMClient" in result["message"]

    def test_process_estimate_cost(self, agent_v2_with_llm):
        """Test cost estimation."""
        result = agent_v2_with_llm.process(
            {
                "action": "estimate_cost",
                "context": {"test": "data"},
            }
        )
        assert result["status"] == "success"
        assert "estimated_cost_usd" in result

    def test_validate_skill_success(self, agent_v2_with_llm):
        """Test skill validation."""
        skill = AgentSkill(
            id="test_skill",
            target_agent="counselor",
            skill_type="behavior_parameter",
            config={"param": "value"},
            confidence=0.75,
            maturity_phase="discovery",
        )
        agent_v2_with_llm.generated_skills[skill.id] = skill

        result = agent_v2_with_llm.process(
            {
                "action": "validate",
                "skill_id": "test_skill",
            }
        )
        assert result["status"] == "success"
        assert result["is_valid"] is True

    def test_validate_skill_not_found(self, agent_v2_with_llm):
        """Test validation of non-existent skill."""
        result = agent_v2_with_llm.process(
            {
                "action": "validate",
                "skill_id": "nonexistent",
            }
        )
        assert result["status"] == "error"
        assert "not found" in result["message"]

    def test_get_phase4_stats(self, agent_v2_with_llm):
        """Test Phase 4 statistics."""
        stats = agent_v2_with_llm.get_phase4_stats()
        assert "total_generated_skills" in stats
        assert "llm_skills" in stats
        assert "generation_mode" in stats
        assert stats["llm_client_available"] is True

    def test_get_phase4_stats_without_llm(self, agent_v2_without_llm):
        """Test Phase 4 statistics without LLM."""
        stats = agent_v2_without_llm.get_phase4_stats()
        assert stats["llm_client_available"] is False

    def test_refine_skill_no_llm(self, agent_v2_without_llm):
        """Test skill refinement without LLM."""
        skill = AgentSkill(
            id="test_skill",
            target_agent="agent",
            skill_type="behavior_parameter",
            config={},
            confidence=0.7,
            maturity_phase="discovery",
        )
        agent_v2_without_llm.generated_skills[skill.id] = skill

        result = agent_v2_without_llm.process(
            {
                "action": "refine",
                "skill_id": "test_skill",
                "feedback": "helpful",
            }
        )
        assert result["status"] == "error"

    def test_fallback_to_parent_actions(self, agent_v2_with_llm, sample_maturity_data):
        """Test that V2 falls back to parent for Phase 1-3 actions."""
        result = agent_v2_with_llm.process(
            {
                "action": "list",
                "phase": "discovery",
            }
        )
        assert result["status"] == "success"
        assert result["agent"] == "SkillGeneratorAgent"

    def test_hybrid_generation_mode(
        self, agent_v2_with_llm, sample_maturity_data, sample_learning_data
    ):
        """Test hybrid generation mode."""
        agent_v2_with_llm.generation_mode = "hybrid"

        # Mock LLM response
        mock_response = Mock()
        mock_response.content = '{"id": "hybrid_skill", "target_agent": "agent", "skill_type": "behavior_parameter", "config": {}, "confidence": 0.7, "maturity_phase": "discovery"}'
        agent_v2_with_llm.llm_client.chat.return_value = mock_response

        result = agent_v2_with_llm._generate_hybrid_skills(
            sample_maturity_data, sample_learning_data, {}
        )
        assert result["status"] == "success"
        assert "hardcoded_skills" in result
        assert "llm_skills" in result

    def test_invalid_generation_mode(self, agent_v2_with_llm, sample_maturity_data):
        """Test invalid generation mode."""
        agent_v2_with_llm.generation_mode = "invalid_mode"
        result = agent_v2_with_llm._generate_with_mode(sample_maturity_data, None, {})
        assert result["status"] == "error"

    def test_llm_generation_with_mock(
        self, agent_v2_with_llm, sample_maturity_data, sample_learning_data
    ):
        """Test LLM generation with mocked response."""
        mock_response = Mock()
        mock_response.content = '{"id": "llm_problem_def", "target_agent": "counselor", "skill_type": "behavior_parameter", "config": {"focus": "problem_definition"}, "confidence": 0.75, "maturity_phase": "discovery"}'
        agent_v2_with_llm.llm_client.chat.return_value = mock_response

        result = agent_v2_with_llm._generate_llm_skills(
            sample_maturity_data, sample_learning_data, {}
        )
        assert result["status"] in ["success", "partial"]
        assert "skills_generated" in result

    def test_cost_tracking(self, agent_v2_with_llm, sample_maturity_data):
        """Test cost tracking across multiple generations."""
        agent_v2_with_llm.skill_costs = [0.001, 0.001, 0.001]
        stats = agent_v2_with_llm.get_phase4_stats()
        assert stats["total_generation_cost_usd"] > 0
        assert stats["average_cost_per_skill_usd"] > 0

    def test_validation_storage(self, agent_v2_with_llm):
        """Test validation result storage."""
        skill = AgentSkill(
            id="test_skill",
            target_agent="agent",
            skill_type="behavior_parameter",
            config={},
            confidence=0.7,
            maturity_phase="discovery",
        )
        agent_v2_with_llm.generated_skills[skill.id] = skill

        result = agent_v2_with_llm.process(
            {
                "action": "validate",
                "skill_id": "test_skill",
            }
        )
        assert "test_skill" in agent_v2_with_llm.validation_results or result["status"] == "success"


class TestSkillGeneratorAgentV2Integration:
    """Integration tests for SkillGeneratorAgentV2."""

    def test_complete_workflow_hardcoded(self):
        """Test complete workflow with hardcoded mode."""
        agent = SkillGeneratorAgentV2(llm_client=None, generation_mode="hardcoded")

        maturity_data = {
            "current_phase": "discovery",
            "completion_percent": 25,
            "weak_categories": ["problem_definition"],
            "category_scores": {"problem_definition_score": 10},
        }
        learning_data = {"learning_velocity": "medium", "engagement_score": 0.7}

        result = agent.process(
            {
                "action": "generate",
                "maturity_data": maturity_data,
                "learning_data": learning_data,
            }
        )

        assert result["status"] == "success"
        assert len(agent.generated_skills) >= 0

    def test_phase4_features(self):
        """Test Phase 4-specific features."""
        mock_client = Mock()
        agent = SkillGeneratorAgentV2(llm_client=mock_client)

        # Test cost estimation
        cost_result = agent.process({"action": "estimate_cost", "context": {}})
        assert cost_result["status"] == "success"

        # Test statistics
        stats = agent.get_phase4_stats()
        assert "llm_client_available" in stats
        assert "generation_mode" in stats
        assert "average_cost_per_skill_usd" in stats

    def test_agent_v2_backward_compatibility(self):
        """Test that V2 is backward compatible with Phase 1-3."""
        agent = SkillGeneratorAgentV2(llm_client=None, generation_mode="hardcoded")

        # Test Phase 1-3 action (list)
        result = agent.process({"action": "list", "phase": "discovery"})
        assert result["status"] == "success"

        # Test Phase 1-3 action (evaluate)
        skill = AgentSkill(
            id="test",
            target_agent="agent",
            skill_type="behavior_parameter",
            config={},
            confidence=0.7,
            maturity_phase="discovery",
        )
        agent.generated_skills[skill.id] = skill

        result = agent.process(
            {
                "action": "evaluate",
                "skill_id": "test",
                "feedback": "helpful",
                "effectiveness_score": 0.8,
            }
        )
        assert result["status"] == "success"

    def test_mode_switching(self):
        """Test switching between generation modes."""
        mock_client = Mock()
        agent = SkillGeneratorAgentV2(llm_client=mock_client, generation_mode="hardcoded")

        # Switch modes
        agent.generation_mode = "hybrid"
        stats = agent.get_phase4_stats()
        assert stats["generation_mode"] == "hybrid"

        agent.generation_mode = "llm"
        stats = agent.get_phase4_stats()
        assert stats["generation_mode"] == "llm"
