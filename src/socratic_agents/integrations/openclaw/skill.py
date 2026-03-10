"""Openclaw skill for Socratic Agents orchestration."""

from typing import Any, Dict, List, Optional

from socratic_agents import (
    BaseAgent,
    CodeGenerator,
    CodeValidator,
    ConflictDetector,
    ContextAnalyzer,
    DocumentContextAnalyzer,
    DocumentProcessor,
    GithubSyncHandler,
    KnowledgeAnalysis,
    KnowledgeManager,
    LearningAgent,
    MultiLlmAgent,
    NoteManager,
    ProjectManager,
    QualityController,
    QuestionQueueAgent,
    SocraticCounselor,
    SystemMonitor,
    UserManager,
)


class SocraticAgentsSkill:
    """
    Openclaw skill for multi-agent orchestration using Socratic Agents.

    Provides access to all 18 agents through a unified Openclaw skill interface.
    """

    AGENTS = {
        "counselor": SocraticCounselor,
        "code_generator": CodeGenerator,
        "code_validator": CodeValidator,
        "knowledge_manager": KnowledgeManager,
        "learning_agent": LearningAgent,
        "llm_coordinator": MultiLlmAgent,
        "project_manager": ProjectManager,
        "quality_controller": QualityController,
        "context_analyzer": ContextAnalyzer,
        "document_processor": DocumentProcessor,
        "github_sync": GithubSyncHandler,
        "system_monitor": SystemMonitor,
        "user_manager": UserManager,
        "conflict_detector": ConflictDetector,
        "knowledge_analyzer": KnowledgeAnalysis,
        "doc_context_analyzer": DocumentContextAnalyzer,
        "note_manager": NoteManager,
        "question_queue": QuestionQueueAgent,
    }

    def __init__(self, llm_client: Optional[Any] = None, **kwargs):
        """
        Initialize the Socratic Agents skill.

        Args:
            llm_client: Optional LLMClient from Socrates Nexus
            **kwargs: Additional configuration options
        """
        self.llm_client = llm_client
        self.config = kwargs
        self.agents: Dict[str, BaseAgent] = {}

        # Initialize agents with LLM client
        for agent_name, agent_class in self.AGENTS.items():
            self.agents[agent_name] = agent_class(llm_client=llm_client)

    def get_agent(self, agent_name: str) -> Optional[BaseAgent]:
        """Get an agent by name."""
        return self.agents.get(agent_name)

    def list_agents(self) -> List[str]:
        """List all available agents."""
        return list(self.AGENTS.keys())

    def execute_workflow(self, task: str, agents: List[str], **kwargs) -> Dict[str, Any]:
        """
        Execute a multi-agent workflow.

        Args:
            task: Description of the task
            agents: List of agent names to use
            **kwargs: Additional parameters for agents

        Returns:
            Workflow execution result
        """
        results = {}

        for agent_name in agents:
            agent = self.get_agent(agent_name)
            if not agent:
                results[agent_name] = {
                    "status": "error",
                    "message": f"Agent '{agent_name}' not found",
                }
                continue

            try:
                request = {"task": task, **kwargs}
                result = agent.process(request)
                results[agent_name] = result
            except Exception as e:
                results[agent_name] = {"status": "error", "message": str(e)}

        return {
            "status": "success",
            "task": task,
            "agents_executed": len([r for r in results.values() if r.get("status") == "success"]),
            "results": results,
        }

    def guide(self, topic: str, level: str = "beginner") -> Dict[str, Any]:
        """
        Use Socratic Counselor to guide learning.

        Args:
            topic: Topic to learn about
            level: Learning level (beginner, intermediate, advanced)

        Returns:
            Guiding questions
        """
        agent = self.agents["counselor"]
        return agent.process({"topic": topic, "level": level})

    def generate_code(self, prompt: str, language: str = "python") -> str:
        """
        Generate code using CodeGenerator agent.

        Args:
            prompt: Description of code to generate
            language: Programming language

        Returns:
            Generated code
        """
        agent = self.agents["code_generator"]
        result = agent.process({"prompt": prompt, "language": language})
        return result.get("code", "")

    def validate_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Validate code using CodeValidator agent.

        Args:
            code: Code to validate
            language: Programming language

        Returns:
            Validation results
        """
        agent = self.agents["code_validator"]
        return agent.process({"code": code, "language": language})
