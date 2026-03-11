"""Tests for SkillValidationEngine component."""

import pytest
from socratic_agents.skill_generation.skill_validation_engine import (
    SkillValidationEngine,
    ValidationResult,
)
from socratic_agents.models.skill_models import AgentSkill


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_validation_result_initialization(self):
        """Test ValidationResult initialization."""
        result = ValidationResult(is_valid=True, skill_id="test_skill")
        assert result.is_valid is True
        assert result.skill_id == "test_skill"
        assert len(result.errors) == 0
        assert len(result.warnings) == 0

    def test_validation_result_with_errors(self):
        """Test ValidationResult with errors."""
        result = ValidationResult(
            is_valid=False,
            skill_id="bad_skill",
            errors=["Missing id", "Invalid config"],
        )
        assert result.is_valid is False
        assert len(result.errors) == 2

    def test_validation_result_to_dict(self):
        """Test ValidationResult conversion to dict."""
        result = ValidationResult(
            is_valid=True,
            skill_id="test",
            errors=["error1"],
            warnings=["warning1"],
        )
        data = result.to_dict()
        assert data["is_valid"] is True
        assert data["skill_id"] == "test"
        assert "error1" in data["errors"]


class TestSkillValidationEngine:
    """Tests for SkillValidationEngine."""

    @pytest.fixture
    def engine(self):
        """Create a validation engine."""
        return SkillValidationEngine()

    @pytest.fixture
    def valid_skill(self):
        """Create a valid skill."""
        return AgentSkill(
            id="valid_skill_1",
            target_agent="socratic_counselor",
            skill_type="behavior_parameter",
            config={"focus": "problem_definition"},
            confidence=0.75,
            maturity_phase="discovery",
        )

    def test_engine_initialization(self):
        """Test engine initialization."""
        engine = SkillValidationEngine()
        assert engine is not None
        assert engine.max_skill_id_length == 50
        assert len(engine.harmful_patterns) > 0

    def test_validate_valid_skill(self, engine, valid_skill):
        """Test validation of a valid skill."""
        result = engine.validate_skill(valid_skill)
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert result.safety_checks_passed is True

    def test_validate_skill_missing_id(self, engine):
        """Test validation with missing ID."""
        skill = AgentSkill(
            id="",
            target_agent="agent",
            skill_type="behavior_parameter",
            config={},
            confidence=0.7,
            maturity_phase="discovery",
        )
        result = engine.validate_skill(skill)
        assert result.is_valid is False
        assert any("id" in e.lower() for e in result.errors)

    def test_validate_skill_missing_target_agent(self, engine):
        """Test validation with missing target agent."""
        skill = AgentSkill(
            id="test_skill",
            target_agent="",
            skill_type="behavior_parameter",
            config={},
            confidence=0.7,
            maturity_phase="discovery",
        )
        result = engine.validate_skill(skill)
        assert result.is_valid is False

    def test_validate_skill_missing_skill_type(self, engine):
        """Test validation with missing skill type."""
        skill = AgentSkill(
            id="test_skill",
            target_agent="agent",
            skill_type="",
            config={},
            confidence=0.7,
            maturity_phase="discovery",
        )
        result = engine.validate_skill(skill)
        assert result.is_valid is False

    def test_validate_skill_invalid_confidence(self, engine, valid_skill):
        """Test validation with invalid confidence."""
        valid_skill.confidence = 1.5
        result = engine.validate_skill(valid_skill)
        assert result.is_valid is False
        assert any("confidence" in e.lower() for e in result.errors)

    def test_validate_skill_harmful_pattern_in_id(self, engine):
        """Test validation detects harmful patterns in ID."""
        skill = AgentSkill(
            id="skill_delete_data",
            target_agent="agent",
            skill_type="behavior_parameter",
            config={},
            confidence=0.7,
            maturity_phase="discovery",
        )
        result = engine.validate_skill(skill)
        assert result.is_valid is False
        assert result.safety_checks_passed is False

    def test_validate_skill_harmful_pattern_in_config(self, engine):
        """Test validation detects harmful patterns in config."""
        skill = AgentSkill(
            id="test_skill",
            target_agent="agent",
            skill_type="behavior_parameter",
            config={"instruction": "exploit system"},
            confidence=0.7,
            maturity_phase="discovery",
        )
        result = engine.validate_skill(skill)
        assert result.is_valid is False
        assert result.safety_checks_passed is False

    def test_validate_skill_invalid_maturity_phase(self, engine, valid_skill):
        """Test validation with invalid maturity phase."""
        valid_skill.maturity_phase = "invalid_phase"
        result = engine.validate_skill(valid_skill)
        assert not result.convention_compliant
        assert any("maturity" in w.lower() for w in result.warnings)

    def test_validate_skill_invalid_skill_type(self, engine, valid_skill):
        """Test validation with invalid skill type."""
        valid_skill.skill_type = "invalid_type"
        result = engine.validate_skill(valid_skill)
        assert not result.convention_compliant
        assert any("skill type" in w.lower() for w in result.warnings)

    def test_validate_batch_single_skill(self, engine, valid_skill):
        """Test batch validation with single skill."""
        results = engine.validate_batch([valid_skill])
        assert len(results) == 1
        assert valid_skill.id in results
        assert results[valid_skill.id].is_valid is True

    def test_validate_batch_multiple_skills(self, engine):
        """Test batch validation with multiple skills."""
        skills = [
            AgentSkill(
                id=f"skill_{i}",
                target_agent="agent",
                skill_type="behavior_parameter",
                config={},
                confidence=0.7,
                maturity_phase="discovery",
            )
            for i in range(3)
        ]
        results = engine.validate_batch(skills)
        assert len(results) == 3

    def test_validate_batch_mixed_validity(self, engine):
        """Test batch validation with valid and invalid skills."""
        skills = [
            AgentSkill(
                id="good_skill",
                target_agent="agent",
                skill_type="behavior_parameter",
                config={},
                confidence=0.7,
                maturity_phase="discovery",
            ),
            AgentSkill(
                id="",
                target_agent="agent",
                skill_type="behavior_parameter",
                config={},
                confidence=0.7,
                maturity_phase="discovery",
            ),
        ]
        results = engine.validate_batch(skills)
        assert len(results) == 2

    def test_is_valid_identifier_valid(self, engine):
        """Test valid identifier checking."""
        assert engine._is_valid_identifier("valid_skill_name") is True
        assert engine._is_valid_identifier("skill1") is True
        assert engine._is_valid_identifier("_private_skill") is True

    def test_is_valid_identifier_invalid(self, engine):
        """Test invalid identifier checking."""
        assert engine._is_valid_identifier("1invalid") is False
        assert engine._is_valid_identifier("invalid-skill") is False
        assert engine._is_valid_identifier("invalid.skill") is False
        assert engine._is_valid_identifier("") is False

    def test_contains_harmful_pattern(self, engine):
        """Test harmful pattern detection."""
        assert engine._contains_harmful_pattern("delete data") is True
        assert engine._contains_harmful_pattern("shutdown system") is True
        assert engine._contains_harmful_pattern("normal operation") is False
        assert engine._contains_harmful_pattern("DELETE") is True


class TestSkillValidationEngineIntegration:
    """Integration tests for SkillValidationEngine."""

    def test_full_validation_workflow(self):
        """Test complete validation workflow."""
        engine = SkillValidationEngine()

        # Create multiple skills
        skills = [
            AgentSkill(
                id="skill_discovery_1",
                target_agent="counselor",
                skill_type="behavior_parameter",
                config={"approach": "guided"},
                confidence=0.75,
                maturity_phase="discovery",
            ),
            AgentSkill(
                id="skill_definition_1",
                target_agent="codeGenerator",
                skill_type="method",
                config={"pattern": "MVC"},
                confidence=0.8,
                maturity_phase="definition",
            ),
        ]

        # Validate all
        results = engine.validate_batch(skills)

        # Check results
        assert len(results) == 2
        valid_count = sum(1 for r in results.values() if r.is_valid)
        assert valid_count >= 1

    def test_validation_catches_configuration_issues(self):
        """Test that validation catches common configuration issues."""
        engine = SkillValidationEngine()

        issues = [
            (
                "missing_target",
                AgentSkill(
                    id="test",
                    target_agent="",
                    skill_type="behavior_parameter",
                    config={},
                    confidence=0.7,
                    maturity_phase="discovery",
                ),
            ),
            (
                "bad_confidence",
                AgentSkill(
                    id="test",
                    target_agent="agent",
                    skill_type="behavior_parameter",
                    config={},
                    confidence=2.0,
                    maturity_phase="discovery",
                ),
            ),
            (
                "bad_phase",
                AgentSkill(
                    id="test",
                    target_agent="agent",
                    skill_type="behavior_parameter",
                    config={},
                    confidence=0.7,
                    maturity_phase="unknown",
                ),
            ),
        ]

        for issue_name, skill in issues:
            result = engine.validate_skill(skill)
            assert result.is_valid is False or not result.convention_compliant
