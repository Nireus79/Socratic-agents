"""Performance benchmarks for core agents."""

import pytest
from socratic_agents import (
    SocraticCounselor,
    CodeGenerator,
    CodeValidator,
    QualityController,
    SkillGeneratorAgent,
)


class TestAgentInitializationPerformance:
    """Benchmark agent initialization time."""

    @pytest.mark.benchmark
    def test_counselor_initialization(self, benchmark):
        """Benchmark SocraticCounselor initialization."""
        result = benchmark(SocraticCounselor)
        assert result is not None

    @pytest.mark.benchmark
    def test_skill_generator_initialization(self, benchmark):
        """Benchmark SkillGeneratorAgent initialization."""
        result = benchmark(SkillGeneratorAgent)
        assert result is not None

    @pytest.mark.benchmark
    def test_quality_controller_initialization(self, benchmark):
        """Benchmark QualityController initialization."""
        result = benchmark(QualityController)
        assert result is not None


class TestAgentProcessingPerformance:
    """Benchmark agent processing time."""

    @pytest.mark.benchmark
    def test_counselor_guide_performance(self, benchmark):
        """Benchmark SocraticCounselor.guide() speed."""
        counselor = SocraticCounselor()

        result = benchmark(
            counselor.process, {"action": "guide", "topic": "Python", "level": "beginner"}
        )

        assert result["status"] == "success"

    @pytest.mark.benchmark
    def test_code_generator_performance(self, benchmark):
        """Benchmark CodeGenerator.process() speed."""
        generator = CodeGenerator()

        result = benchmark(
            generator.process, {"prompt": "Create a sorting function", "language": "python"}
        )

        assert "code" in result

    @pytest.mark.benchmark
    def test_code_validator_performance(self, benchmark, sample_code_medium):
        """Benchmark CodeValidator.process() speed."""
        validator = CodeValidator()

        result = benchmark(validator.process, {"code": sample_code_medium, "language": "python"})

        assert "valid" in result

    @pytest.mark.benchmark
    def test_quality_controller_performance(self, benchmark, sample_code_medium):
        """Benchmark QualityController weak area detection."""
        controller = QualityController()

        result = benchmark(
            controller.process, {"action": "detect_weak_areas", "code": sample_code_medium}
        )

        assert "status" in result
        assert result["status"] == "success"

    @pytest.mark.benchmark
    def test_skill_generation_performance(
        self, benchmark, sample_maturity_data, sample_learning_data
    ):
        """Benchmark SkillGeneratorAgent.process() speed."""
        agent = SkillGeneratorAgent()

        result = benchmark(
            agent.process,
            {
                "action": "generate",
                "maturity_data": sample_maturity_data,
                "learning_data": sample_learning_data,
            },
        )

        assert result["status"] == "success"
        assert "skills" in result


class TestScalabilityBenchmarks:
    """Test agent performance under load."""

    @pytest.mark.benchmark
    def test_large_code_validation(self, benchmark, sample_code_large):
        """Test validation performance with large code."""
        validator = CodeValidator()

        result = benchmark(validator.process, {"code": sample_code_large, "language": "python"})

        assert "valid" in result

    @pytest.mark.benchmark
    def test_multiple_skill_generations(self, benchmark, sample_maturity_data):
        """Test skill generation with multiple weak areas."""
        agent = SkillGeneratorAgent()

        # Maturity data with many weak areas
        complex_data = {
            **sample_maturity_data,
            "weak_categories": [
                "problem_definition",
                "scope",
                "architecture",
                "testing",
                "documentation",
                "performance",
            ],
        }

        result = benchmark(agent.process, {"action": "generate", "maturity_data": complex_data})

        assert len(result.get("skills", [])) > 0


class TestComparativeBenchmarks:
    """Compare performance across agents."""

    @pytest.mark.benchmark(group="agent-comparison")
    def test_counselor_vs_generator(self, benchmark):
        """Compare counselor and generator performance."""
        counselor = SocraticCounselor()
        generator = CodeGenerator()

        def run_both():
            counselor.process({"action": "guide", "topic": "testing"})
            generator.process({"prompt": "test function", "language": "python"})

        benchmark(run_both)
