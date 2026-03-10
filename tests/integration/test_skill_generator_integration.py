"""Integration tests for SkillGeneratorAgent - testing skill generation and application flow."""

import pytest
from socratic_agents import SkillGeneratorAgent


class TestSkillGenerationAndApplicationFlow:
    """Test complete workflow of generating, applying, and evaluating skills."""

    def test_full_skill_workflow_discovery_phase(self):
        """
        Test complete skill workflow for discovery phase:
        1. Generate skills for weak categories
        2. Verify skills are created with correct targets
        3. Evaluate their effectiveness
        4. Verify learning feedback is recorded
        """
        agent = SkillGeneratorAgent()

        # Step 1: Generate skills based on discovery phase weakness
        maturity_data = {
            "current_phase": "discovery",
            "completion_percent": 35,
            "weak_categories": ["problem_definition", "scope"],
            "category_scores": {
                "problem_definition": 0.2,  # Very weak
                "scope": 0.5,  # Moderately weak
                "target_audience": 0.9,  # Strong
            },
        }

        learning_data = {"learning_velocity": "medium", "engagement_score": 0.8}

        gen_result = agent.process(
            {"action": "generate", "maturity_data": maturity_data, "learning_data": learning_data}
        )

        # Step 1 Verification
        assert gen_result["status"] == "success"
        assert gen_result["phase"] == "discovery"
        assert gen_result["completion_percent"] == 35
        assert gen_result["skills_generated"] == 2  # Two weak categories

        # Step 2: Verify skill properties
        skills = gen_result["skills"]
        problem_def_skill = next(s for s in skills if s["category_focus"] == "problem_definition")
        scope_skill = next(s for s in skills if s["category_focus"] == "scope")

        assert problem_def_skill["target_agent"] == "SocraticCounselor"
        assert scope_skill["target_agent"] == "SocraticCounselor"

        # Verify priority: problem_definition should be higher priority
        recs = gen_result["recommendations"]
        problem_def_rec = next(
            r for r in recs if r["skill"]["category_focus"] == "problem_definition"
        )
        scope_rec = next(r for r in recs if r["skill"]["category_focus"] == "scope")

        assert problem_def_rec["priority"] == "high"
        assert scope_rec["priority"] in ["high", "medium"]

        # Step 3: Simulate applying skills and evaluate effectiveness
        # Skill 1: Problem Definition Focus - very effective
        eval_result_1 = agent.process(
            {
                "action": "evaluate",
                "skill_id": problem_def_skill["id"],
                "feedback": "helped",
                "effectiveness_score": 0.9,
            }
        )

        assert eval_result_1["status"] == "success"
        assert eval_result_1["effectiveness_score"] == 0.9

        # Skill 2: Scope Refinement - moderately effective
        eval_result_2 = agent.process(
            {
                "action": "evaluate",
                "skill_id": scope_skill["id"],
                "feedback": "helped",
                "effectiveness_score": 0.65,
            }
        )

        assert eval_result_2["status"] == "success"
        assert eval_result_2["effectiveness_score"] == 0.65

        # Step 4: List skills and verify feedback was recorded
        list_result = agent.process({"action": "list", "phase": "discovery"})

        assert list_result["skills_count"] == 2
        updated_skills = list_result["skills"]

        updated_problem_def = next(s for s in updated_skills if s["id"] == problem_def_skill["id"])
        updated_scope = next(s for s in updated_skills if s["id"] == scope_skill["id"])

        assert updated_problem_def["feedback"] == "helped"
        assert updated_problem_def["effectiveness_score"] == 0.9
        assert updated_scope["feedback"] == "helped"
        assert updated_scope["effectiveness_score"] == 0.65

    def test_full_skill_workflow_analysis_phase(self):
        """
        Test skill generation and evaluation for analysis phase.
        """
        agent = SkillGeneratorAgent()

        # Generate skills for analysis phase
        gen_result = agent.process(
            {
                "action": "generate",
                "maturity_data": {
                    "current_phase": "analysis",
                    "completion_percent": 50,
                    "weak_categories": [
                        "functional_requirements",
                        "non_functional_requirements",
                        "data_requirements",
                    ],
                    "category_scores": {
                        "functional_requirements": 0.3,
                        "non_functional_requirements": 0.2,
                        "data_requirements": 0.4,
                    },
                },
                "learning_data": {"learning_velocity": "high", "engagement_score": 0.9},
            }
        )

        assert gen_result["status"] == "success"
        assert gen_result["skills_generated"] == 3
        assert all(s["target_agent"] == "CodeGenerator" for s in gen_result["skills"])

        # Verify recommendations are ordered by priority
        recs = gen_result["recommendations"]
        priorities = [r["priority"] for r in recs]

        # Should have high priority first
        if len(priorities) > 0:
            assert priorities[0] == "high"

        # Evaluate all skills
        for skill in gen_result["skills"]:
            eval_result = agent.process(
                {
                    "action": "evaluate",
                    "skill_id": skill["id"],
                    "feedback": "helped",
                    "effectiveness_score": 0.8,
                }
            )
            assert eval_result["status"] == "success"

    def test_multiple_phase_skill_generation(self):
        """
        Test generating skills across multiple phases in sequence.
        """
        agent = SkillGeneratorAgent()

        # Phase 1: Discovery
        discovery_result = agent.process(
            {
                "action": "generate",
                "maturity_data": {
                    "current_phase": "discovery",
                    "completion_percent": 100,
                    "weak_categories": ["problem_definition"],
                    "category_scores": {"problem_definition": 0.5},
                },
                "learning_data": {"learning_velocity": "medium", "engagement_score": 0.6},
            }
        )

        discovery_skill_id = discovery_result["skills"][0]["id"]

        # Phase 2: Analysis
        analysis_result = agent.process(
            {
                "action": "generate",
                "maturity_data": {
                    "current_phase": "analysis",
                    "completion_percent": 50,
                    "weak_categories": ["functional_requirements"],
                    "category_scores": {"functional_requirements": 0.4},
                },
                "learning_data": {"learning_velocity": "medium", "engagement_score": 0.7},
            }
        )

        analysis_skill_id = analysis_result["skills"][0]["id"]

        # Phase 3: Design
        design_result = agent.process(
            {
                "action": "generate",
                "maturity_data": {
                    "current_phase": "design",
                    "completion_percent": 50,
                    "weak_categories": ["architecture"],
                    "category_scores": {"architecture": 0.3},
                },
                "learning_data": {"learning_velocity": "high", "engagement_score": 0.85},
            }
        )

        design_skill_id = design_result["skills"][0]["id"]

        # Verify all skills are generated in the system
        all_skills_result = agent.process({"action": "list"})
        assert all_skills_result["skills_count"] == 3

        # Verify each phase has correct skills
        discovery_list = agent.process({"action": "list", "phase": "discovery"})
        assert discovery_list["skills_count"] == 1

        analysis_list = agent.process({"action": "list", "phase": "analysis"})
        assert analysis_list["skills_count"] == 1

        design_list = agent.process({"action": "list", "phase": "design"})
        assert design_list["skills_count"] == 1

    def test_skill_effectiveness_tracking_across_evaluations(self):
        """
        Test that skill effectiveness is tracked and updated correctly
        across multiple evaluations.
        """
        agent = SkillGeneratorAgent()

        # Generate a skill
        gen_result = agent.process(
            {
                "action": "generate",
                "maturity_data": {
                    "current_phase": "discovery",
                    "completion_percent": 35,
                    "weak_categories": ["problem_definition"],
                    "category_scores": {"problem_definition": 0.3},
                },
                "learning_data": {"learning_velocity": "medium", "engagement_score": 0.75},
            }
        )

        skill_id = gen_result["skills"][0]["id"]

        # Initial evaluation
        eval1 = agent.process(
            {
                "action": "evaluate",
                "skill_id": skill_id,
                "feedback": "helped",
                "effectiveness_score": 0.7,
            }
        )
        assert eval1["effectiveness_score"] == 0.7

        # Check effectiveness is tracked
        assert skill_id in agent.skill_effectiveness
        assert agent.skill_effectiveness[skill_id] == 0.7

        # Update evaluation
        eval2 = agent.process(
            {
                "action": "evaluate",
                "skill_id": skill_id,
                "feedback": "no effect",
                "effectiveness_score": 0.4,
            }
        )
        assert eval2["effectiveness_score"] == 0.4

        # Verify tracking is updated
        assert agent.skill_effectiveness[skill_id] == 0.4

    def test_engagement_based_skill_customization(self):
        """
        Test that skills are customized based on engagement level.
        High engagement should boost confidence.
        """
        agent = SkillGeneratorAgent()

        # Low engagement
        low_engagement_result = agent.process(
            {
                "action": "generate",
                "maturity_data": {
                    "current_phase": "discovery",
                    "completion_percent": 35,
                    "weak_categories": ["problem_definition"],
                    "category_scores": {"problem_definition": 0.3},
                },
                "learning_data": {"learning_velocity": "medium", "engagement_score": 0.2},
            }
        )

        low_confidence = low_engagement_result["skills"][0]["confidence"]

        # High engagement
        high_engagement_result = agent.process(
            {
                "action": "generate",
                "maturity_data": {
                    "current_phase": "discovery",
                    "completion_percent": 35,
                    "weak_categories": ["problem_definition"],
                    "category_scores": {"problem_definition": 0.3},
                },
                "learning_data": {"learning_velocity": "medium", "engagement_score": 0.9},
            }
        )

        high_confidence = high_engagement_result["skills"][0]["confidence"]

        # High engagement should result in higher confidence
        assert high_confidence > low_confidence

    def test_design_phase_multiple_target_agents(self):
        """
        Test that design phase skills target different agents appropriately.
        """
        agent = SkillGeneratorAgent()

        gen_result = agent.process(
            {
                "action": "generate",
                "maturity_data": {
                    "current_phase": "design",
                    "completion_percent": 60,
                    "weak_categories": ["technology_stack", "architecture", "integrations"],
                    "category_scores": {
                        "technology_stack": 0.3,
                        "architecture": 0.2,
                        "integrations": 0.4,
                    },
                },
                "learning_data": {"learning_velocity": "medium", "engagement_score": 0.7},
            }
        )

        # Verify we have 3 skills
        assert gen_result["skills_generated"] == 3

        # Verify targets
        target_agents = [s["target_agent"] for s in gen_result["skills"]]
        assert "CodeGenerator" in target_agents
        assert "QualityController" in target_agents

    def test_implementation_phase_complete_flow(self):
        """
        Test complete workflow for implementation phase with all 3 skills.
        """
        agent = SkillGeneratorAgent()

        gen_result = agent.process(
            {
                "action": "generate",
                "maturity_data": {
                    "current_phase": "implementation",
                    "completion_percent": 85,
                    "weak_categories": ["code_quality", "testing_coverage", "documentation"],
                    "category_scores": {
                        "code_quality": 0.4,
                        "testing_coverage": 0.3,
                        "documentation": 0.5,
                    },
                },
                "learning_data": {"learning_velocity": "medium", "engagement_score": 0.75},
            }
        )

        assert gen_result["skills_generated"] == 3

        # Verify target agents match expectations
        target_agents = set(s["target_agent"] for s in gen_result["skills"])
        assert "QualityController" in target_agents
        assert "CodeValidator" in target_agents
        assert "DocumentProcessor" in target_agents

        # Evaluate each skill
        for skill in gen_result["skills"]:
            result = agent.process(
                {
                    "action": "evaluate",
                    "skill_id": skill["id"],
                    "feedback": "helped",
                    "effectiveness_score": 0.75,
                }
            )
            assert result["status"] == "success"

        # List and verify all are present
        final_list = agent.process({"action": "list", "phase": "implementation"})
        assert final_list["skills_count"] == 3

    def test_skill_generation_with_no_learning_data(self):
        """
        Test that skill generation works gracefully when learning_data is missing.
        """
        agent = SkillGeneratorAgent()

        gen_result = agent.process(
            {
                "action": "generate",
                "maturity_data": {
                    "current_phase": "discovery",
                    "completion_percent": 35,
                    "weak_categories": ["problem_definition"],
                    "category_scores": {"problem_definition": 0.3},
                },
                # learning_data omitted
            }
        )

        assert gen_result["status"] == "success"
        assert gen_result["skills_generated"] == 1
        # Should use default values for engagement and velocity

    def test_recommendation_reasons_are_descriptive(self):
        """
        Test that skill recommendations include descriptive reasoning.
        """
        agent = SkillGeneratorAgent()

        gen_result = agent.process(
            {
                "action": "generate",
                "maturity_data": {
                    "current_phase": "discovery",
                    "completion_percent": 35,
                    "weak_categories": ["problem_definition"],
                    "category_scores": {"problem_definition": 0.25},
                },
                "learning_data": {"learning_velocity": "medium", "engagement_score": 0.75},
            }
        )

        rec = gen_result["recommendations"][0]
        assert "reason" in rec
        assert "Addresses weak category" in rec["reason"]
        assert "problem_definition" in rec["reason"]
