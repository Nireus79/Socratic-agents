"""
Phase 6: Skill Versioning & Compatibility Management Examples

This module demonstrates how to use the skill versioning system, including:
- Creating and versioning skills
- Refining skills to create new versions
- Managing skill dependencies
- Checking skill-agent compatibility
- Handling deprecation workflows
- Upgrading skills to newer versions
"""

from socratic_agents.agents.skill_generator_agent_v2 import SkillGeneratorAgentV2
from socratic_agents.integrations.skill_orchestrator import SkillOrchestrator
from socratic_agents.models.skill_models import AgentSkill
from socratic_agents.skill_generation.compatibility_checker import CompatibilityChecker
from socratic_agents.skill_generation.skill_version_manager import SkillVersionManager


def example_basic_version_management():
    """Example 1: Basic skill versioning workflow."""
    print("\n=== Example 1: Basic Skill Versioning ===\n")

    # Create a version manager
    version_manager = SkillVersionManager()

    # Create and register a skill version 1.0.0
    skill_v1 = AgentSkill(
        id="discovery_skill",
        target_agent="socratic_counselor",
        skill_type="behavior_parameter",
        config={"focus": "problem_definition", "approach": "guided_questions"},
        confidence=0.8,
        maturity_phase="discovery",
        version="1.0.0",
    )

    version_manager.register_version(
        skill_v1, changelog="Initial version of discovery skill", created_by="system"
    )

    print("Registered skill version 1.0.0")
    print(f"Latest version: {version_manager.get_latest_version('discovery_skill')}")

    # Create and register version 1.1.0 (minor enhancement)
    skill_v11 = AgentSkill(
        id="discovery_skill",
        target_agent="socratic_counselor",
        skill_type="behavior_parameter",
        config={"focus": "problem_definition", "approach": "guided_questions", "depth": "deep"},
        confidence=0.85,
        maturity_phase="discovery",
        version="1.1.0",
        parent_skill_id="discovery_skill",
        parent_version="1.0.0",
    )

    version_manager.register_version(
        skill_v11,
        changelog="Added depth parameter for more nuanced questioning",
        created_by="skill_generator",
    )

    print("Registered skill version 1.1.0")
    print(f"Latest version: {version_manager.get_latest_version('discovery_skill')}")

    # List all versions
    versions = version_manager.list_versions("discovery_skill")
    print(f"All versions: {versions}")

    # Upgrade to latest
    upgraded = version_manager.upgrade_skill("discovery_skill", "1.0.0", "1.1.0")
    print(f"Upgraded to version {upgraded.version} with config: {upgraded.config}")


def example_skill_refinement_with_versioning():
    """Example 2: Refining skills with automatic versioning."""
    print("\n=== Example 2: Skill Refinement with Versioning ===\n")

    # Create a skill generator with versioning support
    agent = SkillGeneratorAgentV2(enable_llm_generation=False)

    # Generate a skill
    result = agent.process(
        {
            "action": "generate",
            "maturity_data": {
                "current_phase": "discovery",
                "completion_percent": 50,
                "weak_categories": ["problem_definition"],
            },
            "learning_data": {"code_length": 100, "issue_count": 5},
        }
    )

    if result["status"] == "success":
        skill_id = result["skills"][0]["id"]
        original_version = result["skills"][0]["version"]
        print(f"Generated skill {skill_id} with version {original_version}")

        # Note: Refinement requires LLM client for full functionality
        # In production, you would provide an actual LLM client
        print("To refine this skill, you would call:")
        print(
            f"  agent.process({{'action': 'refine', 'skill_id': '{skill_id}', 'feedback': 'Improve clarity'}})"
        )
        print("This would create version 1.0.1 with parent references preserved")


def example_dependency_management():
    """Example 3: Managing skill dependencies."""
    print("\n=== Example 3: Dependency Management ===\n")

    checker = CompatibilityChecker()

    # Create a base skill (foundation)
    base_skill = AgentSkill(
        id="base_understanding",
        target_agent="socratic_counselor",
        skill_type="behavior_parameter",
        config={"level": "fundamental"},
        confidence=0.9,
        maturity_phase="discovery",
        version="1.0.0",
    )

    # Create a dependent skill (builds on base)
    dependent_skill = AgentSkill(
        id="advanced_questioning",
        target_agent="socratic_counselor",
        skill_type="behavior_parameter",
        config={"complexity": "high"},
        confidence=0.85,
        maturity_phase="discovery",
        version="1.0.0",
        dependencies=[
            {
                "skill_id": "base_understanding",
                "min_version": "1.0.0",
                "max_version": "2.0.0",
            }
        ],
    )

    # Register the base skill
    checker.register_available_skill(base_skill)

    # Check if dependencies are satisfied
    result = checker.check_dependencies(dependent_skill)

    print(f"Dependency satisfied: {result.is_compatible}")
    print(f"Missing dependencies: {result.missing_dependencies}")
    print(f"Version conflicts: {result.version_conflicts}")


def example_compatibility_checking():
    """Example 4: Checking skill-agent compatibility."""
    print("\n=== Example 4: Skill-Agent Compatibility ===\n")

    checker = CompatibilityChecker()

    # Register agent capabilities
    checker.register_agent_capability("socratic_counselor", "behavior_parameter", "1.0")
    checker.register_agent_capability("socratic_counselor", "method", "1.0")
    checker.register_agent_capability("code_generator", "method", "1.0")

    # Create a skill
    skill = AgentSkill(
        id="questioning_skill",
        target_agent="socratic_counselor",
        skill_type="behavior_parameter",
        config={"style": "open_ended"},
        confidence=0.9,
        maturity_phase="discovery",
        version="1.0.0",
    )

    # Check compatibility with different agents
    result_counselor = checker.check_compatibility(skill, "socratic_counselor")
    result_generator = checker.check_compatibility(skill, "code_generator")

    print(f"Compatible with socratic_counselor: {result_counselor.is_compatible}")
    print(f"Warnings: {result_counselor.warnings}")

    print(f"\nCompatible with code_generator: {result_generator.is_compatible}")
    print(f"Issues: {result_generator.issues}")

    # Generate compatibility matrix
    matrix = checker.get_compatibility_matrix([skill], ["socratic_counselor", "code_generator"])
    print(f"\nCompatibility matrix: {matrix}")


def example_deprecation_workflow():
    """Example 5: Handling deprecation and migration."""
    print("\n=== Example 5: Deprecation & Migration ===\n")

    version_manager = SkillVersionManager()

    # Create v1.0.0
    skill_v1 = AgentSkill(
        id="old_approach",
        target_agent="socratic_counselor",
        skill_type="behavior_parameter",
        config={"method": "old"},
        confidence=0.7,
        maturity_phase="discovery",
        version="1.0.0",
    )

    version_manager.register_version(skill_v1, created_by="system")
    print("Registered version 1.0.0")

    # Create improved v2.0.0
    skill_v2 = AgentSkill(
        id="old_approach",
        target_agent="socratic_counselor",
        skill_type="behavior_parameter",
        config={"method": "new", "efficiency": "improved"},
        confidence=0.95,
        maturity_phase="discovery",
        version="2.0.0",
        parent_skill_id="old_approach",
        parent_version="1.0.0",
    )

    version_manager.register_version(skill_v2, created_by="system")
    print("Registered version 2.0.0")

    # Deprecate v1.0.0
    version_manager.deprecate_version(
        "old_approach",
        "1.0.0",
        reason="Replaced by more efficient version",
        replacement_version="2.0.0",
    )
    print("Deprecated version 1.0.0")

    # Check that latest skips deprecated
    latest = version_manager.get_latest_version("old_approach")
    print(f"Latest (non-deprecated) version: {latest}")

    # List all versions
    all_versions = version_manager.list_versions("old_approach", include_deprecated=True)
    print(f"All versions (including deprecated): {all_versions}")


def example_conflict_detection():
    """Example 6: Detecting conflicting skills."""
    print("\n=== Example 6: Conflict Detection ===\n")

    checker = CompatibilityChecker()

    # Create two skills with conflicting configs
    skill1 = AgentSkill(
        id="skill_1",
        target_agent="agent1",
        skill_type="behavior_parameter",
        config={"mode": "strict", "timeout": 30},
        confidence=0.9,
        maturity_phase="discovery",
        version="1.0.0",
    )

    skill2 = AgentSkill(
        id="skill_2",
        target_agent="agent1",
        skill_type="behavior_parameter",
        config={"mode": "lenient", "timeout": 60},
        confidence=0.9,
        maturity_phase="discovery",
        version="1.0.0",
    )

    # Detect conflicts
    conflicts = checker.detect_conflicts([skill1, skill2])

    print(f"Number of conflicts detected: {len(conflicts)}")
    for conflict in conflicts:
        skill_a, skill_b, description = conflict
        print(f"  Conflict: {skill_a} vs {skill_b}")
        print(f"  Reason: {description}")


def example_orchestrator_with_versioning():
    """Example 7: Using orchestrator with version management."""
    print("\n=== Example 7: Orchestrator with Version Management ===\n")

    # Create orchestrator with version management
    orchestrator = SkillOrchestrator()

    # Create a properly formatted skill dict
    skill_dict = {
        "id": "orchestrator_skill",
        "target_agent": "socratic_counselor",
        "skill_type": "behavior_parameter",
        "config": {"focus": "clarity"},
        "confidence": 0.88,
        "maturity_phase": "discovery",
        "version": "1.0.0",
    }

    # Apply skill with compatibility checking
    result = orchestrator.apply_and_track_skill(
        "orchestrator_skill", skill_dict, feedback="Initial application"
    )

    print(f"Application result: {result['status']}")
    if result["status"] == "success":
        print(f"Skill version: {result.get('version', 'N/A')}")
        print(f"Compatibility warnings: {result.get('compatibility_warnings', [])}")

        # Record effectiveness
        orchestrator.record_effectiveness_feedback("orchestrator_skill", 0.92)
        print("Recorded effectiveness feedback: 0.92")


def example_circular_dependency_detection():
    """Example 8: Detecting circular dependencies."""
    print("\n=== Example 8: Circular Dependency Detection ===\n")

    checker = CompatibilityChecker()

    # Create skill A that depends on B
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

    # Create skill B that depends on A (circular!)
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

    # Validate dependency tree
    is_valid, errors = checker.validate_dependency_tree(skill_a)

    print(f"Dependency tree valid: {is_valid}")
    print(f"Errors: {errors}")


def example_version_comparison():
    """Example 9: Semantic version comparison."""
    print("\n=== Example 9: Semantic Version Comparison ===\n")

    version_manager = SkillVersionManager()

    # Compare versions
    result_1_0_to_1_1 = version_manager.compare_versions("1.0.0", "1.1.0")
    result_1_1_to_2_0 = version_manager.compare_versions("1.1.0", "2.0.0")
    result_same = version_manager.compare_versions("1.0.0", "1.0.0")

    print(f"1.0.0 vs 1.1.0: {result_1_0_to_1_1} (negative = older, positive = newer)")
    print(f"1.1.0 vs 2.0.0: {result_1_1_to_2_0}")
    print(f"1.0.0 vs 1.0.0: {result_same}")


def example_version_history_queries():
    """Example 10: Querying version history."""
    print("\n=== Example 10: Version History Queries ===\n")

    version_manager = SkillVersionManager()

    # Create multiple skill versions
    for i in range(1, 4):
        skill = AgentSkill(
            id="history_skill",
            target_agent="agent",
            skill_type="type",
            config={"iteration": i},
            confidence=0.8 + (i * 0.05),
            maturity_phase="discovery",
            version=f"1.{i}.0",
        )
        version_manager.register_version(
            skill, changelog=f"Iteration {i} improvements", created_by="system"
        )

    # Get all history
    history = version_manager.get_version_history()
    print(f"Total history entries: {len(history)}")

    # Get skill-specific history
    skill_history = version_manager.get_version_history("history_skill")
    print(f"Entries for history_skill: {len(skill_history)}")

    # Get stats
    stats = version_manager.get_stats()
    print("Version manager stats:")
    print(f"  Total unique skills: {stats.get('total_unique_skills', 0)}")
    print(f"  Total versions: {stats.get('total_versions', 0)}")
    print(f"  Deprecated versions: {stats.get('deprecated_versions', 0)}")


if __name__ == "__main__":
    print("=" * 60)
    print("Phase 6: Skill Versioning & Compatibility Management Examples")
    print("=" * 60)

    example_basic_version_management()
    example_skill_refinement_with_versioning()
    example_dependency_management()
    example_compatibility_checking()
    example_deprecation_workflow()
    example_conflict_detection()
    example_orchestrator_with_versioning()
    example_circular_dependency_detection()
    example_version_comparison()
    example_version_history_queries()

    print("\n" + "=" * 60)
    print("All examples completed successfully!")
    print("=" * 60)
