"""Tests for CompatibilityChecker (Phase 6)."""

import pytest

from socratic_agents.models.skill_models import AgentSkill
from socratic_agents.skill_generation.compatibility_checker import CompatibilityChecker
from socratic_agents.skill_generation.skill_version_manager import SkillVersionManager


class TestCompatibilityCheckerInitialization:
    """Test CompatibilityChecker initialization."""

    def test_initialization_default(self):
        """Test checker initializes with defaults."""
        checker = CompatibilityChecker()
        assert checker.agent_capabilities == {}
        assert checker.available_skills == {}
        assert checker.version_manager is None

    def test_initialization_with_version_manager(self):
        """Test checker with version manager."""
        vm = SkillVersionManager()
        checker = CompatibilityChecker(version_manager=vm)
        assert checker.version_manager is vm


class TestAgentCapabilityRegistration:
    """Test agent capability registration."""

    @pytest.fixture
    def checker(self):
        return CompatibilityChecker()

    def test_register_single_capability(self, checker):
        """Test registering single agent capability."""
        checker.register_agent_capability("agent1", "type1", "1.0")
        assert "agent1" in checker.agent_capabilities
        assert "type1" in checker.agent_capabilities["agent1"]
        assert checker.agent_capabilities["agent1"]["type1"] == "1.0"

    def test_register_multiple_capabilities(self, checker):
        """Test registering multiple capabilities."""
        checker.register_agent_capability("agent1", "type1", "1.0")
        checker.register_agent_capability("agent1", "type2", "1.0")
        assert len(checker.agent_capabilities["agent1"]) == 2


class TestCompatibilityChecking:
    """Test skill compatibility checking."""

    @pytest.fixture
    def checker_with_capabilities(self):
        checker = CompatibilityChecker()
        checker.register_agent_capability("agent1", "behavior_parameter", "1.0")
        return checker

    @pytest.fixture
    def compatible_skill(self):
        return AgentSkill(
            id="skill_001",
            target_agent="agent1",
            skill_type="behavior_parameter",
            config={},
            confidence=0.9,
            maturity_phase="discovery",
            version="1.0.0",
            schema_version="1.0",
        )

    def test_check_compatible_skill(self, checker_with_capabilities, compatible_skill):
        """Test checking compatible skill."""
        result = checker_with_capabilities.check_compatibility(compatible_skill)
        assert result.is_compatible
        assert len(result.issues) == 0

    def test_check_unsupported_type(self, checker_with_capabilities):
        """Test checking skill with unsupported type."""
        skill = AgentSkill(
            id="skill_001",
            target_agent="agent1",
            skill_type="unsupported_type",
            config={},
            confidence=0.9,
            maturity_phase="discovery",
            version="1.0.0",
        )
        result = checker_with_capabilities.check_compatibility(skill)
        assert not result.is_compatible
        assert len(result.issues) > 0

    def test_check_deprecated_skill_warning(self, checker_with_capabilities, compatible_skill):
        """Test deprecated skill generates warning."""
        compatible_skill.deprecated = True
        compatible_skill.replacement_version = "2.0.0"
        result = checker_with_capabilities.check_compatibility(compatible_skill)
        assert len(result.warnings) > 0


class TestDependencyChecking:
    """Test dependency checking."""

    @pytest.fixture
    def checker_with_skills(self):
        checker = CompatibilityChecker()

        # Register available skills
        dep_skill = AgentSkill(
            id="dep_skill",
            target_agent="agent",
            skill_type="type",
            config={},
            confidence=0.9,
            maturity_phase="discovery",
            version="1.5.0",
        )
        checker.register_available_skill(dep_skill)

        return checker

    def test_check_dependencies_satisfied(self, checker_with_skills):
        """Test dependencies satisfied."""
        skill = AgentSkill(
            id="skill_001",
            target_agent="agent",
            skill_type="type",
            config={},
            confidence=0.9,
            maturity_phase="discovery",
            version="1.0.0",
            dependencies=[
                {"skill_id": "dep_skill", "min_version": "1.0.0", "max_version": "2.0.0"}
            ],
        )
        result = checker_with_skills.check_dependencies(skill)
        assert result.is_compatible
        assert len(result.missing_dependencies) == 0

    def test_check_missing_dependency(self, checker_with_skills):
        """Test missing dependency detected."""
        skill = AgentSkill(
            id="skill_001",
            target_agent="agent",
            skill_type="type",
            config={},
            confidence=0.9,
            maturity_phase="discovery",
            version="1.0.0",
            dependencies=[{"skill_id": "missing_skill", "min_version": "1.0.0"}],
        )
        result = checker_with_skills.check_dependencies(skill)
        assert not result.is_compatible
        assert "missing_skill" in result.missing_dependencies

    def test_check_version_conflict(self, checker_with_skills):
        """Test version conflict detected."""
        skill = AgentSkill(
            id="skill_001",
            target_agent="agent",
            skill_type="type",
            config={},
            confidence=0.9,
            maturity_phase="discovery",
            version="1.0.0",
            dependencies=[{"skill_id": "dep_skill", "min_version": "2.0.0"}],  # dep is 1.5.0
        )
        result = checker_with_skills.check_dependencies(skill)
        assert not result.is_compatible
        assert len(result.version_conflicts) > 0


class TestConflictDetection:
    """Test conflict detection between skills."""

    @pytest.fixture
    def checker(self):
        return CompatibilityChecker()

    def test_detect_no_conflicts_different_agents(self, checker):
        """Test no conflicts with different target agents."""
        skill1 = AgentSkill(
            id="skill_001",
            target_agent="agent1",
            skill_type="type1",
            config={},
            confidence=0.9,
            maturity_phase="discovery",
            version="1.0.0",
        )
        skill2 = AgentSkill(
            id="skill_002",
            target_agent="agent2",
            skill_type="type2",
            config={},
            confidence=0.9,
            maturity_phase="discovery",
            version="1.0.0",
        )
        conflicts = checker.detect_conflicts([skill1, skill2])
        assert len(conflicts) == 0

    def test_detect_config_conflicts(self, checker):
        """Test detecting config conflicts."""
        skill1 = AgentSkill(
            id="skill_001",
            target_agent="agent1",
            skill_type="type1",
            config={"param": "value1"},
            confidence=0.9,
            maturity_phase="discovery",
            version="1.0.0",
        )
        skill2 = AgentSkill(
            id="skill_002",
            target_agent="agent1",
            skill_type="type1",
            config={"param": "value2"},
            confidence=0.9,
            maturity_phase="discovery",
            version="1.0.0",
        )
        conflicts = checker.detect_conflicts([skill1, skill2])
        assert len(conflicts) > 0


class TestDependencyTreeValidation:
    """Test dependency tree validation."""

    @pytest.fixture
    def checker_with_tree(self):
        checker = CompatibilityChecker()

        # Build dependency tree
        skill_a = AgentSkill(
            id="skill_a",
            target_agent="agent",
            skill_type="type",
            config={},
            confidence=0.9,
            maturity_phase="discovery",
            version="1.0.0",
        )
        skill_b = AgentSkill(
            id="skill_b",
            target_agent="agent",
            skill_type="type",
            config={},
            confidence=0.9,
            maturity_phase="discovery",
            version="1.0.0",
            dependencies=[{"skill_id": "skill_a"}],
        )

        checker.register_available_skill(skill_a)
        checker.register_available_skill(skill_b)

        return checker

    def test_validate_valid_tree(self, checker_with_tree):
        """Test validating valid dependency tree."""
        skill = checker_with_tree.available_skills["skill_b"]
        is_valid, errors = checker_with_tree.validate_dependency_tree(skill)
        assert is_valid
        assert len(errors) == 0

    def test_detect_circular_dependency(self):
        """Test detecting circular dependencies."""
        checker = CompatibilityChecker()

        # Create circular dependency
        skill_a = AgentSkill(
            id="skill_a",
            target_agent="agent",
            skill_type="type",
            config={},
            confidence=0.9,
            maturity_phase="discovery",
            version="1.0.0",
            dependencies=[{"skill_id": "skill_b"}],
        )
        skill_b = AgentSkill(
            id="skill_b",
            target_agent="agent",
            skill_type="type",
            config={},
            confidence=0.9,
            maturity_phase="discovery",
            version="1.0.0",
            dependencies=[{"skill_id": "skill_a"}],
        )

        checker.register_available_skill(skill_a)
        checker.register_available_skill(skill_b)

        is_valid, errors = checker.validate_dependency_tree(skill_a)
        assert not is_valid
        assert len(errors) > 0


class TestCompatibilityMatrix:
    """Test compatibility matrix generation."""

    def test_build_compatibility_matrix(self):
        """Test building compatibility matrix."""
        checker = CompatibilityChecker()
        checker.register_agent_capability("agent1", "type1", "1.0")
        checker.register_agent_capability("agent2", "type2", "1.0")

        skill1 = AgentSkill(
            id="skill_001",
            target_agent="agent1",
            skill_type="type1",
            config={},
            confidence=0.9,
            maturity_phase="discovery",
            version="1.0.0",
            schema_version="1.0",
        )

        matrix = checker.get_compatibility_matrix([skill1], ["agent1", "agent2"])
        assert "skill_001" in matrix
        assert "agent1" in matrix["skill_001"]
        assert matrix["skill_001"]["agent1"] is True


class TestOptionalDependencies:
    """Test optional dependency handling."""

    def test_optional_dependency_not_found(self):
        """Test optional dependency not found doesn't fail."""
        checker = CompatibilityChecker()
        skill = AgentSkill(
            id="skill_001",
            target_agent="agent",
            skill_type="type",
            config={},
            confidence=0.9,
            maturity_phase="discovery",
            version="1.0.0",
            dependencies=[{"skill_id": "missing_optional", "optional": True}],
        )
        result = checker.check_dependencies(skill)
        assert result.is_compatible
        assert "missing_optional" not in result.missing_dependencies
