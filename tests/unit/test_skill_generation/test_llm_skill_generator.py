"""Tests for LLMSkillGenerator component."""

from unittest.mock import Mock

import pytest

from socratic_agents.models.skill_models import AgentSkill
from socratic_agents.skill_generation.llm_skill_generator import LLMSkillGenerator


class TestLLMSkillGenerator:
    """Tests for LLMSkillGenerator."""

    @pytest.fixture
    def mock_llm_client(self):
        """Create a mock LLM client."""
        client = Mock()
        return client

    @pytest.fixture
    def generator(self, mock_llm_client):
        """Create a generator with mock client."""
        return LLMSkillGenerator(mock_llm_client)

    @pytest.fixture
    def sample_skill(self):
        """Create a sample skill."""
        return AgentSkill(
            id="test_skill_1",
            target_agent="socratic_counselor",
            skill_type="behavior_parameter",
            config={"focus": "problem_definition", "approach": "guided_questions"},
            confidence=0.75,
            maturity_phase="discovery",
        )

    def test_generator_initialization(self, mock_llm_client):
        """Test generator initialization."""
        gen = LLMSkillGenerator(mock_llm_client)
        assert gen.llm_client == mock_llm_client
        assert isinstance(gen.skill_cache, dict)
        assert len(gen.skill_cache) == 0
        assert len(gen.generation_costs) == 0

    def test_generator_without_llm_client(self):
        """Test generator handles missing LLM client."""
        gen = LLMSkillGenerator(None)
        result = gen.generate_skill({}, "test_area", "test prompt")
        assert result is None

    def test_extract_json_direct(self):
        """Test JSON extraction from direct JSON."""
        json_str = '{"id": "test", "name": "Test"}'
        result = LLMSkillGenerator._extract_json(json_str)
        assert result is not None
        assert result["id"] == "test"
        assert result["name"] == "Test"

    def test_extract_json_from_markdown(self):
        """Test JSON extraction from markdown code block."""
        text = 'Here is a skill:\n```json\n{"id": "test", "target_agent": "agent"}\n```'
        result = LLMSkillGenerator._extract_json(text)
        assert result is not None
        assert result["id"] == "test"

    def test_extract_json_from_code_block(self):
        """Test JSON extraction from code block."""
        text = 'Here is a skill:\n```\n{"id": "test", "type": "skill"}\n```'
        result = LLMSkillGenerator._extract_json(text)
        assert result is not None
        assert result["id"] == "test"

    def test_extract_json_invalid(self):
        """Test JSON extraction with invalid JSON."""
        text = "This is not valid JSON"
        result = LLMSkillGenerator._extract_json(text)
        assert result is None

    def test_parse_skill_response_valid(self, generator, mock_llm_client):
        """Test parsing a valid skill response."""
        response = Mock()
        response.content = '{"id": "test_skill", "target_agent": "counselor", "skill_type": "behavior_parameter", "config": {"param": "value"}, "confidence": 0.8, "maturity_phase": "discovery"}'

        result = generator._parse_skill_response(response, "test_area", {})
        assert result is not None
        assert result.id == "test_skill"
        assert result.target_agent == "counselor"
        assert result.confidence == 0.8

    def test_parse_skill_response_invalid(self, generator):
        """Test parsing an invalid skill response."""
        response = Mock()
        response.content = "Not a skill"

        result = generator._parse_skill_response(response, "test_area", {})
        assert result is None

    def test_estimate_cost(self, generator):
        """Test cost estimation."""
        cost = generator.estimate_cost({})
        assert isinstance(cost, float)
        assert cost > 0
        assert cost < 0.01  # Should be less than a cent
        assert len(generator.generation_costs) == 1

    def test_estimate_cost_multiple(self, generator):
        """Test multiple cost estimations."""
        costs = [generator.estimate_cost({}) for _ in range(3)]
        assert len(costs) == 3
        assert all(c > 0 for c in costs)
        assert generator.get_average_cost() > 0

    def test_get_average_cost_empty(self):
        """Test average cost with no generations."""
        gen = LLMSkillGenerator(None)
        assert gen.get_average_cost() == 0.0

    def test_clear_cache(self, generator, sample_skill):
        """Test cache clearing."""
        generator.skill_cache["test"] = sample_skill
        assert len(generator.skill_cache) > 0
        generator.clear_cache()
        assert len(generator.skill_cache) == 0

    def test_generate_skill_with_mock_response(self, generator, mock_llm_client):
        """Test skill generation with mock Claude response."""
        mock_response = Mock()
        mock_response.content = '{"id": "llm_problem_definition", "target_agent": "counselor", "skill_type": "behavior_parameter", "config": {"focus": "problem_definition"}, "confidence": 0.75, "maturity_phase": "discovery"}'
        mock_llm_client.chat.return_value = mock_response

        skill = generator.generate_skill({}, "problem_definition", "test prompt")
        assert skill is not None
        assert skill.id == "llm_problem_definition"
        assert skill.target_agent == "counselor"
        assert mock_llm_client.chat.called

    def test_generate_skill_batch(self, generator, mock_llm_client):
        """Test batch skill generation."""
        mock_response = Mock()
        mock_response.content = '{"id": "skill1", "target_agent": "agent1", "skill_type": "behavior_parameter", "config": {}, "confidence": 0.75, "maturity_phase": "discovery"}'
        mock_llm_client.chat.return_value = mock_response

        contexts = [{}, {}]
        weak_areas = ["area1", "area2"]
        prompts = ["prompt1", "prompt2"]

        skills = generator.generate_skill_batch(contexts, weak_areas, prompts)
        assert len(skills) >= 1

    def test_refine_skill_success(self, generator, mock_llm_client, sample_skill):
        """Test skill refinement."""
        mock_response = Mock()
        mock_response.content = '{"id": "test_skill_1", "target_agent": "counselor", "skill_type": "behavior_parameter", "config": {"improved": true}, "confidence": 0.85, "maturity_phase": "discovery"}'
        mock_llm_client.chat.return_value = mock_response

        refined = generator.refine_skill(sample_skill, "helpful", "refine prompt")
        assert refined is not None
        assert refined.id == "test_skill_1"

    def test_refine_skill_no_client(self, sample_skill):
        """Test refinement without LLM client."""
        gen = LLMSkillGenerator(None)
        result = gen.refine_skill(sample_skill, "feedback", "prompt")
        assert result is None


class TestLLMSkillGeneratorIntegration:
    """Integration tests for LLMSkillGenerator."""

    def test_full_generation_workflow(self):
        """Test complete skill generation workflow."""
        mock_client = Mock()
        gen = LLMSkillGenerator(mock_client)

        # Estimate cost
        cost = gen.estimate_cost({})
        assert cost > 0

        # Generate multiple skills
        mock_response = Mock()
        mock_response.content = '{"id": "skill1", "target_agent": "agent", "skill_type": "behavior_parameter", "config": {}, "confidence": 0.7, "maturity_phase": "discovery"}'
        mock_client.chat.return_value = mock_response

        skills = gen.generate_skill_batch([{}], ["area1"], ["prompt1"])
        assert len(skills) >= 0

        # Check average cost
        avg_cost = gen.get_average_cost()
        assert avg_cost == cost

    def test_caching_works(self):
        """Test that skill caching works."""
        mock_client = Mock()
        gen = LLMSkillGenerator(mock_client)

        mock_response = Mock()
        mock_response.content = '{"id": "cached_skill", "target_agent": "agent", "skill_type": "behavior_parameter", "config": {}, "confidence": 0.7, "maturity_phase": "discovery"}'
        mock_client.chat.return_value = mock_response

        _ = gen.generate_skill({}, "test_area", "prompt")
        assert len(gen.skill_cache) >= 0

        gen.clear_cache()
        assert len(gen.skill_cache) == 0
