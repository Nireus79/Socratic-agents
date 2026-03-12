"""Benchmarks for skill generation agent."""

import pytest
from socratic_agents import SkillGeneratorAgent


class TestSkillGenerationBenchmarks:
    """Benchmark skill generation performance."""

    @pytest.mark.benchmark
    def test_skill_generation_discovery_phase(self, benchmark, sample_maturity_data):
        """Benchmark skill generation for discovery phase."""
        agent = SkillGeneratorAgent()

        result = benchmark(
            agent.process,
            {
                "action": "generate",
                "maturity_data": {
                    **sample_maturity_data,
                    "current_phase": "discovery",
                    "completion_percent": 25
                }
            }
        )

        assert result["status"] == "success"
        assert len(result.get("skills", [])) > 0

    @pytest.mark.benchmark
    def test_skill_generation_design_phase(self, benchmark, sample_maturity_data):
        """Benchmark skill generation for design phase."""
        agent = SkillGeneratorAgent()

        result = benchmark(
            agent.process,
            {
                "action": "generate",
                "maturity_data": {
                    **sample_maturity_data,
                    "current_phase": "design",
                    "completion_percent": 50
                }
            }
        )

        assert result["status"] == "success"
        assert len(result.get("skills", [])) > 0

    @pytest.mark.benchmark
    def test_skill_generation_implementation_phase(self, benchmark, sample_maturity_data):
        """Benchmark skill generation for implementation phase."""
        agent = SkillGeneratorAgent()

        result = benchmark(
            agent.process,
            {
                "action": "generate",
                "maturity_data": {
                    **sample_maturity_data,
                    "current_phase": "implementation",
                    "completion_percent": 75
                }
            }
        )

        assert result["status"] == "success"
        assert len(result.get("skills", [])) > 0

    @pytest.mark.benchmark
    def test_skill_generation_many_weak_areas(self, benchmark, sample_maturity_data):
        """Benchmark skill generation with many weak categories."""
        agent = SkillGeneratorAgent()

        # Create maturity data with many weak areas
        complex_data = {
            **sample_maturity_data,
            "weak_categories": [
                "problem_definition",
                "scope",
                "architecture",
                "testing",
                "documentation",
                "performance",
                "security",
                "accessibility",
            ],
            "category_scores": {
                "problem_definition": 0.2,
                "scope": 0.3,
                "architecture": 0.4,
                "testing": 0.3,
                "documentation": 0.2,
                "performance": 0.5,
                "security": 0.4,
                "accessibility": 0.3,
            }
        }

        result = benchmark(
            agent.process,
            {
                "action": "generate",
                "maturity_data": complex_data
            }
        )

        assert result["status"] == "success"
        assert len(result.get("skills", [])) >= 5  # Should generate multiple skills

    @pytest.mark.benchmark
    def test_skill_generation_high_completion(self, benchmark, sample_maturity_data):
        """Benchmark skill generation with high completion percentage."""
        agent = SkillGeneratorAgent()

        result = benchmark(
            agent.process,
            {
                "action": "generate",
                "maturity_data": {
                    **sample_maturity_data,
                    "completion_percent": 95,
                    "weak_categories": []
                }
            }
        )

        assert result["status"] == "success"

    @pytest.mark.benchmark(group="skill-comparison")
    def test_skill_generation_vs_retrieval(self, benchmark, sample_maturity_data):
        """Compare skill generation vs retrieval performance."""
        agent = SkillGeneratorAgent()

        def generate_and_retrieve():
            # Generate skills
            result = agent.process({
                "action": "generate",
                "maturity_data": sample_maturity_data
            })
            # Retrieve skills
            agent.process({
                "action": "retrieve",
                "maturity_data": sample_maturity_data
            })
            return result

        result = benchmark(generate_and_retrieve)
        assert result["status"] == "success"
