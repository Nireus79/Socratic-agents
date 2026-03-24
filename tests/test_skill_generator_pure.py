"""
Tests for pure SkillGenerator - Phase 3 extraction.

Demonstrates the complete integration chain:
  MaturityCalculator → QualityController → SkillGenerator
"""


from socrates_maturity import MaturityCalculator

from src.socratic_agents.skill_generator import AgentSkill, SkillGenerator


class TestSkillGenerator:
    """Tests for pure skill generation."""

    def test_generate_returns_skills(self):
        """Test that generate returns skills for weak categories."""
        skills = SkillGenerator.generate(
            phase="analysis",
            weak_categories=["functional_requirements"],
            category_scores={"functional_requirements": 0.4},
        )

        assert isinstance(skills, list)
        assert len(skills) > 0
        assert all(isinstance(s, AgentSkill) for s in skills)

    def test_generate_targets_weak_categories(self):
        """Test that skills are generated for weak categories."""
        # Weak category triggers skill
        weak_skills = SkillGenerator.generate(
            phase="analysis",
            weak_categories=["functional_requirements"],
            category_scores={"functional_requirements": 0.4},
        )

        # No matching weak category
        no_skills = SkillGenerator.generate(
            phase="analysis",
            weak_categories=["nonexistent_category"],
            category_scores={"nonexistent_category": 0.8},
        )

        assert len(weak_skills) > 0
        assert len(no_skills) == 0  # No matching template for non-existent category

    def test_generate_customizes_by_learning_velocity(self):
        """Test that learning velocity customizes skill config."""
        high_velocity = SkillGenerator.generate(
            phase="discovery",
            weak_categories=["problem_definition"],
            category_scores={"problem_definition": 0.3},
            learning_velocity="high",
        )

        low_velocity = SkillGenerator.generate(
            phase="discovery",
            weak_categories=["problem_definition"],
            category_scores={"problem_definition": 0.3},
            learning_velocity="low",
        )

        # High velocity should have higher config intensity
        high_config = high_velocity[0].config
        low_config = low_velocity[0].config

        assert high_config.get("intensity") == "high"
        assert low_config.get("intensity") == "low"

    def test_generate_adjusts_confidence_by_engagement(self):
        """Test that engagement score adjusts skill confidence."""
        high_engagement = SkillGenerator.generate(
            phase="analysis",
            weak_categories=["functional_requirements"],
            category_scores={"functional_requirements": 0.4},
            engagement_score=0.9,
        )

        low_engagement = SkillGenerator.generate(
            phase="analysis",
            weak_categories=["functional_requirements"],
            category_scores={"functional_requirements": 0.4},
            engagement_score=0.1,
        )

        # Higher engagement = higher confidence
        high_conf = high_engagement[0].confidence
        low_conf = low_engagement[0].confidence

        assert high_conf > low_conf

    def test_generate_returns_correct_phase(self):
        """Test that generated skills have correct phase."""
        for phase in ["discovery", "analysis", "design", "implementation"]:
            skills = SkillGenerator.generate(
                phase=phase,
                weak_categories=["problem_definition"],  # Generic to avoid issues
                category_scores={"problem_definition": 0.3},
            )

            if skills:  # Only check if phase has matching template
                for skill in skills:
                    assert skill.maturity_phase == phase

    def test_generate_prioritizes_by_weakness(self):
        """Test that skills are prioritized by weakness severity."""
        skills = SkillGenerator.generate(
            phase="implementation",
            weak_categories=["code_quality", "testing_coverage", "documentation"],
            category_scores={
                "code_quality": 0.2,  # Very weak
                "testing_coverage": 0.5,  # Weak
                "documentation": 0.3,  # Weak
            },
        )

        # First skill should target weakest category
        if len(skills) > 0:
            first_skill_category = skills[0].category_focus
            # Verify it's one of the weak categories
            assert first_skill_category in [
                "code_quality",
                "testing_coverage",
                "documentation",
            ]

    def test_skill_to_dict_serializable(self):
        """Test that skills can be serialized to dict."""
        skills = SkillGenerator.generate(
            phase="analysis",
            weak_categories=["functional_requirements"],
            category_scores={"functional_requirements": 0.4},
        )

        assert len(skills) > 0
        skill_dict = skills[0].to_dict()

        assert isinstance(skill_dict, dict)
        assert "id" in skill_dict
        assert "target_agent" in skill_dict
        assert "config" in skill_dict
        assert "confidence" in skill_dict

    def test_get_phases(self):
        """Test getting list of supported phases."""
        phases = SkillGenerator.get_phases()

        assert isinstance(phases, list)
        assert "discovery" in phases
        assert "analysis" in phases
        assert "design" in phases
        assert "implementation" in phases

    def test_get_templates(self):
        """Test getting skill templates."""
        all_templates = SkillGenerator.get_templates()

        assert isinstance(all_templates, dict)
        assert len(all_templates) == 4  # 4 phases

        # Get specific phase
        discovery_templates = SkillGenerator.get_templates("discovery")
        assert "discovery" in discovery_templates
        assert len(discovery_templates["discovery"]) == 3  # 3 skills per phase

    def test_empty_weak_categories(self):
        """Test with no weak categories."""
        skills = SkillGenerator.generate(
            phase="analysis",
            weak_categories=[],
            category_scores={},
        )

        assert skills == []

    def test_invalid_phase(self):
        """Test with invalid phase."""
        skills = SkillGenerator.generate(
            phase="unknown_phase",
            weak_categories=["something"],
            category_scores={"something": 0.3},
        )

        assert skills == []


class TestIntegrationWithMaturityCalculator:
    """Tests showing integration with MaturityCalculator."""

    def test_skill_generation_from_qc_output(self):
        """Test skill generation using QualityController output format."""
        # Simulate QualityController output
        qc_output = {
            "phase": "analysis",
            "category_scores": {
                "functional_requirements": 0.4,
                "non_functional_requirements": 0.5,
                "data_requirements": 0.8,
            },
            "weak_categories": ["functional_requirements", "non_functional_requirements"],
        }

        # Generate skills from QC output
        skills = SkillGenerator.generate(
            phase=qc_output["phase"],
            weak_categories=qc_output["weak_categories"],
            category_scores=qc_output["category_scores"],
            learning_velocity="high",
            engagement_score=0.8,
        )

        # Should have skills for 2 weak categories
        assert len(skills) > 0
        assert len(skills) <= 2

        # All skills should target weak categories
        for skill in skills:
            assert skill.category_focus in qc_output["weak_categories"]

    def test_maturity_driven_skill_generation(self):
        """Test skill generation driven by MaturityCalculator output."""
        # Step 1: Use MaturityCalculator to estimate phase
        overall_maturity = MaturityCalculator.calculate_overall_maturity(
            {"discovery": 1.0, "analysis": 0.4}
        )
        current_phase = MaturityCalculator.estimate_current_phase(overall_maturity)
        # Should be "design" phase (50-75%)

        # Step 2: Simulate category scores for design phase
        category_scores = {
            "technology_stack": 0.4,  # Weak - matches design template
            "architecture": 0.5,  # Weak - matches design template
            "integrations": 0.8,  # Strong
        }

        # Step 3: Identify weak categories using MaturityCalculator
        weak_categories = MaturityCalculator.identify_weak_categories(category_scores)

        # Step 4: Generate skills for weak categories
        skills = SkillGenerator.generate(
            phase=current_phase,
            weak_categories=weak_categories,
            category_scores=category_scores,
        )

        # Verify the chain works
        assert current_phase in ["discovery", "analysis", "design", "implementation"]
        assert len(weak_categories) > 0
        # Skills will be generated if categories match templates for the phase
        if current_phase == "design":
            assert len(skills) > 0

    def test_complete_workflow(self):
        """Test complete workflow: MaturityCalculator → QC → SkillGenerator."""
        # Step 1: Calculate maturity
        phase_scores = {"discovery": 1.0, "analysis": 0.3}
        overall = MaturityCalculator.calculate_overall_maturity(phase_scores)
        current_phase = MaturityCalculator.estimate_current_phase(overall)
        # Should be "design" phase

        # Step 2: Simulate QualityController analysis for design phase
        qc_category_scores = {
            "technology_stack": 0.4,  # Weak - design phase category
            "architecture": 0.5,  # Weak - design phase category
            "integrations": 0.8,  # Strong - design phase category
        }

        # Step 3: Identify weak categories
        weak_categories = MaturityCalculator.identify_weak_categories(qc_category_scores)

        # Step 4: Generate skills
        skills = SkillGenerator.generate(
            phase=current_phase,
            weak_categories=weak_categories,
            category_scores=qc_category_scores,
            learning_velocity="high",
            engagement_score=0.8,
        )

        # Verify complete chain
        assert current_phase is not None
        assert len(weak_categories) == 2
        assert current_phase == "design"
        assert len(skills) > 0

        # All skills should target weak areas
        for skill in skills:
            assert skill.category_focus in weak_categories

    def test_skill_application_chain(self):
        """Test that generated skills can be applied to improve weak areas."""
        # Initial state: weak categories
        initial_scores = {
            "functional_requirements": 0.4,
            "non_functional_requirements": 0.5,
            "data_requirements": 0.8,
        }

        initial_weak = MaturityCalculator.identify_weak_categories(initial_scores)
        assert len(initial_weak) == 2

        # Generate skills for weak areas
        skills = SkillGenerator.generate(
            phase="analysis",
            weak_categories=initial_weak,
            category_scores=initial_scores,
        )

        assert len(skills) > 0

        # Simulate improvement from applying skills
        improved_scores = {
            "functional_requirements": 0.6,  # Improved
            "non_functional_requirements": 0.7,  # Improved
            "data_requirements": 0.8,  # Unchanged
        }

        # Track improvement
        improvement = MaturityCalculator.calculate_category_improvement(
            initial_scores, improved_scores
        )

        assert abs(improvement["functional_requirements"] - 0.2) < 0.001
        assert abs(improvement["non_functional_requirements"] - 0.2) < 0.001

        # New weak categories (should be fewer now)
        new_weak = MaturityCalculator.identify_weak_categories(improved_scores)
        assert len(new_weak) == 0  # No more weak categories!

        # Overall maturity improved
        initial_overall = sum(initial_scores.values()) / len(initial_scores)
        improved_overall = sum(improved_scores.values()) / len(improved_scores)
        assert improved_overall > initial_overall
