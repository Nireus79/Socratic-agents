"""Unit tests for Skill Interaction Tracker."""

import pytest

from socratic_agents.analytics import SkillInteractionTracker


class TestSkillInteractionTracker:
    """Test SkillInteractionTracker functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tracker = SkillInteractionTracker()

    def test_record_interaction(self):
        """Test recording a skill interaction."""
        self.tracker.record_skill_interaction(["skill_a", "skill_b"], 0.85)
        history = self.tracker.get_interaction_history()

        assert len(history) == 1
        assert history[0]["skill_ids"] == ["skill_a", "skill_b"]
        assert history[0]["effectiveness"] == 0.85

    def test_record_interaction_validation(self):
        """Test validation of record_skill_interaction parameters."""
        with pytest.raises(ValueError, match="skill_ids cannot be empty"):
            self.tracker.record_skill_interaction([], 0.5)

        with pytest.raises(ValueError, match="At least 2 skills required"):
            self.tracker.record_skill_interaction(["skill_a"], 0.5)

        with pytest.raises(ValueError, match="effectiveness must be between"):
            self.tracker.record_skill_interaction(["skill_a", "skill_b"], 1.5)

    def test_interaction_matrix_calculation(self):
        """Test calculation of interaction matrix."""
        self.tracker.record_skill_interaction(["skill_a", "skill_b"], 0.8)
        self.tracker.record_skill_interaction(["skill_a", "skill_b"], 0.6)

        matrix = self.tracker.get_interaction_matrix()

        assert "skill_a" in matrix
        assert "skill_b" in matrix
        assert matrix["skill_a"]["skill_b"] == 0.7
        assert matrix["skill_b"]["skill_a"] == 0.7

    def test_synergy_detection(self):
        """Test identifying skill synergies."""
        self.tracker.record_skill_interaction(["skill_a", "skill_b"], 0.85)
        self.tracker.record_skill_interaction(["skill_a", "skill_b"], 0.75)
        self.tracker.record_skill_interaction(["skill_c", "skill_d"], 0.3)

        synergies = self.tracker.identify_skill_synergies(threshold=0.7)

        assert len(synergies) == 1
        assert synergies[0][0:2] == ("skill_a", "skill_b")
        assert synergies[0][2] == 0.8

    def test_conflict_detection(self):
        """Test identifying skill conflicts."""
        self.tracker.record_skill_interaction(["skill_x", "skill_y"], 0.2)
        self.tracker.record_skill_interaction(["skill_x", "skill_y"], 0.1)
        self.tracker.record_skill_interaction(["skill_z", "skill_w"], 0.9)

        conflicts = self.tracker.identify_skill_conflicts(threshold=0.3)

        assert len(conflicts) == 1
        assert conflicts[0][0:2] == ("skill_x", "skill_y")
        assert pytest.approx(conflicts[0][2]) == 0.15

    def test_best_combination(self):
        """Test finding the best skill combination."""
        self.tracker.record_skill_interaction(["skill_a", "skill_b"], 0.7)
        self.tracker.record_skill_interaction(["skill_c", "skill_d", "skill_e"], 0.9)
        self.tracker.record_skill_interaction(["skill_f", "skill_g"], 0.6)

        best = self.tracker.get_best_skill_combination()

        assert best == ["skill_c", "skill_d", "skill_e"]

    def test_interaction_strength(self):
        """Test getting interaction strength between two skills."""
        self.tracker.record_skill_interaction(["skill_a", "skill_b"], 0.8)
        self.tracker.record_skill_interaction(["skill_a", "skill_b"], 0.6)

        strength = self.tracker.get_interaction_strength("skill_a", "skill_b")

        assert strength == 0.7

    def test_get_statistics(self):
        """Test getting statistics about interactions."""
        assert self.tracker.get_statistics()["total_interactions"] == 0

        self.tracker.record_skill_interaction(["skill_a", "skill_b"], 0.8)
        self.tracker.record_skill_interaction(["skill_a", "skill_b"], 0.6)
        self.tracker.record_skill_interaction(["skill_c", "skill_d"], 0.5)

        stats = self.tracker.get_statistics()

        assert stats["total_interactions"] == 3
        assert stats["unique_skills"] == 4
        assert stats["unique_skill_pairs"] == 2
        assert stats["min_effectiveness"] == 0.5
        assert stats["max_effectiveness"] == 0.8

    def test_multiple_skills_interaction(self):
        """Test recording interactions with more than 2 skills."""
        self.tracker.record_skill_interaction(["skill_a", "skill_b", "skill_c"], 0.9)

        matrix = self.tracker.get_interaction_matrix()

        assert matrix["skill_a"]["skill_b"] == 0.9
        assert matrix["skill_a"]["skill_c"] == 0.9
        assert matrix["skill_b"]["skill_c"] == 0.9
