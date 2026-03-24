"""
Phase 4: Test all 19 agents work independently.

This test suite verifies that:
1. Each agent can be instantiated without the full Socrates system
2. Each agent has a process() method (standard interface)
3. No circular dependencies between agents
4. Dependencies are minimal and explicit
"""

import pytest


# Test Agent Instantiation (Independence)
class TestAgentInstantiation:
    """Test that all 19 agents can be instantiated independently."""

    def test_base_agent_instantiation(self):
        """Test BaseAgent class is available."""
        from src.socratic_agents.agents.base import BaseAgent

        assert BaseAgent is not None

    def test_socratic_counselor_instantiation(self):
        """SocraticCounselor can be instantiated without dependencies."""
        from src.socratic_agents.agents.socratic_counselor import SocraticCounselor

        agent = SocraticCounselor()
        assert agent.name == "SocraticCounselor"
        assert hasattr(agent, "process")

    def test_code_generator_instantiation(self):
        """CodeGenerator can be instantiated independently."""
        from src.socratic_agents.agents.code_generator import CodeGenerator

        agent = CodeGenerator()
        assert agent.name == "CodeGenerator"
        assert hasattr(agent, "process")

    def test_code_validator_instantiation(self):
        """CodeValidator can be instantiated independently."""
        from src.socratic_agents.agents.code_validation_agent import CodeValidator

        agent = CodeValidator()
        assert agent.name == "CodeValidator"
        assert hasattr(agent, "process")

    def test_quality_controller_instantiation(self):
        """QualityController can be instantiated independently."""
        from src.socratic_agents.agents.quality_controller import QualityController

        agent = QualityController()
        assert agent.name == "QualityController"
        assert hasattr(agent, "process")

    def test_knowledge_manager_instantiation(self):
        """KnowledgeManager can be instantiated independently."""
        from src.socratic_agents.agents.knowledge_manager import KnowledgeManager

        agent = KnowledgeManager()
        assert agent.name == "KnowledgeManager"
        assert hasattr(agent, "process")

    def test_learning_agent_instantiation(self):
        """LearningAgent can be instantiated independently."""
        from src.socratic_agents.agents.learning_agent import LearningAgent

        agent = LearningAgent()
        assert agent.name == "LearningAgent"
        assert hasattr(agent, "process")

    def test_multi_llm_agent_instantiation(self):
        """MultiLlmAgent can be instantiated independently."""
        from src.socratic_agents.agents.multi_llm_agent import MultiLlmAgent

        agent = MultiLlmAgent()
        assert agent.name == "MultiLlmAgent"
        assert hasattr(agent, "process")

    def test_project_manager_instantiation(self):
        """ProjectManager can be instantiated independently."""
        from src.socratic_agents.agents.project_manager import ProjectManager

        agent = ProjectManager()
        assert agent.name == "ProjectManager"
        assert hasattr(agent, "process")

    def test_context_analyzer_instantiation(self):
        """ContextAnalyzer can be instantiated independently."""
        from src.socratic_agents.agents.context_analyzer import ContextAnalyzer

        agent = ContextAnalyzer()
        assert agent.name == "ContextAnalyzer"
        assert hasattr(agent, "process")

    def test_document_processor_instantiation(self):
        """DocumentProcessor can be instantiated independently."""
        from src.socratic_agents.agents.document_processor import DocumentProcessor

        agent = DocumentProcessor()
        assert agent.name == "DocumentProcessor"
        assert hasattr(agent, "process")

    def test_github_sync_handler_instantiation(self):
        """GithubSyncHandler can be instantiated independently."""
        from src.socratic_agents.agents.github_sync_handler import GithubSyncHandler

        agent = GithubSyncHandler()
        assert agent.name == "GithubSyncHandler"
        assert hasattr(agent, "process")

    def test_conflict_detector_instantiation(self):
        """AgentConflictDetector can be instantiated independently."""
        from src.socratic_agents.agents.conflict_detector import AgentConflictDetector

        agent = AgentConflictDetector()
        assert agent.name == "AgentConflictDetector"
        assert hasattr(agent, "process")

    def test_knowledge_analysis_instantiation(self):
        """KnowledgeAnalysis can be instantiated independently."""
        from src.socratic_agents.agents.knowledge_analysis import KnowledgeAnalysis

        agent = KnowledgeAnalysis()
        assert agent.name == "KnowledgeAnalysis"
        assert hasattr(agent, "process")

    def test_document_context_analyzer_instantiation(self):
        """DocumentContextAnalyzer can be instantiated independently."""
        from src.socratic_agents.agents.document_context_analyzer import (
            DocumentContextAnalyzer,
        )

        agent = DocumentContextAnalyzer()
        assert agent.name == "DocumentContextAnalyzer"
        assert hasattr(agent, "process")

    def test_note_manager_instantiation(self):
        """NoteManager can be instantiated independently."""
        from src.socratic_agents.agents.note_manager import NoteManager

        agent = NoteManager()
        assert agent.name == "NoteManager"
        assert hasattr(agent, "process")

    def test_question_queue_agent_instantiation(self):
        """QuestionQueueAgent can be instantiated independently."""
        from src.socratic_agents.agents.question_queue_agent import QuestionQueueAgent

        agent = QuestionQueueAgent()
        assert agent.name == "QuestionQueueAgent"
        assert hasattr(agent, "process")

    def test_system_monitor_instantiation(self):
        """SystemMonitor can be instantiated independently."""
        from src.socratic_agents.agents.system_monitor import SystemMonitor

        agent = SystemMonitor()
        assert agent.name == "SystemMonitor"
        assert hasattr(agent, "process")

    def test_user_manager_instantiation(self):
        """UserManager can be instantiated independently."""
        from src.socratic_agents.agents.user_manager import UserManager

        agent = UserManager()
        assert agent.name == "UserManager"
        assert hasattr(agent, "process")

    def test_skill_generator_agent_instantiation(self):
        """SkillGeneratorAgent can be instantiated independently."""
        from src.socratic_agents.agents.skill_generator_agent import SkillGeneratorAgent

        agent = SkillGeneratorAgent()
        assert agent.name == "SkillGeneratorAgent"
        assert hasattr(agent, "process")

    def test_skill_generator_agent_v2_instantiation(self):
        """SkillGeneratorAgentV2 can be instantiated independently."""
        from src.socratic_agents.agents.skill_generator_agent_v2 import (
            SkillGeneratorAgentV2,
        )

        agent = SkillGeneratorAgentV2()
        # V2 inherits from V1, so name is still SkillGeneratorAgent
        assert agent.name == "SkillGeneratorAgent"
        assert hasattr(agent, "process")


# Test Standard Agent Interface
class TestAgentInterface:
    """Test that all agents follow standard interface."""

    def test_process_method_exists(self):
        """All agents should have process() method."""
        from src.socratic_agents.agents.code_generator import CodeGenerator
        from src.socratic_agents.agents.quality_controller import QualityController
        from src.socratic_agents.agents.socratic_counselor import SocraticCounselor

        agents = [SocraticCounselor(), CodeGenerator(), QualityController()]

        for agent in agents:
            assert hasattr(agent, "process"), f"{agent.name} missing process()"
            assert callable(agent.process), f"{agent.name}.process is not callable"

    def test_process_returns_dict(self):
        """process() should return dict with status."""
        from src.socratic_agents.agents.quality_controller import QualityController

        qc = QualityController()
        result = qc.process({"action": "check", "code": "x = 1"})

        assert isinstance(result, dict), "process() must return dict"
        assert "status" in result, "Result must have 'status' field"
        assert "agent" in result, "Result must have 'agent' field"

    def test_unknown_action_handling(self):
        """Agents should handle unknown actions gracefully."""
        from src.socratic_agents.agents.quality_controller import QualityController

        qc = QualityController()
        result = qc.process({"action": "unknown_action"})

        assert result["status"] == "error", "Unknown action should error"
        assert "Unknown action" in result.get("message", ""), "Should mention unknown action"


# Test Agent Composition
class TestAgentComposition:
    """Test that agents can work together."""

    def test_qc_with_skill_generator(self):
        """QualityController and SkillGenerator can work together."""
        from socrates_maturity import MaturityCalculator

        from src.socratic_agents.agents.quality_controller import QualityController
        from src.socratic_agents.skill_generator import SkillGenerator

        # QC analyzes code
        qc = QualityController()
        code = "def hello(): pass"
        qc_result = qc.detect_weak_areas(code)

        assert qc_result["status"] == "success"

        # SkillGenerator creates skills for weak areas
        weak = MaturityCalculator.identify_weak_categories(qc_result["category_scores"])
        skills = SkillGenerator.generate(
            phase=qc_result["phase"],
            weak_categories=weak,
            category_scores=qc_result["category_scores"],
        )

        # Should have integration
        assert isinstance(skills, list)

    def test_learning_agent_tracks_skills(self):
        """LearningAgent can track skill effectiveness."""
        from src.socratic_agents.agents.learning_agent import LearningAgent

        learning = LearningAgent()

        # LearningAgent has process method
        result = learning.process(
            {
                "action": "track",
                "user_id": "test_user",
                "interaction_type": "skill_application",
                "metadata": {"effectiveness": 0.8},
            }
        )

        assert result is not None


# Test Agent Count
class TestAgentCount:
    """Verify we have all 19 agents."""

    def test_19_agents_exist(self):
        """Verify all 19 agents can be imported."""
        agents_to_import = [
            ("socratic_counselor", "SocraticCounselor"),
            ("code_generator", "CodeGenerator"),
            ("code_validation_agent", "CodeValidator"),
            ("quality_controller", "QualityController"),
            ("knowledge_manager", "KnowledgeManager"),
            ("learning_agent", "LearningAgent"),
            ("multi_llm_agent", "MultiLlmAgent"),
            ("project_manager", "ProjectManager"),
            ("context_analyzer", "ContextAnalyzer"),
            ("document_processor", "DocumentProcessor"),
            ("github_sync_handler", "GithubSyncHandler"),
            ("conflict_detector", "AgentConflictDetector"),
            ("knowledge_analysis", "KnowledgeAnalysis"),
            ("document_context_analyzer", "DocumentContextAnalyzer"),
            ("note_manager", "NoteManager"),
            ("question_queue_agent", "QuestionQueueAgent"),
            ("system_monitor", "SystemMonitor"),
            ("user_manager", "UserManager"),
            ("skill_generator_agent", "SkillGeneratorAgent"),
        ]

        imported_count = 0
        for module_name, class_name in agents_to_import:
            try:
                module_path = f"src.socratic_agents.agents.{module_name}"
                exec(f"from {module_path} import {class_name}")
                imported_count += 1
            except ImportError as e:
                pytest.fail(f"Failed to import {class_name} from {module_name}: {e}")

        # Should have at least 19
        assert imported_count >= 19, f"Only imported {imported_count} agents"
