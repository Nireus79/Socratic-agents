
import pytest

from socratic_agents.agents.quality_controller import QualityController
from socratic_agents.integrations.skill_orchestrator import SkillOrchestrator


class TestSkillOrchestrationFlow:
    @pytest.fixture
    def orchestrator(self):
        return SkillOrchestrator()

    @pytest.fixture
    def sample_code(self):
        return "def bad(): x=1; if x: pass"

    def test_init(self, orchestrator):
        assert orchestrator.name == "SkillOrchestrator"
        assert isinstance(orchestrator.quality_controller, QualityController)

    def test_empty_code(self, orchestrator):
        result = orchestrator.process_quality_issue("")
        assert result["status"] == "error"

    def test_process_quality(self, orchestrator, sample_code):
        result = orchestrator.process_quality_issue(sample_code)
        assert result["status"] == "success"
        assert "session_id" in result

    def test_apply_skill(self, orchestrator):
        result = orchestrator.apply_and_track_skill("s1", {"name": "test"})
        assert result["status"] == "success"

    def test_get_history(self, orchestrator, sample_code):
        orchestrator.process_quality_issue(sample_code)
        history = orchestrator.get_skills_history()
        assert history["status"] == "success"

    def test_learning_profile(self, orchestrator):
        p = orchestrator.get_learning_profile()
        assert p["status"] == "success"

    def test_effectiveness(self, orchestrator):
        e = orchestrator.analyze_skill_effectiveness()
        assert e["status"] == "success"
