"""Integration tests for AgentConflictDetector with socratic-conflict library."""

from unittest.mock import Mock

import pytest

from src.socratic_agents.agents.conflict_detector import AgentConflictDetector


class TestConflictDetectorInitialization:
    """Test AgentConflictDetector initialization."""

    def test_create_detector_minimal(self):
        """Test creating detector with minimal parameters."""
        detector = AgentConflictDetector()
        assert detector is not None
        assert detector.name == "AgentConflictDetector"
        assert detector.conflicts == []

    def test_create_detector_with_llm(self):
        """Test creating detector with LLM client."""
        mock_llm = Mock()
        detector = AgentConflictDetector(llm_client=mock_llm)
        assert detector.llm_client == mock_llm


class TestSimpleConflictDetection:
    """Test simple conflict detection (when socratic-conflict unavailable)."""

    def test_detect_duplicate_items(self):
        """Test detecting duplicate items."""
        detector = AgentConflictDetector()

        result = detector.detect_conflicts(["item1", "item2", "item1"])

        assert result["status"] == "success"
        assert result["conflicts_found"] == 1  # One duplicate pair
        assert len(result["conflicts"]) == 1

    def test_detect_no_conflicts(self):
        """Test when no conflicts exist."""
        detector = AgentConflictDetector()

        result = detector.detect_conflicts(["item1", "item2", "item3"])

        assert result["status"] == "success"
        assert result["conflicts_found"] == 0
        assert result["conflicts"] == []

    def test_empty_items_list(self):
        """Test with empty items list."""
        detector = AgentConflictDetector()

        result = detector.detect_conflicts([])

        assert result["status"] == "error"
        assert "required" in result["message"].lower()


class TestConflictListing:
    """Test listing detected conflicts."""

    def test_list_conflicts_empty(self):
        """Test listing when no conflicts exist."""
        detector = AgentConflictDetector()

        result = detector.list_conflicts()

        assert result["status"] == "success"
        assert result["conflicts_count"] == 0
        assert result["conflicts"] == []

    def test_list_conflicts_after_detection(self):
        """Test listing after detecting conflicts."""
        detector = AgentConflictDetector()

        # Detect some conflicts
        detector.detect_conflicts(["a", "b", "a"])

        # List them
        result = detector.list_conflicts()

        assert result["status"] == "success"
        assert result["conflicts_count"] > 0
        assert len(result["conflicts"]) > 0


class TestConflictClearance:
    """Test clearing conflict history."""

    def test_clear_conflicts(self):
        """Test clearing conflict history."""
        detector = AgentConflictDetector()

        # Add some conflicts
        detector.detect_conflicts(["a", "b", "a"])
        assert len(detector.conflicts) > 0

        # Clear them
        result = detector.clear_conflicts()

        assert result["status"] == "success"
        assert result["cleared_count"] > 0
        assert len(detector.conflicts) == 0

    def test_clear_empty_conflicts(self):
        """Test clearing when no conflicts exist."""
        detector = AgentConflictDetector()

        result = detector.clear_conflicts()

        assert result["status"] == "success"
        assert result["cleared_count"] == 0


class TestConflictResolution:
    """Test conflict resolution."""

    def test_resolve_nonexistent_conflict(self):
        """Test resolving a conflict that doesn't exist."""
        detector = AgentConflictDetector()

        result = detector.resolve_conflict("nonexistent_id")

        assert result["status"] == "error"
        assert "not found" in result["message"].lower()

    def test_resolve_detected_conflict(self):
        """Test resolving a detected conflict."""
        detector = AgentConflictDetector()

        # Detect conflicts
        detect_result = detector.detect_conflicts(["a", "b", "a"])
        conflicts = detect_result["conflicts"]

        if conflicts:
            conflict_id = conflicts[0]["id"]
            result = detector.resolve_conflict(conflict_id)

            assert result["status"] == "success"
            assert result["resolved"] is True
            assert result["conflict_id"] == conflict_id


class TestProcessMethod:
    """Test the main process method."""

    def test_process_detect_with_items(self):
        """Test process method with detect action and items."""
        detector = AgentConflictDetector()

        result = detector.process(
            {
                "action": "detect",
                "items": ["a", "b", "a"],
            }
        )

        assert result["status"] == "success"
        assert "conflicts" in result

    def test_process_list(self):
        """Test process method with list action."""
        detector = AgentConflictDetector()

        result = detector.process({"action": "list"})

        assert result["status"] == "success"
        assert "conflicts_count" in result

    def test_process_clear(self):
        """Test process method with clear action."""
        detector = AgentConflictDetector()

        # Add conflicts
        detector.detect_conflicts(["a", "b", "a"])

        result = detector.process({"action": "clear"})

        assert result["status"] == "success"
        assert result["cleared_count"] > 0

    def test_process_missing_params(self):
        """Test process method with missing required parameters."""
        detector = AgentConflictDetector()

        result = detector.process(
            {
                "action": "detect",
                # Missing items or agent_states
            }
        )

        assert result["status"] == "error"

    def test_process_unknown_action(self):
        """Test process method with unknown action."""
        detector = AgentConflictDetector()

        result = detector.process({"action": "unknown_action"})

        assert result["status"] == "error"
        assert "Unknown action" in result["message"]


class TestFullDetectionMode:
    """Test full detection mode when socratic-conflict is available."""

    def test_detect_from_agent_states(self):
        """Test detecting from agent states."""
        detector = AgentConflictDetector()

        if detector.use_full_detection:
            agent_states = {
                "agent1": {"goal": "maximize profit"},
                "agent2": {"goal": "minimize cost"},
            }

            result = detector.detect_from_agent_states(agent_states)

            assert result["status"] == "success"
            assert "conflicts" in result
            assert "agent_count" in result

    def test_fallback_when_library_unavailable(self):
        """Test fallback behavior when library unavailable."""
        detector = AgentConflictDetector()

        # If library unavailable, detect_from_agent_states should return error
        if not detector.use_full_detection:
            result = detector.detect_from_agent_states({"agent1": {}})
            assert result["status"] == "error"
            assert "not available" in result["message"].lower()


class TestConflictTracking:
    """Test conflict tracking and persistence."""

    def test_conflicts_tracked_in_history(self):
        """Test that conflicts are tracked in detector history."""
        detector = AgentConflictDetector()

        # Detect conflicts
        detector.detect_conflicts(["x", "y", "x"])

        # Verify they're in history
        assert len(detector.conflicts) > 0

        # Verify they can be listed
        result = detector.list_conflicts()
        assert result["conflicts_count"] == len(detector.conflicts)

    def test_multiple_detections_accumulated(self):
        """Test that multiple detections accumulate."""
        detector = AgentConflictDetector()

        # First detection
        detector.detect_conflicts(["a", "a"])
        count1 = len(detector.conflicts)

        # Second detection
        detector.detect_conflicts(["b", "b"])
        count2 = len(detector.conflicts)

        # Should accumulate
        assert count2 > count1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
