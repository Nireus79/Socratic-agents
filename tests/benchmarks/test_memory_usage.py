"""Memory usage benchmarks."""

import tracemalloc

import pytest

from socratic_agents import (
    QualityController,
    SkillGeneratorAgent,
    SocraticCounselor,
)


class TestMemoryFootprint:
    """Test memory usage of agents."""

    @pytest.mark.memory
    def test_single_agent_memory(self):
        """Measure memory footprint of single agent."""
        tracemalloc.start()

        agent = SocraticCounselor()
        result = agent.process({"action": "guide", "topic": "memory"})

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Should use less than 10MB for single agent
        assert peak < 10 * 1024 * 1024
        assert result is not None

    @pytest.mark.memory
    def test_multiple_agents_memory(self):
        """Measure memory usage with multiple agents."""
        tracemalloc.start()

        agents = [SocraticCounselor() for _ in range(10)]

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # 10 agents should use less than 50MB
        assert peak < 50 * 1024 * 1024
        assert len(agents) == 10

    @pytest.mark.memory
    def test_skill_generation_memory(self, sample_maturity_data):
        """Measure memory usage during skill generation."""
        tracemalloc.start()

        agent = SkillGeneratorAgent()
        result = agent.process({"action": "generate", "maturity_data": sample_maturity_data})

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Skill generation should use less than 15MB
        assert peak < 15 * 1024 * 1024
        assert "skills" in result

    @pytest.mark.memory
    def test_quality_controller_memory(self, sample_code_medium):
        """Measure memory usage of QualityController."""
        tracemalloc.start()

        controller = QualityController()
        result = controller.process({"action": "detect_weak_areas", "code": sample_code_medium})

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Quality controller should use less than 8MB
        assert peak < 8 * 1024 * 1024
        assert "status" in result
