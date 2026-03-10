"""Unit tests for Socratic Agents."""

import pytest
from socratic_agents import (
    BaseAgent,
    SocraticCounselor,
    CodeGenerator,
    CodeValidator,
)


class TestBaseAgent:
    """Test BaseAgent functionality."""

    def test_base_agent_initialization(self):
        """Test creating a base agent."""
        # BaseAgent is abstract, so create a concrete subclass
        counselor = SocraticCounselor()
        assert counselor.name == "SocraticCounselor"
        assert counselor.created_at is not None

    def test_agent_string_representation(self):
        """Test agent string representation."""
        counselor = SocraticCounselor()
        assert "SocraticCounselor" in str(counselor)


class TestSocraticCounselor:
    """Test Socratic Counselor agent."""

    @pytest.mark.unit
    def test_initialization(self):
        """Test counselor initialization."""
        counselor = SocraticCounselor()
        assert counselor.name == "SocraticCounselor"

    @pytest.mark.unit
    def test_guide_learning_with_topic(self):
        """Test guiding learning on a topic."""
        counselor = SocraticCounselor()
        result = counselor.guide("recursion", level="beginner")
        
        assert result["status"] == "success"
        assert result["topic"] == "recursion"
        assert "questions" in result
        assert len(result["questions"]) > 0

    @pytest.mark.unit
    def test_guide_learning_different_levels(self):
        """Test guidance at different levels."""
        counselor = SocraticCounselor()
        
        for level in ["beginner", "intermediate", "advanced"]:
            result = counselor.guide("Python", level=level)
            assert result["level"] == level
            assert len(result["questions"]) > 0

    @pytest.mark.unit
    def test_guide_learning_without_topic(self):
        """Test guidance without topic fails gracefully."""
        counselor = SocraticCounselor()
        result = counselor.process({"topic": ""})
        
        assert result["status"] == "error"


class TestCodeGenerator:
    """Test Code Generator agent."""

    @pytest.mark.unit
    def test_initialization(self):
        """Test code generator initialization."""
        generator = CodeGenerator()
        assert generator.name == "CodeGenerator"

    @pytest.mark.unit
    def test_generate_code(self):
        """Test code generation."""
        generator = CodeGenerator()
        result = generator.process({
            "prompt": "Create a function to add two numbers",
            "language": "python"
        })
        
        assert result["status"] == "success"
        assert "code" in result
        assert result["language"] == "python"

    @pytest.mark.unit
    def test_generate_without_prompt(self):
        """Test generation without prompt fails gracefully."""
        generator = CodeGenerator()
        result = generator.process({"prompt": ""})
        
        assert result["status"] == "error"


class TestCodeValidator:
    """Test Code Validator agent."""

    @pytest.mark.unit
    def test_initialization(self):
        """Test validator initialization."""
        validator = CodeValidator()
        assert validator.name == "CodeValidator"

    @pytest.mark.unit
    def test_validate_valid_code(self):
        """Test validating valid code."""
        validator = CodeValidator()
        code = "def add(a, b):\n    return a + b"
        result = validator.validate(code, language="python")
        
        assert result["status"] == "success"
        assert "issues" in result
        assert "valid" in result

    @pytest.mark.unit
    def test_validate_empty_code(self):
        """Test validation of empty code."""
        validator = CodeValidator()
        result = validator.validate("", language="python")

        # Empty code is an error (code is required)
        assert result["status"] == "error"

    @pytest.mark.unit
    def test_validate_without_code(self):
        """Test validation without code fails gracefully."""
        validator = CodeValidator()
        result = validator.process({"code": ""})
        
        assert result["status"] == "error"
