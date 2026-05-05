"""
Socratic Agents System - Complete initialization and orchestration.

Provides turnkey initialization of the agent system for external projects.
Handles agent registration, service setup, and request routing.
"""

import asyncio
import logging
from typing import Any, Dict, Optional

from socratic_agents.config import SocratesConfig
from socratic_agents.orchestrator import AgentOrchestrator
from socratic_agents.registry import AgentRegistry
from socratic_agents.request_handler import RequestHandler
from socratic_agents.services import (
    ConfigService,
    DatabaseService,
    EventEmitterService,
    LLMService,
    VectorDatabaseService,
    create_service_adapters,
)
from socratic_agents.services.defaults import (
    DefaultConfigService,
    DefaultDatabaseService,
    DefaultEventEmitterService,
    DefaultLLMService,
    DefaultVectorDatabaseService,
)

logger = logging.getLogger(__name__)


class SocraticAgentsSystem:
    """
    Complete Socratic Agents system for external projects.

    Provides:
    - Agent registration and discovery
    - Service dependency injection
    - Request routing and standardization
    - Response normalization
    - Lifecycle management

    Example usage:

        # Initialize system
        system = SocraticAgentsSystem(
            api_key="sk-...",
            data_dir="/path/to/data"
        )

        # Use agent
        response = system.process_request(
            "project_manager",
            {"action": "create_project", "name": "My Project"}
        )

        # Or async
        response = await system.process_request_async(
            "code_generator",
            {"action": "generate_artifact", "context": "..."}
        )
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        data_dir: str = ".",
        claude_model: str = "claude-haiku-4-5-20251001",
        database: Optional[DatabaseService] = None,
        llm: Optional[LLMService] = None,
        vector_db: Optional[VectorDatabaseService] = None,
        config: Optional[ConfigService] = None,
        event_emitter: Optional[EventEmitterService] = None,
    ):
        """
        Initialize Socratic Agents system.

        Args:
            api_key: Anthropic API key (optional)
            data_dir: Data directory path
            claude_model: Claude model name
            database: Custom DatabaseService (uses default if None)
            llm: Custom LLMService (uses default if None)
            vector_db: Custom VectorDatabaseService (uses default if None)
            config: Custom ConfigService (uses default if None)
            event_emitter: Custom EventEmitterService (uses default if None)
        """
        self.logger = logging.getLogger("socratic_agents.system")

        # Initialize config
        self.config = config or DefaultConfigService(
            data_dir=data_dir,
            api_key=api_key,
            claude_model=claude_model,
        )

        # Initialize services (use defaults if not provided)
        self.event_emitter = event_emitter or DefaultEventEmitterService()
        self.database = database or DefaultDatabaseService()
        self.llm = llm or DefaultLLMService(api_key=api_key)
        self.vector_db = vector_db or DefaultVectorDatabaseService()

        # Initialize registry
        self.registry = AgentRegistry()
        self.registry.auto_register_agents()
        self.logger.info(f"Registered {len(self.registry.list_agents())} agents")

        # Initialize orchestrator
        self.orchestrator = AgentOrchestrator(
            database=self.database,
            vector_db=self.vector_db,
            claude_client=self.llm,
            config=self.config,
        )
        self.orchestrator.event_emitter = self.event_emitter
        self.logger.info("Orchestrator initialized")

        # Initialize request handler
        self.request_handler = RequestHandler()

    def list_agents(self) -> Dict[str, str]:
        """
        List all available agents.

        Returns:
            Dictionary of agent_name -> agent_class_name
        """
        return self.registry.list_agents()

    def get_agent(self, name: str) -> Optional[Any]:
        """
        Get an agent instance.

        Args:
            name: Agent name

        Returns:
            Agent instance or None if not found
        """
        agent = self.registry.create_agent(
            name,
            database=self.database,
            llm=self.llm,
            vector_db=self.vector_db,
            config=self.config,
            event_emitter=self.event_emitter,
        )
        return agent

    def process_request(self, agent_name: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a synchronous agent request.

        Args:
            agent_name: Name of agent to invoke
            request: Request dictionary

        Returns:
            Standardized response dictionary
        """
        try:
            # Get agent
            agent = self.get_agent(agent_name)
            if not agent:
                return {
                    "status": "error",
                    "data": {},
                    "message": f"Agent not found: {agent_name}",
                    "error_code": "AGENT_NOT_FOUND",
                }

            # Handle request
            return self.request_handler.handle_request_sync(agent, request)

        except Exception as e:
            self.logger.error(f"Error processing request: {e}", exc_info=True)
            return {
                "status": "error",
                "data": {},
                "message": str(e),
                "error_code": "SYSTEM_ERROR",
            }

    async def process_request_async(
        self, agent_name: str, request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process an asynchronous agent request.

        Args:
            agent_name: Name of agent to invoke
            request: Request dictionary

        Returns:
            Standardized response dictionary
        """
        try:
            # Get agent
            agent = self.get_agent(agent_name)
            if not agent:
                return {
                    "status": "error",
                    "data": {},
                    "message": f"Agent not found: {agent_name}",
                    "error_code": "AGENT_NOT_FOUND",
                }

            # Handle request
            return await self.request_handler.handle_request_async(agent, request)

        except Exception as e:
            self.logger.error(f"Error processing request: {e}", exc_info=True)
            return {
                "status": "error",
                "data": {},
                "message": str(e),
                "error_code": "SYSTEM_ERROR",
            }

    def register_agent(self, name: str, agent_class: Any) -> None:
        """
        Register a custom agent.

        Args:
            name: Agent name
            agent_class: Agent class
        """
        self.registry.register(name, agent_class)
        self.logger.info(f"Registered custom agent: {name}")

    def set_service(
        self,
        service_type: str,
        service: Any,
    ) -> None:
        """
        Replace a service implementation.

        Args:
            service_type: "database", "llm", "vector_db", "config", or "event_emitter"
            service: Service instance
        """
        if service_type == "database":
            self.database = service
        elif service_type == "llm":
            self.llm = service
        elif service_type == "vector_db":
            self.vector_db = service
        elif service_type == "config":
            self.config = service
        elif service_type == "event_emitter":
            self.event_emitter = service
            self.orchestrator.event_emitter = service
        else:
            self.logger.error(f"Unknown service type: {service_type}")
            return

        self.logger.info(f"Service '{service_type}' updated")

    def shutdown(self) -> None:
        """Clean up resources."""
        self.logger.info("Shutting down Socratic Agents system")
        # Add cleanup code as needed
