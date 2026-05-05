"""
Agent Registry - Discovery and lifecycle management for agents.

Provides centralized registration, discovery, and instantiation of agents
for use in external projects.
"""

import logging
from typing import Any, Dict, List, Optional, Type

from socratic_agents.base import Agent

logger = logging.getLogger(__name__)


class AgentRegistry:
    """
    Registry for managing agent classes and instances.

    Supports:
    - Agent class registration by name
    - Agent discovery and listing
    - Agent instantiation with dependency injection
    - Singleton and prototype patterns
    """

    def __init__(self):
        """Initialize the agent registry."""
        self._agent_classes: Dict[str, Type[Agent]] = {}
        self._agent_instances: Dict[str, Agent] = {}
        self.logger = logging.getLogger("socratic_agents.registry")

    def register(self, name: str, agent_class: Type[Agent], singleton: bool = True) -> None:
        """
        Register an agent class.

        Args:
            name: Unique name for the agent
            agent_class: Agent class to register
            singleton: If True, same instance returned each time. If False, new instance created.
        """
        if not issubclass(agent_class, Agent):
            raise TypeError(f"{agent_class} must be a subclass of Agent")

        self._agent_classes[name] = agent_class
        self.logger.info(f"Registered agent: {name} ({agent_class.__name__})")

    def get_agent_class(self, name: str) -> Optional[Type[Agent]]:
        """
        Get an agent class by name.

        Args:
            name: Agent name

        Returns:
            Agent class or None if not found
        """
        return self._agent_classes.get(name)

    def list_agents(self) -> Dict[str, str]:
        """
        List all registered agents with descriptions.

        Returns:
            Dictionary of agent_name -> agent_class_name
        """
        return {name: cls.__name__ for name, cls in self._agent_classes.items()}

    def create_agent(
        self,
        name: str,
        database: Optional[Any] = None,
        llm: Optional[Any] = None,
        vector_db: Optional[Any] = None,
        config: Optional[Any] = None,
        event_emitter: Optional[Any] = None,
        orchestrator: Optional[Any] = None,
    ) -> Optional[Agent]:
        """
        Create an agent instance with dependency injection.

        Args:
            name: Agent name
            database: DatabaseService instance
            llm: LLMService instance
            vector_db: VectorDatabaseService instance
            config: ConfigService instance
            event_emitter: EventEmitterService instance
            orchestrator: (Legacy) AgentOrchestrator instance

        Returns:
            Agent instance or None if not found
        """
        agent_class = self._agent_classes.get(name)
        if not agent_class:
            self.logger.error(f"Agent not found: {name}")
            return None

        # Create agent with services
        try:
            agent = agent_class(
                name=name,
                orchestrator=orchestrator,
                database=database,
                llm=llm,
                vector_db=vector_db,
                config=config,
                event_emitter=event_emitter,
            )
            self.logger.info(f"Created agent instance: {name}")
            return agent
        except TypeError:
            # Fallback: Try with just orchestrator (backward compatibility)
            if orchestrator is not None:
                try:
                    agent = agent_class(name=name, orchestrator=orchestrator)
                    self.logger.info(f"Created agent instance (legacy): {name}")
                    return agent
                except Exception as e:
                    self.logger.error(f"Failed to create agent {name} with orchestrator: {e}")
                    return None
            else:
                self.logger.error(f"Failed to create agent {name}: missing orchestrator or services")
                return None

    def auto_register_agents(self) -> None:
        """
        Auto-register all built-in agents.

        Scans the socratic_agents module and registers all Agent subclasses.
        """
        from socratic_agents import (
            CodeGeneratorAgent,
            CodeValidationAgent,
            ConflictDetectorAgent,
            ContextAnalyzerAgent,
            DocumentContextAnalyzer,
            DocumentProcessorAgent,
            KnowledgeAnalysisAgent,
            KnowledgeManagerAgent,
            MultiLLMAgent,
            NoteManagerAgent,
            ProjectManagerAgent,
            QualityControllerAgent,
            QuestionQueueAgent,
            SocraticCounselorAgent,
            SystemMonitorAgent,
            UserLearningAgent,
            UserManagerAgent,
        )

        agents = [
            ("project_manager", ProjectManagerAgent),
            ("socratic_counselor", SocraticCounselorAgent),
            ("code_generator", CodeGeneratorAgent),
            ("code_validation", CodeValidationAgent),
            ("context_analyzer", ContextAnalyzerAgent),
            ("conflict_detector", ConflictDetectorAgent),
            ("document_processor", DocumentProcessorAgent),
            ("document_context_analyzer", DocumentContextAnalyzer),
            ("user_manager", UserManagerAgent),
            ("note_manager", NoteManagerAgent),
            ("knowledge_manager", KnowledgeManagerAgent),
            ("knowledge_analysis", KnowledgeAnalysisAgent),
            ("quality_controller", QualityControllerAgent),
            ("system_monitor", SystemMonitorAgent),
            ("learning_agent", UserLearningAgent),
            ("multi_llm", MultiLLMAgent),
            ("question_queue", QuestionQueueAgent),
        ]

        for name, agent_class in agents:
            self.register(name, agent_class)

        self.logger.info(f"Auto-registered {len(agents)} agents")
