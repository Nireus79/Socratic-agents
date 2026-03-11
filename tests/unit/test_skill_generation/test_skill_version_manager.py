"""Tests for SkillVersionManager (Phase 6)."""

import pytest

from socratic_agents.models.skill_models import AgentSkill
from socratic_agents.skill_generation.skill_version_manager import SkillVersionManager


class TestSkillVersionManagerInitialization:
    """Test SkillVersionManager initialization."""

    def test_initialization(self):
        """Test manager initializes correctly."""
        manager = SkillVersionManager()
        assert manager.versions == {}
        assert manager.latest_versions == {}
        assert manager.deprecated_versions == {}
        assert manager.version_history == []


class TestVersionRegistration:
    """Test version registration."""

    @pytest.fixture
    def manager(self):
        return SkillVersionManager()

    @pytest.fixture
    def sample_skill(self):
        return AgentSkill(
            id="test_skill_001",
            target_agent="test_agent",
            skill_type="behavior_parameter",
            config={"key": "value"},
            confidence=0.9,
            maturity_phase="discovery",
            version="1.0.0",
        )

    def test_register_new_skill(self, manager, sample_skill):
        """Test registering a new skill version."""
        success = manager.register_version(sample_skill)
        assert success
        assert "test_skill_001" in manager.versions
        assert "1.0.0" in manager.versions["test_skill_001"]

    def test_register_duplicate_version(self, manager, sample_skill):
        """Test registering duplicate version fails."""
        manager.register_version(sample_skill)
        success = manager.register_version(sample_skill)
        assert not success

    def test_register_updates_latest(self, manager, sample_skill):
        """Test registration updates latest version."""
        manager.register_version(sample_skill)
        assert manager.latest_versions["test_skill_001"] == "1.0.0"

    def test_register_multiple_versions(self, manager, sample_skill):
        """Test registering multiple versions."""
        manager.register_version(sample_skill)

        skill_v2 = AgentSkill(
            id="test_skill_001",
            target_agent="test_agent",
            skill_type="behavior_parameter",
            config={"key": "value2"},
            confidence=0.9,
            maturity_phase="discovery",
            version="1.1.0",
        )
        manager.register_version(skill_v2)

        assert len(manager.versions["test_skill_001"]) == 2
        assert manager.latest_versions["test_skill_001"] == "1.1.0"

    def test_register_with_changelog(self, manager, sample_skill):
        """Test registering version with changelog."""
        success = manager.register_version(sample_skill, changelog="Bug fixes and improvements")
        assert success
        skill_version = manager.versions["test_skill_001"]["1.0.0"]
        assert skill_version.changelog == "Bug fixes and improvements"


class TestVersionRetrieval:
    """Test version retrieval."""

    @pytest.fixture
    def manager_with_skills(self):
        manager = SkillVersionManager()
        skill_v1 = AgentSkill(
            id="skill_001",
            target_agent="agent",
            skill_type="type",
            config={},
            confidence=0.9,
            maturity_phase="discovery",
            version="1.0.0",
        )
        skill_v2 = AgentSkill(
            id="skill_001",
            target_agent="agent",
            skill_type="type",
            config={},
            confidence=0.9,
            maturity_phase="discovery",
            version="2.0.0",
        )
        manager.register_version(skill_v1)
        manager.register_version(skill_v2)
        return manager

    def test_get_latest_version(self, manager_with_skills):
        """Test retrieving latest version."""
        skill = manager_with_skills.get_version("skill_001")
        assert skill is not None
        assert skill.version == "2.0.0"

    def test_get_specific_version(self, manager_with_skills):
        """Test retrieving specific version."""
        skill = manager_with_skills.get_version("skill_001", "1.0.0")
        assert skill is not None
        assert skill.version == "1.0.0"

    def test_get_nonexistent_skill(self, manager_with_skills):
        """Test retrieving nonexistent skill."""
        skill = manager_with_skills.get_version("nonexistent")
        assert skill is None

    def test_get_nonexistent_version(self, manager_with_skills):
        """Test retrieving nonexistent version."""
        skill = manager_with_skills.get_version("skill_001", "99.0.0")
        assert skill is None


class TestVersionListing:
    """Test version listing."""

    @pytest.fixture
    def manager_with_skills(self):
        manager = SkillVersionManager()
        for i in range(1, 4):
            skill = AgentSkill(
                id="skill_001",
                target_agent="agent",
                skill_type="type",
                config={},
                confidence=0.9,
                maturity_phase="discovery",
                version=f"{i}.0.0",
            )
            manager.register_version(skill)
        return manager

    def test_list_versions(self, manager_with_skills):
        """Test listing all versions."""
        versions = manager_with_skills.list_versions("skill_001")
        assert len(versions) == 3
        assert versions[0] == "3.0.0"  # Newest first
        assert versions[1] == "2.0.0"
        assert versions[2] == "1.0.0"

    def test_list_versions_empty(self, manager_with_skills):
        """Test listing versions for nonexistent skill."""
        versions = manager_with_skills.list_versions("nonexistent")
        assert versions == []


class TestVersionUpgrade:
    """Test version upgrade functionality."""

    @pytest.fixture
    def manager_with_skills(self):
        manager = SkillVersionManager()
        for i in range(1, 4):
            skill = AgentSkill(
                id="skill_001",
                target_agent="agent",
                skill_type="type",
                config={},
                confidence=0.9,
                maturity_phase="discovery",
                version=f"{i}.0.0",
            )
            manager.register_version(skill)
        return manager

    def test_upgrade_to_latest(self, manager_with_skills):
        """Test upgrading to latest version."""
        upgraded = manager_with_skills.upgrade_skill("skill_001", "1.0.0")
        assert upgraded is not None
        assert upgraded.version == "3.0.0"

    def test_upgrade_to_specific(self, manager_with_skills):
        """Test upgrading to specific version."""
        upgraded = manager_with_skills.upgrade_skill("skill_001", "1.0.0", "2.0.0")
        assert upgraded is not None
        assert upgraded.version == "2.0.0"

    def test_upgrade_invalid_path(self, manager_with_skills):
        """Test invalid upgrade path (downgrade)."""
        upgraded = manager_with_skills.upgrade_skill("skill_001", "3.0.0", "2.0.0")
        assert upgraded is None


class TestVersionDeprecation:
    """Test version deprecation."""

    @pytest.fixture
    def manager_with_skills(self):
        manager = SkillVersionManager()
        skill_v1 = AgentSkill(
            id="skill_001",
            target_agent="agent",
            skill_type="type",
            config={},
            confidence=0.9,
            maturity_phase="discovery",
            version="1.0.0",
        )
        skill_v2 = AgentSkill(
            id="skill_001",
            target_agent="agent",
            skill_type="type",
            config={},
            confidence=0.9,
            maturity_phase="discovery",
            version="2.0.0",
        )
        manager.register_version(skill_v1)
        manager.register_version(skill_v2)
        return manager

    def test_deprecate_version(self, manager_with_skills):
        """Test deprecating a version."""
        success = manager_with_skills.deprecate_version(
            "skill_001",
            "1.0.0",
            "Obsolete",
            replacement_version="2.0.0",
        )
        assert success
        assert "1.0.0" in manager_with_skills.deprecated_versions["skill_001"]

    def test_deprecate_latest_updates_latest(self, manager_with_skills):
        """Test deprecating latest version updates latest pointer."""
        manager_with_skills.deprecate_version(
            "skill_001",
            "2.0.0",
            "Obsolete",
        )
        assert manager_with_skills.latest_versions["skill_001"] == "1.0.0"

    def test_deprecate_nonexistent(self, manager_with_skills):
        """Test deprecating nonexistent version."""
        success = manager_with_skills.deprecate_version("skill_001", "99.0.0", "Missing")
        assert not success

    def test_list_versions_excludes_deprecated(self, manager_with_skills):
        """Test list excludes deprecated by default."""
        manager_with_skills.deprecate_version("skill_001", "1.0.0", "Obsolete")
        versions = manager_with_skills.list_versions("skill_001")
        assert "1.0.0" not in versions
        assert "2.0.0" in versions


class TestVersionComparison:
    """Test version comparison."""

    @pytest.fixture
    def manager(self):
        return SkillVersionManager()

    def test_compare_equal(self, manager):
        """Test comparing equal versions."""
        result = manager.compare_versions("1.0.0", "1.0.0")
        assert result == 0

    def test_compare_less_than(self, manager):
        """Test comparing older version."""
        result = manager.compare_versions("1.0.0", "2.0.0")
        assert result == -1

    def test_compare_greater_than(self, manager):
        """Test comparing newer version."""
        result = manager.compare_versions("2.0.0", "1.0.0")
        assert result == 1

    def test_compare_minor_versions(self, manager):
        """Test comparing minor versions."""
        assert manager.compare_versions("1.0.0", "1.1.0") == -1
        assert manager.compare_versions("1.1.0", "1.0.0") == 1

    def test_compare_patch_versions(self, manager):
        """Test comparing patch versions."""
        assert manager.compare_versions("1.0.0", "1.0.1") == -1
        assert manager.compare_versions("1.0.1", "1.0.0") == 1


class TestVersionIncrement:
    """Test version incrementing."""

    @pytest.fixture
    def manager(self):
        return SkillVersionManager()

    def test_increment_major(self, manager):
        """Test incrementing major version."""
        new_version = manager.increment_version("1.2.3", "major")
        assert new_version == "2.0.0"

    def test_increment_minor(self, manager):
        """Test incrementing minor version."""
        new_version = manager.increment_version("1.2.3", "minor")
        assert new_version == "1.3.0"

    def test_increment_patch(self, manager):
        """Test incrementing patch version."""
        new_version = manager.increment_version("1.2.3", "patch")
        assert new_version == "1.2.4"

    def test_increment_invalid_part(self, manager):
        """Test incrementing invalid part raises error."""
        with pytest.raises(ValueError):
            manager.increment_version("1.0.0", "invalid")


class TestVersionHistory:
    """Test version history tracking."""

    @pytest.fixture
    def manager_with_history(self):
        manager = SkillVersionManager()
        skill = AgentSkill(
            id="skill_001",
            target_agent="agent",
            skill_type="type",
            config={},
            confidence=0.9,
            maturity_phase="discovery",
            version="1.0.0",
        )
        manager.register_version(skill)
        manager.deprecate_version("skill_001", "1.0.0", "Old")
        return manager

    def test_get_all_history(self, manager_with_history):
        """Test retrieving all history."""
        history = manager_with_history.get_version_history()
        assert len(history) >= 2

    def test_filter_history_by_skill(self, manager_with_history):
        """Test filtering history by skill ID."""
        history = manager_with_history.get_version_history(skill_id="skill_001")
        assert all(h.get("skill_id") == "skill_001" for h in history)

    def test_filter_history_by_action(self, manager_with_history):
        """Test filtering history by action."""
        history = manager_with_history.get_version_history(action="deprecate")
        assert all(h.get("action") == "deprecate" for h in history)


class TestManagerStats:
    """Test version manager statistics."""

    def test_stats_empty_manager(self):
        """Test stats for empty manager."""
        manager = SkillVersionManager()
        stats = manager.get_stats()
        assert stats["total_skills"] == 0
        assert stats["total_versions"] == 0
        assert stats["total_deprecated"] == 0

    def test_stats_with_skills(self):
        """Test stats with registered skills."""
        manager = SkillVersionManager()
        for i in range(3):
            skill = AgentSkill(
                id=f"skill_{i}",
                target_agent="agent",
                skill_type="type",
                config={},
                confidence=0.9,
                maturity_phase="discovery",
                version="1.0.0",
            )
            manager.register_version(skill)

        stats = manager.get_stats()
        assert stats["total_skills"] == 3
        assert stats["total_versions"] == 3
        assert stats["avg_versions_per_skill"] == 1.0


class TestVersionDownloadTracking:
    """Test download count tracking."""

    def test_download_count_increments(self):
        """Test download count increments on retrieval."""
        manager = SkillVersionManager()
        skill = AgentSkill(
            id="skill_001",
            target_agent="agent",
            skill_type="type",
            config={},
            confidence=0.9,
            maturity_phase="discovery",
            version="1.0.0",
        )
        manager.register_version(skill)

        # Retrieve multiple times
        manager.get_version("skill_001")
        manager.get_version("skill_001")

        # Check download count
        skill_version = manager.versions["skill_001"]["1.0.0"]
        assert skill_version.download_count == 2
