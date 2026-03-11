"""Tests for SkillPromptEngine component."""

import pytest
from socratic_agents.skill_generation.skill_prompt_engine import SkillPromptEngine


class TestSkillPromptEngine:
    """Tests for SkillPromptEngine."""

    @pytest.fixture
    def engine(self):
        """Create a prompt engine."""
        return SkillPromptEngine()

    def test_engine_initialization(self):
        """Test engine initialization."""
        engine = SkillPromptEngine()
        assert engine is not None

    def test_build_generation_prompt_basic(self, engine):
        """Test building a basic generation prompt."""
        context = {
            "maturity_phase": "discovery",
            "completion_percent": 25,
            "problem_definition_score": 10,
        }
        prompt = engine.build_generation_prompt(context, "problem_definition")

        assert "problem_definition" in prompt
        assert "discovery" in prompt
        assert "25" in prompt
        assert "JSON" in prompt

    def test_build_generation_prompt_with_all_context(self, engine):
        """Test generation prompt with complete context."""
        context = {
            "maturity_phase": "execution",
            "completion_percent": 60,
            "scope_definition_score": 45,
            "resource_planning_score": 50,
        }
        prompt = engine.build_generation_prompt(context, "scope_definition")

        assert "execution" in prompt
        assert "scope_definition" in prompt
        assert "JSON" in prompt
        assert len(prompt) > 100

    def test_build_generation_prompt_minimal_context(self, engine):
        """Test generation prompt with minimal context."""
        prompt = engine.build_generation_prompt({}, "test_area")
        assert "test_area" in prompt
        assert "JSON" in prompt

    def test_build_refinement_prompt(self, engine):
        """Test building a refinement prompt."""
        prompt = engine.build_refinement_prompt("skill_test_1", "The skill was helpful")

        assert "skill_test_1" in prompt
        assert "helpful" in prompt
        assert "JSON" in prompt
        assert "refine" in prompt.lower() or "improv" in prompt.lower()

    def test_build_refinement_prompt_negative_feedback(self, engine):
        """Test refinement prompt with negative feedback."""
        feedback = "The skill did not help with the problem"
        prompt = engine.build_refinement_prompt("skill_x", feedback)

        assert "skill_x" in prompt
        assert "did not help" in prompt
        assert "JSON" in prompt

    def test_build_evaluation_prompt(self, engine):
        """Test building an evaluation prompt."""
        results = {
            "effectiveness_before": 30,
            "effectiveness_after": 75,
        }
        prompt = engine.build_evaluation_prompt("skill_eval_1", results)

        assert "skill_eval_1" in prompt
        assert "30" in prompt
        assert "75" in prompt
        assert "+45" in prompt
        assert "JSON" in prompt

    def test_build_evaluation_prompt_no_improvement(self, engine):
        """Test evaluation prompt with no improvement."""
        results = {
            "effectiveness_before": 50,
            "effectiveness_after": 50,
        }
        prompt = engine.build_evaluation_prompt("skill_no_change", results)

        assert "skill_no_change" in prompt
        assert "0.0" in prompt
        assert "JSON" in prompt

    def test_build_evaluation_prompt_negative_change(self, engine):
        """Test evaluation prompt with negative change."""
        results = {
            "effectiveness_before": 80,
            "effectiveness_after": 40,
        }
        prompt = engine.build_evaluation_prompt("skill_degraded", results)

        assert "skill_degraded" in prompt
        assert "-40" in prompt
        assert "JSON" in prompt

    def test_build_compatibility_prompt(self, engine):
        """Test building a compatibility prompt."""
        prompt = engine.build_compatibility_prompt("skill_a", "skill_b")

        assert "skill_a" in prompt
        assert "skill_b" in prompt
        assert "compatible" in prompt.lower()
        assert "JSON" in prompt

    def test_build_compatibility_prompt_same_skill(self, engine):
        """Test compatibility prompt with same skill ID."""
        prompt = engine.build_compatibility_prompt("skill_same", "skill_same")

        assert "skill_same" in prompt
        assert "JSON" in prompt

    def test_all_prompts_are_non_empty(self, engine):
        """Test that all generated prompts are non-empty."""
        context = {"maturity_phase": "discovery", "completion_percent": 25}

        p1 = engine.build_generation_prompt(context, "area")
        p2 = engine.build_refinement_prompt("skill_1", "feedback")
        p3 = engine.build_evaluation_prompt(
            "skill_2", {"effectiveness_before": 50, "effectiveness_after": 75}
        )
        p4 = engine.build_compatibility_prompt("s1", "s2")

        assert len(p1) > 0
        assert len(p2) > 0
        assert len(p3) > 0
        assert len(p4) > 0

    def test_all_prompts_contain_json_instruction(self, engine):
        """Test that all prompts instruct JSON response."""
        context = {"maturity_phase": "discovery"}

        prompts = [
            engine.build_generation_prompt(context, "area"),
            engine.build_refinement_prompt("skill", "feedback"),
            engine.build_evaluation_prompt(
                "skill", {"effectiveness_before": 50, "effectiveness_after": 75}
            ),
            engine.build_compatibility_prompt("s1", "s2"),
        ]

        for prompt in prompts:
            assert "JSON" in prompt


class TestSkillPromptEngineIntegration:
    """Integration tests for SkillPromptEngine."""

    def test_prompt_sequence_workflow(self):
        """Test a complete prompt workflow."""
        engine = SkillPromptEngine()

        # Step 1: Generate prompt
        context = {"maturity_phase": "discovery", "completion_percent": 20}
        gen_prompt = engine.build_generation_prompt(context, "problem_definition")
        assert len(gen_prompt) > 100

        # Step 2: Refine prompt (after skill is created)
        ref_prompt = engine.build_refinement_prompt("skill_pd_1", "helpful feedback")
        assert len(ref_prompt) > 50

        # Step 3: Evaluate prompt
        eval_prompt = engine.build_evaluation_prompt(
            "skill_pd_1", {"effectiveness_before": 20, "effectiveness_after": 60}
        )
        assert len(eval_prompt) > 50

        # Step 4: Check compatibility
        compat_prompt = engine.build_compatibility_prompt("skill_pd_1", "skill_rd_1")
        assert len(compat_prompt) > 50

    def test_multiple_context_variations(self):
        """Test prompts with various context values."""
        engine = SkillPromptEngine()

        phases = ["discovery", "definition", "execution", "optimization"]
        areas = ["problem_definition", "scope_definition", "resource_planning", "quality_metrics"]

        for phase in phases:
            for area in areas:
                context = {"maturity_phase": phase, "completion_percent": 30}
                prompt = engine.build_generation_prompt(context, area)
                assert phase in prompt
                assert area in prompt
