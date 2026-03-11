"""Compatibility Checker for Phase 6: Skill Versioning & Compatibility."""

import logging
from typing import Any, Dict, List, Optional, Set, Tuple

from ..models.skill_models import AgentSkill, CompatibilityResult, DependencyConstraint


class CompatibilityChecker:
    """
    Check skill compatibility with agents and dependencies.

    Provides:
    - Agent compatibility verification
    - Dependency resolution
    - Version constraint checking
    - Conflict detection
    - Upgrade path validation
    """

    def __init__(self, version_manager=None):
        """
        Initialize compatibility checker.

        Args:
            version_manager: SkillVersionManager instance (optional)
        """
        self.logger = logging.getLogger(f"socratic_agents.{self.__class__.__name__}")
        self.version_manager = version_manager

        # Agent compatibility matrix: {agent_name: {skill_type: schema_version}}
        self.agent_capabilities: Dict[str, Dict[str, str]] = {}

        # Registered skills for dependency checking
        self.available_skills: Dict[str, AgentSkill] = {}

    def register_agent_capability(
        self,
        agent_name: str,
        skill_type: str,
        schema_version: str = "1.0",
    ) -> None:
        """
        Register what skill types an agent can handle.

        Args:
            agent_name: Name of the agent
            skill_type: Type of skill it supports
            schema_version: Schema version it supports
        """
        if agent_name not in self.agent_capabilities:
            self.agent_capabilities[agent_name] = {}

        self.agent_capabilities[agent_name][skill_type] = schema_version
        self.logger.debug(f"Registered {agent_name} capability: {skill_type} v{schema_version}")

    def register_available_skill(self, skill: AgentSkill) -> None:
        """Register a skill as available for dependency checking."""
        self.available_skills[skill.id] = skill

    def check_compatibility(
        self,
        skill: AgentSkill,
        target_agent: Optional[str] = None,
    ) -> CompatibilityResult:
        """
        Check if a skill is compatible with target agent.

        Args:
            skill: Skill to check
            target_agent: Target agent (None = use skill.target_agent)

        Returns:
            CompatibilityResult with details
        """
        agent = target_agent or skill.target_agent
        issues: List[str] = []
        warnings: List[str] = []

        # Check agent capability
        if agent in self.agent_capabilities:
            agent_caps = self.agent_capabilities[agent]

            # Check if agent supports skill type
            if skill.skill_type not in agent_caps:
                issues.append(f"Agent {agent} does not support skill type '{skill.skill_type}'")
            else:
                # Check schema version compatibility
                agent_schema = agent_caps[skill.skill_type]
                if agent_schema != skill.schema_version:
                    warnings.append(
                        f"Schema version mismatch: agent={agent_schema}, skill={skill.schema_version}"
                    )
        else:
            warnings.append(f"No capability information for agent {agent}")

        # Check if skill is deprecated
        if skill.deprecated:
            warnings.append(f"Skill version {skill.version} is deprecated")
            if skill.replacement_version:
                warnings.append(f"Use replacement version {skill.replacement_version} instead")

        # Check compatible_agents list
        if skill.compatible_agents and agent not in skill.compatible_agents:
            issues.append(f"Skill is not compatible with agent {agent}")

        return CompatibilityResult(
            is_compatible=len(issues) == 0,
            skill_id=skill.id,
            version=skill.version,
            issues=issues,
            warnings=warnings,
        )

    def check_dependencies(
        self,
        skill: AgentSkill,
        available_skills: Optional[Dict[str, AgentSkill]] = None,
    ) -> CompatibilityResult:
        """
        Check if all skill dependencies are satisfied.

        Args:
            skill: Skill to check
            available_skills: Available skills (uses registered if None)

        Returns:
            CompatibilityResult with dependency status
        """
        skills_to_check = available_skills or self.available_skills

        issues: List[str] = []
        warnings: List[str] = []
        missing_deps: List[str] = []
        version_conflicts: List[Tuple[str, str, str]] = []

        # Check each dependency
        for dep_dict in skill.dependencies:
            dep_id = dep_dict.get("skill_id")
            if not dep_id:
                continue

            min_version = dep_dict.get("min_version")
            max_version = dep_dict.get("max_version")
            optional = dep_dict.get("optional", False)

            # Check if dependency is available
            if dep_id not in skills_to_check:
                if not optional:
                    missing_deps.append(dep_id)
                    issues.append(f"Required dependency missing: {dep_id}")
                else:
                    warnings.append(f"Optional dependency missing: {dep_id}")
                continue

            # Check version constraints
            dep_skill = skills_to_check[dep_id]
            dep_version = dep_skill.version

            constraint = DependencyConstraint(
                skill_id=dep_id,
                min_version=min_version,
                max_version=max_version,
                optional=optional,
            )

            if not constraint.is_satisfied_by(dep_version):
                version_range = f"{min_version or '0'}-{max_version or 'any'}"
                version_conflicts.append((dep_id, version_range, dep_version))
                issues.append(
                    f"Dependency {dep_id} version {dep_version} does not satisfy"
                    f" constraint {version_range}"
                )

        return CompatibilityResult(
            is_compatible=len(issues) == 0,
            skill_id=skill.id,
            version=skill.version,
            issues=issues,
            warnings=warnings,
            missing_dependencies=missing_deps,
            version_conflicts=version_conflicts,
        )

    def detect_conflicts(
        self,
        skills: List[AgentSkill],
    ) -> List[Tuple[str, str, str]]:
        """
        Detect conflicts between skills.

        Args:
            skills: List of skills to check

        Returns:
            List of (skill1_id, skill2_id, conflict_description)
        """
        conflicts: List[Tuple[str, str, str]] = []

        # Check all pairs
        for i, skill_a in enumerate(skills):
            for skill_b in skills[i + 1 :]:
                # Check if they target the same agent
                if skill_a.target_agent == skill_b.target_agent:
                    # Check for incompatible skill types
                    if not self._are_types_compatible(skill_a.skill_type, skill_b.skill_type):
                        conflicts.append(
                            (
                                f"{skill_a.id} v{skill_a.version}",
                                f"{skill_b.id} v{skill_b.version}",
                                f"Incompatible types: {skill_a.skill_type} vs {skill_b.skill_type}",
                            )
                        )

                    # Check for config conflicts
                    config_conflicts = self._check_config_conflicts(skill_a.config, skill_b.config)
                    if config_conflicts:
                        conflicts.append(
                            (
                                f"{skill_a.id} v{skill_a.version}",
                                f"{skill_b.id} v{skill_b.version}",
                                f"Config conflicts: {', '.join(config_conflicts)}",
                            )
                        )

        return conflicts

    def validate_dependency_tree(
        self,
        skill: AgentSkill,
        available_skills: Optional[Dict[str, AgentSkill]] = None,
    ) -> Tuple[bool, List[str]]:
        """
        Validate entire dependency tree for a skill.

        Args:
            skill: Root skill to validate
            available_skills: Available skills

        Returns:
            (is_valid, error_messages)
        """
        skills_to_check = available_skills or self.available_skills
        errors: List[str] = []
        visited: Set[str] = set()

        def validate_recursive(current_skill: AgentSkill, path: List[str]) -> None:
            skill_key = f"{current_skill.id}:{current_skill.version}"

            # Check for circular dependency
            if skill_key in path:
                errors.append(f"Circular dependency: {' -> '.join(path + [skill_key])}")
                return

            # Skip if already validated
            if skill_key in visited:
                return

            visited.add(skill_key)

            # Check dependencies
            for dep_dict in current_skill.dependencies:
                dep_id = dep_dict.get("skill_id")

                if dep_id not in skills_to_check:
                    if not dep_dict.get("optional", False):
                        errors.append(f"Missing dependency: {dep_id}")
                    continue

                dep_skill = skills_to_check[dep_id]
                validate_recursive(dep_skill, path + [skill_key])

        validate_recursive(skill, [])

        return len(errors) == 0, errors

    def get_compatibility_matrix(
        self,
        skills: List[AgentSkill],
        agents: List[str],
    ) -> Dict[str, Dict[str, bool]]:
        """
        Build compatibility matrix for skills and agents.

        Args:
            skills: List of skills
            agents: List of agent names

        Returns:
            {skill_id: {agent_name: is_compatible}}
        """
        matrix: Dict[str, Dict[str, bool]] = {}

        for skill in skills:
            matrix[skill.id] = {}
            for agent in agents:
                result = self.check_compatibility(skill, agent)
                matrix[skill.id][agent] = result.is_compatible

        return matrix

    # Helper methods

    @staticmethod
    def _are_types_compatible(type_a: str, type_b: str) -> bool:
        """Check if two skill types are compatible."""
        # Define incompatible type pairs
        incompatible_pairs = [
            ("behavior_parameter", "workflow"),  # Example: can't have both
        ]

        pair = tuple(sorted([type_a, type_b]))
        return pair not in incompatible_pairs

    @staticmethod
    def _check_config_conflicts(
        config_a: Dict[str, Any],
        config_b: Dict[str, Any],
    ) -> List[str]:
        """Check for conflicting configuration keys."""
        conflicts: List[str] = []

        # Find common keys with different values
        common_keys = set(config_a.keys()) & set(config_b.keys())

        for key in common_keys:
            if config_a[key] != config_b[key]:
                conflicts.append(f"{key}: {config_a[key]} vs {config_b[key]}")

        return conflicts
