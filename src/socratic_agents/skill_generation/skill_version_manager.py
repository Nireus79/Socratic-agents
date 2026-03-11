"""Skill Version Manager for Phase 6: Skill Versioning & Compatibility."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from ..models.skill_models import AgentSkill, SkillVersion


class SkillVersionManager:
    """
    Manages skill versions, upgrades, and version history.

    Provides semantic versioning for skills with:
    - Version registration and tracking
    - Version comparison and ordering
    - Upgrade path management
    - Deprecation workflow
    - Version history queries
    """

    def __init__(self):
        """Initialize version manager."""
        self.logger = logging.getLogger(f"socratic_agents.{self.__class__.__name__}")

        # Storage: {skill_id: {version: SkillVersion}}
        self.versions: Dict[str, Dict[str, SkillVersion]] = {}

        # Latest version cache: {skill_id: version_string}
        self.latest_versions: Dict[str, str] = {}

        # Deprecation tracking
        self.deprecated_versions: Dict[str, List[str]] = {}

        # Version history
        self.version_history: List[Dict[str, Any]] = []

    def register_version(
        self,
        skill: AgentSkill,
        changelog: Optional[str] = None,
        created_by: str = "system",
    ) -> bool:
        """
        Register a new skill version.

        Args:
            skill: Skill to register
            changelog: Description of changes in this version
            created_by: Who created this version

        Returns:
            True if registered successfully, False otherwise
        """
        try:
            skill_id = skill.id
            version = skill.version

            # Initialize skill entry if needed
            if skill_id not in self.versions:
                self.versions[skill_id] = {}

            # Check if version already exists
            if version in self.versions[skill_id]:
                self.logger.warning(f"Version {version} already exists for skill {skill_id}")
                return False

            # Create version entry
            skill_version = SkillVersion(
                skill_id=skill_id,
                version=version,
                skill=skill,
                created_at=datetime.utcnow(),
                created_by=created_by,
                changelog=changelog,
            )

            # Store version
            self.versions[skill_id][version] = skill_version

            # Update latest version if this is newer
            self._update_latest_version(skill_id, version)

            # Track in history
            self.version_history.append(
                {
                    "action": "register",
                    "skill_id": skill_id,
                    "version": version,
                    "timestamp": datetime.utcnow().isoformat(),
                    "created_by": created_by,
                }
            )

            self.logger.info(f"Registered skill {skill_id} version {version}")
            return True

        except Exception as e:
            self.logger.error(f"Error registering version: {e}")
            return False

    def get_version(
        self,
        skill_id: str,
        version: Optional[str] = None,
    ) -> Optional[AgentSkill]:
        """
        Get a specific skill version.

        Args:
            skill_id: Skill identifier
            version: Version to retrieve (None = latest)

        Returns:
            AgentSkill or None if not found
        """
        if skill_id not in self.versions:
            return None

        # Get latest if version not specified
        if version is None:
            version = self.latest_versions.get(skill_id)
            if version is None:
                return None

        # Retrieve version
        skill_version = self.versions[skill_id].get(version)
        if skill_version:
            skill_version.download_count += 1
            return skill_version.skill

        return None

    def list_versions(
        self,
        skill_id: str,
        include_deprecated: bool = False,
    ) -> List[str]:
        """
        List all versions of a skill.

        Args:
            skill_id: Skill identifier
            include_deprecated: Whether to include deprecated versions

        Returns:
            List of version strings, sorted newest to oldest
        """
        if skill_id not in self.versions:
            return []

        versions = list(self.versions[skill_id].keys())

        # Filter deprecated if requested
        if not include_deprecated:
            deprecated = self.deprecated_versions.get(skill_id, [])
            versions = [v for v in versions if v not in deprecated]

        # Sort by semantic version (newest first)
        versions.sort(key=lambda v: self._parse_version(v), reverse=True)

        return versions

    def get_latest_version(self, skill_id: str) -> Optional[str]:
        """Get the latest non-deprecated version of a skill."""
        return self.latest_versions.get(skill_id)

    def upgrade_skill(
        self,
        skill_id: str,
        from_version: str,
        to_version: Optional[str] = None,
    ) -> Optional[AgentSkill]:
        """
        Upgrade a skill to a newer version.

        Args:
            skill_id: Skill to upgrade
            from_version: Current version
            to_version: Target version (None = latest)

        Returns:
            Upgraded skill or None if upgrade fails
        """
        # Get target version
        if to_version is None:
            to_version = self.get_latest_version(skill_id)
            if to_version is None:
                self.logger.error(f"No latest version found for {skill_id}")
                return None

        # Validate upgrade path
        if not self._is_valid_upgrade(from_version, to_version):
            self.logger.error(f"Invalid upgrade from {from_version} to {to_version}")
            return None

        # Get new version
        new_skill = self.get_version(skill_id, to_version)
        if new_skill is None:
            self.logger.error(f"Version {to_version} not found for {skill_id}")
            return None

        # Track upgrade
        self.version_history.append(
            {
                "action": "upgrade",
                "skill_id": skill_id,
                "from_version": from_version,
                "to_version": to_version,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        self.logger.info(f"Upgraded {skill_id} from {from_version} to {to_version}")
        return new_skill

    def deprecate_version(
        self,
        skill_id: str,
        version: str,
        reason: str,
        replacement_version: Optional[str] = None,
        migration_guide: Optional[str] = None,
    ) -> bool:
        """
        Mark a skill version as deprecated.

        Args:
            skill_id: Skill identifier
            version: Version to deprecate
            reason: Why it's being deprecated
            replacement_version: Recommended replacement version
            migration_guide: How to migrate

        Returns:
            True if deprecated successfully
        """
        if skill_id not in self.versions or version not in self.versions[skill_id]:
            self.logger.error(f"Version {version} not found for {skill_id}")
            return False

        # Get the skill version
        skill_version = self.versions[skill_id][version]
        skill = skill_version.skill

        # Mark as deprecated
        skill.deprecated = True
        skill.deprecation_reason = reason
        if replacement_version:
            skill.replacement_skill_id = skill_id
            skill.replacement_version = replacement_version
        if migration_guide:
            skill.migration_guide = migration_guide

        # Track deprecation
        if skill_id not in self.deprecated_versions:
            self.deprecated_versions[skill_id] = []
        self.deprecated_versions[skill_id].append(version)

        # Update latest version if this was the latest
        if self.latest_versions.get(skill_id) == version:
            self._recalculate_latest_version(skill_id)

        self.version_history.append(
            {
                "action": "deprecate",
                "skill_id": skill_id,
                "version": version,
                "reason": reason,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        self.logger.info(f"Deprecated {skill_id} version {version}")
        return True

    def compare_versions(self, v1: str, v2: str) -> int:
        """
        Compare two version strings.

        Returns:
            -1 if v1 < v2, 0 if v1 == v2, 1 if v1 > v2
        """
        t1 = self._parse_version(v1)
        t2 = self._parse_version(v2)

        if t1 < t2:
            return -1
        elif t1 > t2:
            return 1
        return 0

    def get_version_history(
        self,
        skill_id: Optional[str] = None,
        action: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get version history, optionally filtered.

        Args:
            skill_id: Filter by skill ID
            action: Filter by action type

        Returns:
            List of history entries
        """
        history = self.version_history

        if skill_id:
            history = [h for h in history if h.get("skill_id") == skill_id]

        if action:
            history = [h for h in history if h.get("action") == action]

        return history

    def increment_version(
        self,
        current_version: str,
        part: str = "patch",
    ) -> str:
        """
        Increment a version number.

        Args:
            current_version: Current version string
            part: Which part to increment ("major", "minor", "patch")

        Returns:
            New version string
        """
        major, minor, patch = self._parse_version(current_version)

        if part == "major":
            return f"{major + 1}.0.0"
        elif part == "minor":
            return f"{major}.{minor + 1}.0"
        elif part == "patch":
            return f"{major}.{minor}.{patch + 1}"
        else:
            raise ValueError(f"Invalid part: {part}")

    def get_stats(self) -> Dict[str, Any]:
        """Get version manager statistics."""
        total_skills = len(self.versions)
        total_versions = sum(len(versions) for versions in self.versions.values())
        total_deprecated = sum(len(v) for v in self.deprecated_versions.values())

        return {
            "total_skills": total_skills,
            "total_versions": total_versions,
            "total_deprecated": total_deprecated,
            "avg_versions_per_skill": total_versions / total_skills if total_skills > 0 else 0,
        }

    # Helper methods

    def _parse_version(self, version: str) -> Tuple[int, int, int]:
        """Parse version string to tuple."""
        parts = version.split(".")
        if len(parts) != 3:
            raise ValueError(f"Invalid version format: {version}")
        return (int(parts[0]), int(parts[1]), int(parts[2]))

    def _update_latest_version(self, skill_id: str, new_version: str) -> None:
        """Update latest version cache."""
        current_latest = self.latest_versions.get(skill_id)

        if current_latest is None or self.compare_versions(new_version, current_latest) > 0:
            # Check if not deprecated
            if new_version not in self.deprecated_versions.get(skill_id, []):
                self.latest_versions[skill_id] = new_version

    def _recalculate_latest_version(self, skill_id: str) -> None:
        """Recalculate latest non-deprecated version."""
        versions = self.list_versions(skill_id, include_deprecated=False)
        if versions:
            self.latest_versions[skill_id] = versions[0]
        else:
            self.latest_versions.pop(skill_id, None)

    def _is_valid_upgrade(self, from_version: str, to_version: str) -> bool:
        """Check if upgrade path is valid."""
        return self.compare_versions(to_version, from_version) > 0
