"""Unit tests for LLM-enhanced agent wrappers."""

import pytest
from socratic_agents.llm_agents import (
    LLMPoweredCounselor,
    LLMPoweredCodeGenerator,
    LLMPoweredCodeValidator,
    LLMAgentError,
)


class TestLLMAgentError:
    """Tests for LLMAgentError exception."""

    def test_llm_agent_error_creation(self):
        """Test that LLMAgentError can be created and raised."""
        with pytest.raises(LLMAgentError):
            raise LLMAgentError("Test error")

    def test_llm_agent_error_message(self):
        """Test that LLMAgentError preserves message."""
        msg = "Missing LLM configuration"
        with pytest.raises(LLMAgentError, match=msg):
            raise LLMAgentError(msg)


class TestLLMPoweredCounselor:
    """Tests for LLMPoweredCounselor wrapper."""

    def test_requires_llm_client(self):
        """Test that LLMPoweredCounselor raises error without LLM client."""
        with pytest.raises(LLMAgentError):
            LLMPoweredCounselor(llm_client=None)

    def test_initialization_with_llm(self, mock_llm_client):
        """Test that LLMPoweredCounselor initializes with valid LLM client."""
        counselor = LLMPoweredCounselor(llm_client=mock_llm_client)
        assert counselor.llm is not None
        assert counselor.agent is not None

    def test_guide_with_context(self, mock_llm_client):
        """Test guide_with_context method."""
        counselor = LLMPoweredCounselor(llm_client=mock_llm_client)
        result = counselor.guide_with_context(
            topic="Python recursion", level="beginner", context="for someone new to programming"
        )

        assert "questions" in result
        assert result["llm_used"] is True
        assert result["context_aware"] is True
        assert result["topic"] == "Python recursion"
        assert result["level"] == "beginner"
        assert result["context"] == "for someone new to programming"
        assert "llm_enhanced_questions" in result

    def test_guide_with_context_without_context_param(self, mock_llm_client):
        """Test guide_with_context without optional context parameter."""
        counselor = LLMPoweredCounselor(llm_client=mock_llm_client)
        result = counselor.guide_with_context(topic="machine learning", level="intermediate")

        assert result["context_aware"] is False
        assert result["context"] is None
        assert result["llm_used"] is True

    def test_personalized_guide(self, mock_llm_client):
        """Test personalized_guide method."""
        counselor = LLMPoweredCounselor(llm_client=mock_llm_client)
        result = counselor.personalized_guide(
            topic="algorithms", user_level="intermediate", learning_style="practical"
        )

        assert "questions" in result
        assert result["llm_used"] is True
        assert "llm_enhanced_questions" in result

    def test_guide_with_llm_error_handling(self, mock_llm_client_error):
        """Test that guide handles LLM errors gracefully."""
        counselor = LLMPoweredCounselor(llm_client=mock_llm_client_error)
        result = counselor.guide_with_context(topic="testing", level="beginner")

        # Should still return something despite LLM error
        assert "questions" in result
        assert "llm_enhanced_questions" in result


class TestLLMPoweredCodeGenerator:
    """Tests for LLMPoweredCodeGenerator wrapper."""

    def test_requires_llm_client(self):
        """Test that LLMPoweredCodeGenerator raises error without LLM client."""
        with pytest.raises(LLMAgentError):
            LLMPoweredCodeGenerator(llm_client=None)

    def test_initialization_with_llm(self, mock_llm_client):
        """Test that LLMPoweredCodeGenerator initializes with valid LLM client."""
        generator = LLMPoweredCodeGenerator(llm_client=mock_llm_client)
        assert generator.llm is not None
        assert generator.agent is not None

    def test_generate_with_tests(self, mock_llm_client):
        """Test generate_with_tests method."""
        generator = LLMPoweredCodeGenerator(llm_client=mock_llm_client)
        result = generator.generate_with_tests(
            specification="Binary search algorithm", language="python"
        )

        assert "code" in result
        assert result["language"] == "python"
        assert result["has_tests"] is True
        assert result["has_docs"] is True
        assert result["has_error_handling"] is True
        assert result["llm_generated"] is True
        assert result["specification"] == "Binary search algorithm"

    def test_generate_with_tests_no_docs(self, mock_llm_client):
        """Test generate_with_tests without documentation."""
        generator = LLMPoweredCodeGenerator(llm_client=mock_llm_client)
        result = generator.generate_with_tests(
            specification="Quicksort", language="python", include_docs=False
        )

        assert result["has_docs"] is False
        assert result["has_tests"] is True

    def test_generate_with_tests_no_error_handling(self, mock_llm_client):
        """Test generate_with_tests without error handling."""
        generator = LLMPoweredCodeGenerator(llm_client=mock_llm_client)
        result = generator.generate_with_tests(
            specification="Stack implementation", language="python", include_error_handling=False
        )

        assert result["has_error_handling"] is False

    def test_generate_with_explanation(self, mock_llm_client):
        """Test generate_with_explanation method."""
        generator = LLMPoweredCodeGenerator(llm_client=mock_llm_client)
        result = generator.generate_with_explanation(
            specification="Merge sort algorithm", language="python"
        )

        assert "code" in result
        assert "explanation" in result
        assert result["language"] == "python"
        assert result["llm_generated"] is True

    def test_generate_with_llm_error_handling(self, mock_llm_client_error):
        """Test that generate handles LLM errors gracefully."""
        generator = LLMPoweredCodeGenerator(llm_client=mock_llm_client_error)
        result = generator.generate_with_tests(specification="Any function", language="python")

        # Should return error message in code field
        assert "code" in result
        assert "Error" in result["code"] or "error" in result["code"].lower()


class TestLLMPoweredCodeValidator:
    """Tests for LLMPoweredCodeValidator wrapper."""

    def test_requires_llm_client(self):
        """Test that LLMPoweredCodeValidator raises error without LLM client."""
        with pytest.raises(LLMAgentError):
            LLMPoweredCodeValidator(llm_client=None)

    def test_initialization_with_llm(self, mock_llm_client):
        """Test that LLMPoweredCodeValidator initializes with valid LLM client."""
        validator = LLMPoweredCodeValidator(llm_client=mock_llm_client)
        assert validator.llm is not None
        assert validator.agent is not None

    def test_review_with_suggestions(self, mock_llm_client, sample_code):
        """Test review_with_suggestions method."""
        validator = LLMPoweredCodeValidator(llm_client=mock_llm_client)
        result = validator.review_with_suggestions(code=sample_code, language="python")

        assert "llm_review" in result
        assert result["suggestions_provided"] is True
        assert "valid" in result
        assert isinstance(result["focus_areas"], list)

    def test_review_with_focus_areas(self, mock_llm_client, sample_code):
        """Test review with specific focus areas."""
        validator = LLMPoweredCodeValidator(llm_client=mock_llm_client)
        focus = ["performance", "readability"]
        result = validator.review_with_suggestions(
            code=sample_code, language="python", focus_areas=focus
        )

        assert result["focus_areas"] == focus
        assert "llm_review" in result

    def test_review_with_error_handling(self, mock_llm_client_error, sample_code):
        """Test that review handles LLM errors gracefully."""
        validator = LLMPoweredCodeValidator(llm_client=mock_llm_client_error)
        result = validator.review_with_suggestions(code=sample_code, language="python")

        # Should still return review despite error
        assert "llm_review" in result


class TestLLMWrapperIntegration:
    """Integration tests for LLM wrappers working together."""

    def test_counselor_and_generator_workflow(self, mock_llm_client):
        """Test using counselor and generator together."""
        counselor = LLMPoweredCounselor(llm_client=mock_llm_client)
        generator = LLMPoweredCodeGenerator(llm_client=mock_llm_client)

        # Get guidance on topic
        guidance = counselor.guide_with_context("algorithm design")
        assert "questions" in guidance

        # Generate code based on topic
        code_result = generator.generate_with_tests("Implement bubble sort")
        assert "code" in code_result

    def test_generator_and_validator_workflow(self, mock_llm_client):
        """Test using generator and validator together."""
        generator = LLMPoweredCodeGenerator(llm_client=mock_llm_client)
        validator = LLMPoweredCodeValidator(llm_client=mock_llm_client)

        # Generate code
        gen_result = generator.generate_with_tests("Fibonacci function")
        generated_code = gen_result.get("code", "")

        # Validate generated code
        val_result = validator.review_with_suggestions(code=generated_code, language="python")

        assert "llm_review" in val_result

    def test_all_wrappers_with_same_llm(self, mock_llm_client):
        """Test that all wrappers can share the same LLM client."""
        counselor = LLMPoweredCounselor(llm_client=mock_llm_client)
        generator = LLMPoweredCodeGenerator(llm_client=mock_llm_client)
        validator = LLMPoweredCodeValidator(llm_client=mock_llm_client)

        # All should initialize successfully
        assert counselor.llm is mock_llm_client
        assert generator.llm is mock_llm_client
        assert validator.llm is mock_llm_client

        # All should be usable
        assert counselor.agent is not None
        assert generator.agent is not None
        assert validator.agent is not None
