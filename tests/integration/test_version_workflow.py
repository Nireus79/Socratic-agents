"""Integration tests for Phase 6: Skill Versioning & Compatibility Workflows."""

import uuid
from unittest.mock import Mock

import pytest

from socratic_agents.agents.skill_generator_agent_v2 import SkillGeneratorAgentV2
from socratic_agents.integrations.skill_orchestrator import SkillOrchestrator
from socratic_agents.models.skill_models import AgentSkill
from socratic_agents.skill_generation.compatibility_checker import CompatibilityChecker
from socratic_agents.skill_generation.skill_version_manager import SkillVersionManager


class TestCreateAndVersionSkill:
    """Test creating a skill and verifying initial version."""

    def test_generate_skill_has_default_version(self):
        """Test that generated skills have version 1.0.0."""
        agent = SkillGeneratorAgentV2()

        result = agent.process(
            {
                "action": "generate",
                "maturity_data": {
                    "current_phase": "discovery",
                    "completion_percent": 50,
                    "weak_categories": ["problem_definition"],
                },
                "learning_data": {"code_length": 100, "issue_count": 5},
                "context": {"session_id": str(uuid.uuid4())},
            }
        )

        assert result["status"] == "success"
        assert len(result["skills"]) > 0

        skill = result["skills"][0]
        assert "version" in skill
        assert skill["version"] == "1.0.0"
        assert skill["schema_version"] == "1.0"


class TestRefineCreatesNewVersion:
    """Test that refining a skill creates a new version."""

    @pytest.fixture
    def mock_llm_client(self):
        """Create a mock LLM client for refinement."""
        client = Mock()
        client.chat.return_value = Mock(
            content='{"id": "refined_skill", "target_agent": "agent1", "skill_type": "behavior_parameter", "config": {"param": "refined_value"}, "confidence": 0.9, "maturity_phase": "discovery"}'
        )
        return client

    def test_refine_increments_patch_version(self, mock_llm_client):
        """Test refinement with minor feedback increments patch version."""
        agent = SkillGeneratorAgentV2(llm_client=mock_llm_client)

        # Generate initial skill
        gen_result = agent.process(
            {
                "action": "generate",
                "maturity_data": {
                    "current_phase": "discovery",
                    "completion_percent": 50,
                    "weak_categories": ["problem_definition"],
                },
                "learning_data": {"code_length": 100, "issue_count": 5},
                "context": {"session_id": str(uuid.uuid4())},
            }
        )

        assert gen_result["status"] == "success"
        skill_id = gen_result["skills"][0]["id"]
        original_version = gen_result["skills"][0]["version"]

        # Refine skill with patch feedback
        refine_result = agent.process(
            {
                "action": "refine",
                "skill_id": skill_id,
                "feedback": "Improve clarity in the prompt",
            }
        )

        assert refine_result["status"] == "success"
        refined_version = refine_result["refined_version"]
        assert refined_version != original_version
        assert refined_version == "1.0.1"
        assert refine_result["refined_skill"]["parent_skill_id"] == skill_id
        assert refine_result["refined_skill"]["parent_version"] == original_version

    def test_refine_increments_minor_version_for_feature(self, mock_llm_client):
        """Test refinement with feature feedback increments minor version."""
        agent = SkillGeneratorAgentV2(llm_client=mock_llm_client)

        # Generate initial skill
        gen_result = agent.process(
            {
                "action": "generate",
                "maturity_data": {
                    "current_phase": "discovery",
                    "completion_percent": 50,
                    "weak_categories": ["problem_definition"],
                },
                "learning_data": {"code_length": 100, "issue_count": 5},
                "context": {"session_id": str(uuid.uuid4())},
            }
        )

        skill_id = gen_result["skills"][0]["id"]

        # Refine with feature feedback
        refine_result = agent.process(
            {
                "action": "refine",
                "skill_id": skill_id,
                "feedback": "Add new multi-step approach feature",
            }
        )

        assert refine_result["status"] == "success"
        assert refine_result["refined_version"] == "1.1.0"

    def test_refine_increments_major_version_for_breaking_change(self, mock_llm_client):
        """Test refinement with breaking change feedback increments major version."""
        agent = SkillGeneratorAgentV2(llm_client=mock_llm_client)

        # Generate initial skill
        gen_result = agent.process(
            {
                "action": "generate",
                "maturity_data": {
                    "current_phase": "discovery",
                    "completion_percent": 50,
                    "weak_categories": ["problem_definition"],
                },
                "learning_data": {"code_length": 100, "issue_count": 5},
                "context": {"session_id": str(uuid.uuid4())},
            }
        )

        skill_id = gen_result["skills"][0]["id"]

        # Refine with breaking change feedback
        refine_result = agent.process(
            {
                "action": "refine",
                "skill_id": skill_id,
                "feedback": "Breaking: redesign entire approach to be incompatible",
            }
        )

        assert refine_result["status"] == "success"
        assert refine_result["refined_version"] == "2.0.0"


class TestUpgradeWorkflow:
    """Test upgrading skills to newer versions."""

    def test_upgrade_from_v1_to_v2(self):
        """Test upgrading skill from version 1.0.0 to 2.0.0."""
        manager = SkillVersionManager()

        # Create v1
        skill_v1 = AgentSkill(
            id="test_skill",
            target_agent="agent1",
            skill_type="behavior_parameter",
            config={"param": "value1"},
            confidence=0.8,
            maturity_phase="discovery",
            version="1.0.0",
        )

        manager.register_version(skill_v1, created_by="test")
        assert manager.get_latest_version("test_skill") == "1.0.0"

        # Create v2
        skill_v2 = AgentSkill(
            id="test_skill",
            target_agent="agent1",
            skill_type="behavior_parameter",
            config={"param": "value2"},
            confidence=0.9,
            maturity_phase="discovery",
            version="2.0.0",
            parent_skill_id="test_skill",
            parent_version="1.0.0",
        )

        manager.register_version(skill_v2, created_by="test")
        assert manager.get_latest_version("test_skill") == "2.0.0"

        # Upgrade
        upgraded = manager.upgrade_skill("test_skill", "1.0.0", "2.0.0")
        assert upgraded.version == "2.0.0"
        assert upgraded.parent_skill_id == "test_skill"
        assert upgraded.parent_version == "1.0.0"


class TestDeprecationWorkflow:
    """Test deprecating skills and finding replacements."""

    def test_deprecate_skill_version(self):
        """Test deprecating a skill version."""
        manager = SkillVersionManager()

        # Create v1
        skill_v1 = AgentSkill(
            id="old_skill",
            target_agent="agent1",
            skill_type="behavior_parameter",
            config={"param": "value1"},
            confidence=0.7,
            maturity_phase="discovery",
            version="1.0.0",
        )

        manager.register_version(skill_v1, created_by="test")

        # Create v2 (replacement)
        skill_v2 = AgentSkill(
            id="old_skill",
            target_agent="agent1",
            skill_type="behavior_parameter",
            config={"param": "value2"},
            confidence=0.95,
            maturity_phase="discovery",
            version="2.0.0",
            parent_skill_id="old_skill",
            parent_version="1.0.0",
        )

        manager.register_version(skill_v2, created_by="test")

        # Deprecate v1 in favor of v2
        manager.deprecate_version(
            "old_skill",
            "1.0.0",
            reason="Replaced by improved version",
            replacement_version="2.0.0",
        )

        # Check that latest version skips deprecated (returns v2)
        latest = manager.get_latest_version("old_skill")
        assert latest == "2.0.0"

        # Check that v1 is marked deprecated
        v1 = manager.get_version("old_skill", "1.0.0")
        assert v1.deprecated is True
        assert v1.replacement_version == "2.0.0"


class TestDependencyResolution:
    """Test dependency validation and resolution."""

    def test_dependency_validation_satisfied(self):
        """Test that satisfied dependencies validate successfully."""
        checker = CompatibilityChecker()

        # Register dependency skill
        dep_skill = AgentSkill(
            id="base_skill",
            target_agent="agent",
            skill_type="type",
            config={},
            confidence=0.9,
            maturity_phase="discovery",
            version="1.5.0",
        )
        checker.register_available_skill(dep_skill)

        # Create skill with dependency
        skill = AgentSkill(
            id="dependent_skill",
            target_agent="agent",
            skill_type="type",
            config={},
            confidence=0.9,
            maturity_phase="discovery",
            version="1.0.0",
            dependencies=[
                {"skill_id": "base_skill", "min_version": "1.0.0", "max_version": "2.0.0"}
            ],
        )

        # Validate
        result = checker.check_dependencies(skill)
        assert result.is_compatible
        assert len(result.missing_dependencies) == 0
        assert len(result.version_conflicts) == 0

    def test_dependency_validation_missing(self):
        """Test that missing dependencies are detected."""
        checker = CompatibilityChecker()

        # Create skill with missing dependency
        skill = AgentSkill(
            id="dependent_skill",
            target_agent="agent",
            skill_type="type",
            config={},
            confidence=0.9,
            maturity_phase="discovery",
            version="1.0.0",
            dependencies=[{"skill_id": "missing_skill", "min_version": "1.0.0"}],
        )

        # Validate
        result = checker.check_dependencies(skill)
        assert not result.is_compatible
        assert "missing_skill" in result.missing_dependencies

    def test_dependency_tree_validation_no_circular(self):
        """Test that valid dependency tree passes validation."""
        checker = CompatibilityChecker()

        # Create skill A (no dependencies)
        skill_a = AgentSkill(
            id="skill_a",
            target_agent="agent",
            skill_type="type",
            config={},
            confidence=0.9,
            maturity_phase="discovery",
            version="1.0.0",
        )

        # Create skill B (depends on A)
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

        # Validate B
        is_valid, errors = checker.validate_dependency_tree(skill_b)
        assert is_valid
        assert len(errors) == 0

    def test_dependency_tree_validation_circular(self):
        """Test that circular dependencies are detected."""
        checker = CompatibilityChecker()

        # Create skill A depends on B
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

        # Create skill B depends on A (circular)
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

        # Validate A (should find circular)
        is_valid, errors = checker.validate_dependency_tree(skill_a)
        assert not is_valid
        assert len(errors) > 0
        assert any("Circular" in error for error in errors)


class TestCompatibilityWithOrchestrator:
    """Test skill compatibility checking in SkillOrchestrator."""

    def test_apply_compatible_skill(self):
        """Test applying a compatible skill through orchestrator."""
        version_manager = SkillVersionManager()
        orchestrator = SkillOrchestrator(version_manager=version_manager)

        # Create compatible skill
        skill_dict = {
            "id": "test_skill",
            "target_agent": "socratic_counselor",
            "skill_type": "behavior_parameter",
            "config": {"param": "value"},
            "confidence": 0.9,
            "maturity_phase": "discovery",
            "version": "1.0.0",
            "schema_version": "1.0",
        }

        # Apply skill
        result = orchestrator.apply_and_track_skill("test_skill", skill_dict, feedback="applied")

        assert result["status"] == "success"
        assert result["skill_id"] == "test_skill"
        assert result["applied"] is True
        assert result["version"] == "1.0.0"

    def test_apply_incompatible_skill_agent_type(self):
        """Test that incompatible skill type is rejected."""
        orchestrator = SkillOrchestrator()

        # Create skill with unsupported type for agent
        skill_dict = {
            "id": "test_skill",
            "target_agent": "socratic_counselor",
            "skill_type": "unsupported_type",
            "config": {"param": "value"},
            "confidence": 0.9,
            "maturity_phase": "discovery",
            "version": "1.0.0",
        }

        # Try to apply
        result = orchestrator.apply_and_track_skill("test_skill", skill_dict, feedback="applied")

        assert result["status"] == "error"
        assert "compatibility_issues" in result
        assert len(result["compatibility_issues"]) > 0

    def test_apply_skill_with_unsatisfied_dependencies(self):
        """Test that skill with missing dependencies is rejected."""
        orchestrator = SkillOrchestrator()

        # Create skill with missing dependency
        skill_dict = {
            "id": "dependent_skill",
            "target_agent": "socratic_counselor",
            "skill_type": "behavior_parameter",
            "config": {"param": "value"},
            "confidence": 0.9,
            "maturity_phase": "discovery",
            "version": "1.0.0",
            "dependencies": [{"skill_id": "missing_base_skill", "min_version": "1.0.0"}],
        }

        # Try to apply
        result = orchestrator.apply_and_track_skill(
            "dependent_skill", skill_dict, feedback="applied"
        )

        assert result["status"] == "error"
        assert "missing_dependencies" in result
        assert "missing_base_skill" in result["missing_dependencies"]


class TestBackwardCompatibility:
    """Test backward compatibility with legacy skills."""

    def test_legacy_skill_without_version(self):
        """Test that skills without version field are handled gracefully."""
        # Create skill without version field (legacy)
        legacy_skill_dict = {
            "id": "legacy_skill",
            "target_agent": "agent1",
            "skill_type": "behavior_parameter",
            "config": {"param": "value"},
            "confidence": 0.8,
            "maturity_phase": "discovery",
            # Note: no version field
        }

        # Try to convert to AgentSkill
        skill = AgentSkill.from_dict(legacy_skill_dict)

        # Should get default version
        assert skill.version == "1.0.0" or skill.version is None  # Depends on implementation
        assert skill.schema_version == "1.0" or skill.schema_version is None

    def test_orchestrator_with_legacy_skill_dict(self):
        """Test orchestrator handles skill dict with missing version fields."""
        orchestrator = SkillOrchestrator()

        # Create legacy skill dict without version
        legacy_skill_dict = {
            "id": "legacy_skill",
            "target_agent": "socratic_counselor",
            "skill_type": "behavior_parameter",
            "config": {"param": "value"},
            "confidence": 0.8,
            "maturity_phase": "discovery",
            # Note: no version field
        }

        # Try to apply (should handle gracefully)
        result = orchestrator.apply_and_track_skill(
            "legacy_skill", legacy_skill_dict, feedback="applied"
        )

        # Should either succeed with auto-upgrade or fail gracefully, not crash
        assert result["status"] in ["success", "error"]


class TestVersionConflictDetection:
    """Test conflict detection between multiple skills."""

    def test_detect_config_conflicts_same_agent(self):
        """Test detection of conflicting configurations on same agent."""
        checker = CompatibilityChecker()

        # Create two skills with conflicting configs for same agent
        skill1 = AgentSkill(
            id="skill_001",
            target_agent="agent1",
            skill_type="behavior_parameter",
            config={"param": "value1"},
            confidence=0.9,
            maturity_phase="discovery",
            version="1.0.0",
        )

        skill2 = AgentSkill(
            id="skill_002",
            target_agent="agent1",
            skill_type="behavior_parameter",
            config={"param": "value2"},
            confidence=0.9,
            maturity_phase="discovery",
            version="1.0.0",
        )

        # Detect conflicts
        conflicts = checker.detect_conflicts([skill1, skill2])
        assert len(conflicts) > 0

    def test_no_conflicts_different_agents(self):
        """Test that skills for different agents don't conflict."""
        checker = CompatibilityChecker()

        skill1 = AgentSkill(
            id="skill_001",
            target_agent="agent1",
            skill_type="behavior_parameter",
            config={"param": "value1"},
            confidence=0.9,
            maturity_phase="discovery",
            version="1.0.0",
        )

        skill2 = AgentSkill(
            id="skill_002",
            target_agent="agent2",
            skill_type="behavior_parameter",
            config={"param": "value1"},
            confidence=0.9,
            maturity_phase="discovery",
            version="1.0.0",
        )

        conflicts = checker.detect_conflicts([skill1, skill2])
        assert len(conflicts) == 0


class TestMultiAgentCompatibility:
    """Test skill compatibility across multiple agents."""

    def test_compatibility_matrix_generation(self):
        """Test building compatibility matrix for multiple agents."""
        checker = CompatibilityChecker()

        # Register agents and capabilities
        checker.register_agent_capability("agent1", "behavior_parameter", "1.0")
        checker.register_agent_capability("agent2", "method", "1.0")

        # Create skills
        skill1 = AgentSkill(
            id="skill_001",
            target_agent="agent1",
            skill_type="behavior_parameter",
            config={},
            confidence=0.9,
            maturity_phase="discovery",
            version="1.0.0",
        )

        skill2 = AgentSkill(
            id="skill_002",
            target_agent="agent2",
            skill_type="method",
            config={},
            confidence=0.9,
            maturity_phase="discovery",
            version="1.0.0",
        )

        # Generate matrix
        matrix = checker.get_compatibility_matrix([skill1, skill2], ["agent1", "agent2"])

        # skill1 should be compatible with agent1 only
        assert matrix["skill_001"]["agent1"] is True
        assert matrix["skill_001"]["agent2"] is False

        # skill2 should be compatible with agent2 only
        assert matrix["skill_002"]["agent1"] is False
        assert matrix["skill_002"]["agent2"] is True

    def test_skill_compatible_with_multiple_agents(self):
        """Test skill explicitly compatible with multiple agents."""
        checker = CompatibilityChecker()

        checker.register_agent_capability("agent1", "behavior_parameter", "1.0")
        checker.register_agent_capability("agent2", "behavior_parameter", "1.0")

        # Create skill compatible with multiple agents
        skill = AgentSkill(
            id="multi_agent_skill",
            target_agent="agent1",
            skill_type="behavior_parameter",
            config={},
            confidence=0.9,
            maturity_phase="discovery",
            version="1.0.0",
            compatible_agents=["agent1", "agent2"],
        )

        # Check compatibility with both
        result1 = checker.check_compatibility(skill, "agent1")
        result2 = checker.check_compatibility(skill, "agent2")

        assert result1.is_compatible
        assert result2.is_compatible
