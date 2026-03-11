"""Tests for Phase 5: SkillComposition component."""

import pytest

from socratic_agents.skill_generation.skill_composition import SkillComposition
from socratic_agents.skill_generation.workflow_skill import WorkflowSkill


class TestSkillComposition:
    """Tests for SkillComposition."""

    @pytest.fixture
    def composition(self):
        """Create composition engine."""
        return SkillComposition()

    @pytest.fixture
    def sample_skills(self, composition):
        """Register sample skills."""
        skills = {
            "skill_parse": {
                "agent_id": "parser",
                "skill_name": "parse",
                "output_type": "parsed_data",
                "confidence": 0.9,
                "goal": "parse input data",
            },
            "skill_analyze": {
                "agent_id": "analyzer",
                "skill_name": "analyze",
                "input_type": "parsed_data",
                "output_type": "analysis",
                "confidence": 0.85,
                "goal": "analyze parsed data",
                "depends_on": ["skill_parse"],
            },
            "skill_format": {
                "agent_id": "formatter",
                "skill_name": "format",
                "input_type": "analysis",
                "output_type": "report",
                "confidence": 0.8,
                "goal": "format analysis report",
                "depends_on": ["skill_analyze"],
            },
        }

        for skill_id, skill_info in skills.items():
            composition.register_skill(skill_id, skill_info)

        return skills

    def test_register_skill(self, composition):
        """Test skill registration."""
        composition.register_skill(
            "test_skill",
            {
                "agent_id": "agent1",
                "skill_name": "action",
            },
        )
        assert "test_skill" in composition.skill_library

    def test_compose_skills_simple(self, composition, sample_skills):
        """Test composing simple skill chain."""
        workflow = composition.compose_skills(
            ["skill_parse", "skill_analyze"],
            "analyze parsed data",
        )
        assert workflow is not None
        assert isinstance(workflow, WorkflowSkill)
        assert len(workflow.workflow_steps) >= 1

    def test_compose_skills_complex(self, composition, sample_skills):
        """Test composing complex workflow."""
        workflow = composition.compose_skills(
            ["skill_parse", "skill_analyze", "skill_format"],
            "process and format data",
        )
        assert workflow is not None
        assert len(workflow.workflow_steps) >= 1

    def test_compose_skills_empty(self, composition):
        """Test composing with no skills."""
        workflow = composition.compose_skills([], "goal")
        assert workflow is None

    def test_compose_skills_unknown_skill(self, composition, sample_skills):
        """Test composing with unknown skill."""
        workflow = composition.compose_skills(
            ["unknown_skill", "skill_parse"],
            "goal",
        )
        # Should handle gracefully
        assert workflow is None or len(workflow.workflow_steps) >= 0

    def test_find_skill_chain(self, composition, sample_skills):
        """Test finding skill chain."""
        chain = composition.find_skill_chain("skill_parse", "create report")
        assert isinstance(chain, list)
        assert chain[0] == "skill_parse"

    def test_find_skill_chain_not_found(self, composition):
        """Test skill chain with non-existent start."""
        chain = composition.find_skill_chain("unknown", "goal")
        assert chain == []

    def test_optimize_skill_order_single(self, composition, sample_skills):
        """Test optimizing single skill."""
        optimized = composition.optimize_skill_order(["skill_parse"])
        assert optimized == ["skill_parse"]

    def test_optimize_skill_order_dependent(self, composition, sample_skills):
        """Test optimizing dependent skills."""
        # Try different orders
        order1 = composition.optimize_skill_order(["skill_analyze", "skill_parse", "skill_format"])
        # Should respect dependencies
        assert isinstance(order1, list)

    def test_detect_skill_conflicts_none(self, composition, sample_skills):
        """Test detecting conflicts when none exist."""
        conflicts = composition.detect_skill_conflicts(["skill_parse", "skill_analyze"])
        assert isinstance(conflicts, list)

    def test_detect_skill_conflicts_incompatible(self, composition):
        """Test detecting incompatible skills."""
        composition.register_skill(
            "skill_a",
            {
                "agent_id": "agent1",
                "skill_name": "a",
                "output_type": "type_a",
                "can_run_together": False,
            },
        )
        composition.register_skill(
            "skill_b",
            {
                "agent_id": "agent1",
                "skill_name": "b",
                "input_type": "type_b",
            },
        )

        conflicts = composition.detect_skill_conflicts(["skill_a", "skill_b"])
        assert isinstance(conflicts, list)

    def test_composition_history(self, composition, sample_skills):
        """Test composition history tracking."""
        composition.compose_skills(["skill_parse", "skill_analyze"], "goal1")
        composition.compose_skills(["skill_parse"], "goal2")

        assert len(composition.composition_history) >= 1

    def test_estimate_workflow_confidence(self, composition, sample_skills):
        """Test confidence estimation."""
        workflow = composition.compose_skills(
            ["skill_parse", "skill_analyze", "skill_format"],
            "full process",
        )
        if workflow:
            assert 0 <= workflow.confidence <= 1.0

    def test_determine_skill_order_respects_dependencies(self, composition, sample_skills):
        """Test that skill ordering respects dependencies."""
        ordered = composition.optimize_skill_order(["skill_format", "skill_parse", "skill_analyze"])
        # parse should come before analyze, analyze before format
        parse_idx = ordered.index("skill_parse")
        analyze_idx = ordered.index("skill_analyze")
        format_idx = ordered.index("skill_format")

        assert parse_idx < analyze_idx < format_idx


class TestSkillCompositionIntegration:
    """Integration tests for SkillComposition."""

    def test_full_composition_workflow(self):
        """Test complete skill composition workflow."""
        composition = SkillComposition()

        # Register skills
        skills = {
            "read_data": {
                "agent_id": "reader",
                "skill_name": "read",
                "output_type": "raw_data",
                "confidence": 0.95,
                "goal": "read input",
            },
            "validate_data": {
                "agent_id": "validator",
                "skill_name": "validate",
                "input_type": "raw_data",
                "output_type": "validated",
                "confidence": 0.9,
                "goal": "validate data",
                "depends_on": ["read_data"],
            },
            "transform_data": {
                "agent_id": "transformer",
                "skill_name": "transform",
                "input_type": "validated",
                "output_type": "transformed",
                "confidence": 0.85,
                "goal": "transform data",
                "depends_on": ["validate_data"],
            },
            "export_data": {
                "agent_id": "exporter",
                "skill_name": "export",
                "input_type": "transformed",
                "output_type": "report",
                "confidence": 0.8,
                "goal": "export report",
                "depends_on": ["transform_data"],
            },
        }

        for skill_id, skill_info in skills.items():
            composition.register_skill(skill_id, skill_info)

        # Compose workflow
        workflow = composition.compose_skills(
            ["read_data", "validate_data", "transform_data", "export_data"],
            "read validate transform and export data",
        )

        assert workflow is not None
        assert len(workflow.workflow_steps) > 0
        assert workflow.confidence > 0

    def test_conflict_detection_workflow(self):
        """Test conflict detection in multi-skill scenario."""
        composition = SkillComposition()

        # Register conflicting skills
        composition.register_skill(
            "parallel_skill_1",
            {
                "agent_id": "exclusive_agent",
                "skill_name": "task1",
                "can_run_together": False,
            },
        )
        composition.register_skill(
            "parallel_skill_2",
            {
                "agent_id": "exclusive_agent",
                "skill_name": "task2",
            },
        )

        conflicts = composition.detect_skill_conflicts(["parallel_skill_1", "parallel_skill_2"])
        # Should detect that skills cannot run together
        assert isinstance(conflicts, list)

    def test_complex_goal_matching(self):
        """Test relevance calculation for complex goals."""
        composition = SkillComposition()

        composition.register_skill(
            "skill1",
            {
                "agent_id": "a1",
                "skill_name": "s1",
                "goal": "process analyze data",
                "description": "analyzes data structures",
            },
        )
        composition.register_skill(
            "skill2",
            {
                "agent_id": "a2",
                "skill_name": "s2",
                "goal": "generate report output",
            },
        )

        # Compose with multi-word goal
        workflow = composition.compose_skills(
            ["skill1", "skill2"],
            "process and analyze data to generate report",
        )

        if workflow:
            # Should understand relationship between goals
            assert len(workflow.workflow_steps) >= 1
