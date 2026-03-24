"""
Tests for QualityController integration with MaturityCalculator.

Demonstrates how Phase 1 (socrates-maturity) enables Phase 2 (QualityController).
"""

from socrates_maturity import MaturityCalculator

from src.socratic_agents.agents.quality_controller import QualityController


class TestQualityControllerIntegration:
    """Tests for QualityController using MaturityCalculator."""

    def setup_method(self):
        """Set up test fixtures."""
        self.qc = QualityController()

    def test_detect_weak_areas_returns_correct_structure(self):
        """Test that detect_weak_areas returns the expected structure."""
        code = "def hello(): pass"

        result = self.qc.detect_weak_areas(code)

        assert result["status"] == "success"
        assert "phase" in result
        assert "category_scores" in result
        assert "weak_categories" in result
        assert "completion_percent" in result

    def test_phase_estimation_uses_maturity_calculator(self):
        """Test that phase estimation is consistent with MaturityCalculator."""
        # Create code with low quality
        weak_code = "x=1"

        result = self.qc.detect_weak_areas(weak_code)
        estimated_phase = result["phase"]

        # Calculate using MaturityCalculator directly
        avg_score = sum(result["category_scores"].values()) / len(result["category_scores"])
        calculator_phase = MaturityCalculator.estimate_current_phase(avg_score)

        # Should match
        assert estimated_phase == calculator_phase

    def test_weak_categories_identified_correctly(self):
        """Test that weak categories are identified (score < 0.6)."""
        poor_code = "x=1"  # Very minimal code

        result = self.qc.detect_weak_areas(poor_code)

        # All low-scoring categories should be in weak_categories
        category_scores = result["category_scores"]
        weak_categories = result["weak_categories"]

        # Manually identify weak categories (< 0.6)
        expected_weak = [cat for cat, score in category_scores.items() if score < 0.6]

        assert set(weak_categories) == set(expected_weak)

    def test_high_quality_code_has_few_weak_areas(self):
        """Test that well-written code has fewer weak categories."""
        good_code = '''
def calculate_sum(numbers):
    """Calculate the sum of a list of numbers.

    Args:
        numbers: List of numbers to sum

    Returns:
        The sum of all numbers
    """
    total = 0
    for num in numbers:
        assert isinstance(num, (int, float)), "All items must be numeric"
        total += num
    return total


def test_calculate_sum():
    """Test calculate_sum function."""
    assert calculate_sum([1, 2, 3]) == 6
    assert calculate_sum([]) == 0
    assert calculate_sum([1.5, 2.5]) == 4.0
'''

        result = self.qc.detect_weak_areas(good_code)

        weak_categories = result["weak_categories"]

        # High-quality code should have fewer (or no) weak categories
        assert len(weak_categories) <= 2  # At most 2 weak areas in good code

    def test_skill_application(self):
        """Test that skills can be applied to focus on weak areas."""
        poor_code = "x = 1"

        # First detection
        result = self.qc.detect_weak_areas(poor_code)
        weak_areas = result["weak_categories"]

        # Create mock skill targeting a weak area
        if weak_areas:
            skill = {
                "id": f"improve_{weak_areas[0]}",
                "category_focus": weak_areas[0],
                "config": {"intensity": "high", "depth": "comprehensive"},
            }

            apply_result = self.qc.apply_skills([skill])

            assert apply_result["status"] == "success"
            assert apply_result["skills_applied"] == 1
            assert apply_result["focus_area"] == weak_areas[0]

    def test_process_action_routing(self):
        """Test that process() correctly routes to detect_weak_areas."""
        code = "def test(): pass"

        request = {"action": "detect_weak_areas", "code": code}

        result = self.qc.process(request)

        assert result["status"] == "success"
        assert "phase" in result
        assert "weak_categories" in result

    def test_quality_workflow(self):
        """
        Test complete quality control workflow.

        This demonstrates the integration between:
        1. QualityController analyzing code
        2. MaturityCalculator estimating phase
        3. Weak categories identified for improvement
        """
        # Step 1: Analyze code with QualityController
        code = """
def process_data(data):
    result = []
    for item in data:
        # TODO: Add validation
        result.append(item * 2)
    return result
"""

        detection = self.qc.detect_weak_areas(code)

        # Step 2: Extract information
        phase = detection["phase"]
        weak_categories = detection["weak_categories"]
        category_scores = detection["category_scores"]

        # Step 3: Verify integration with MaturityCalculator
        avg_score = sum(category_scores.values()) / len(category_scores)

        # MaturityCalculator should agree on phase
        calc_phase = MaturityCalculator.estimate_current_phase(avg_score)
        assert phase == calc_phase

        # MaturityCalculator should identify same weak categories
        calc_weak = MaturityCalculator.identify_weak_categories(category_scores)
        assert set(weak_categories) == set(calc_weak)

        # Step 4: Create skills for weak areas (simulated)
        if weak_categories:
            # In real system, SkillGenerator would create these
            # For now, simulate skill creation
            skills = []
            for weak_cat in weak_categories:
                skills.append(
                    {
                        "id": f"fix_{weak_cat}",
                        "category_focus": weak_cat,
                        "config": {"priority": "high"},
                    }
                )

            # Step 5: Apply skills
            if skills:
                apply_result = self.qc.apply_skills(skills)
                assert apply_result["status"] == "success"
                assert apply_result["skills_applied"] == len(skills)
