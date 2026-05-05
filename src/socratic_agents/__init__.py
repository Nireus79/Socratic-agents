from __future__ import annotations

"""
Socratic Agents - Distributed Agent Library

A comprehensive multi-agent platform providing 19+ specialized agents for
task automation, analysis, and orchestration.

Core Agents:
- SocraticCounselorAgent: Guides through Socratic questioning
- ProjectManagerAgent: Manages project lifecycle
- QualityControllerAgent: Orchestrates quality and maturity tracking
- CodeGeneratorAgent: Generates code and documentation
- UserLearningAgent: Tracks user behavior and learning
- DocumentProcessorAgent: Processes and analyzes documents
- ConflictDetectorAgent: Identifies and resolves conflicts
- NoteManagerAgent: Manages project notes
- UserManagerAgent: Manages user accounts
- And 10+ more specialized agents

Dependencies:
- pydantic>=2.0: Data validation
- Optional: socratic-morality (for governance features)

Architecture:
- Service-based dependency injection
- Agent bus for inter-agent communication
- Optional governance integration
- REST API support via FastAPI
"""

from .base import Agent
from .code_generator import CodeGeneratorAgent
from .code_validation_agent import CodeValidationAgent
from .conflict_detector import ConflictDetectorAgent
from .context_analyzer import ContextAnalyzerAgent
from .document_context_analyzer import DocumentContextAnalyzer
from .document_processor import DocumentProcessorAgent
from .events import EventType
from .knowledge_analysis import KnowledgeAnalysisAgent
from .knowledge_manager import KnowledgeManagerAgent
from .learning_agent import UserLearningAgent
from .models import (
    LLMProviderConfig,
    LLMUsageRecord,
    ProjectContext,
    ProviderMetadata,
    get_provider_metadata,
    list_available_providers,
)
from .multi_llm_agent import MultiLLMAgent
from .note_manager import NoteManagerAgent
from .orchestrator import AgentOrchestrator, EventEmitter
from .project_manager import ProjectManagerAgent
from .quality_controller import QualityControllerAgent
from .question_queue_agent import QuestionQueueAgent
from .socratic_counselor import SocraticCounselorAgent
from .system_monitor import SystemMonitorAgent
from .user_manager import UserManagerAgent

__all__ = [
    # Core classes
    "Agent",
    "EventType",
    "AgentOrchestrator",
    "EventEmitter",
    # Models
    "ProjectContext",
    "ProjectNote",
    "User",
    "TeamMemberRole",
    # Agent implementations
    "ProjectManagerAgent",
    "UserManagerAgent",
    "SocraticCounselorAgent",
    "ContextAnalyzerAgent",
    "CodeGeneratorAgent",
    "CodeValidationAgent",
    "SystemMonitorAgent",
    "ConflictDetectorAgent",
    "DocumentContextAnalyzer",
    "DocumentProcessorAgent",
    "NoteManagerAgent",
    "QualityControllerAgent",
    "KnowledgeAnalysisAgent",
    "KnowledgeManagerAgent",
    "UserLearningAgent",
    "MultiLLMAgent",
    "QuestionQueueAgent",
]

# Phase 4 - REST API Client (New)
from .client import (
    AgentNotFoundError,
    AgentTimeoutError,
    JobNotFoundError,
    SocratesAgentClient,
    SocratesAgentClientError,
    SocratesAgentClientSync,
)

__all__ = __all__ + [
    "SocratesAgentClient",
    "SocratesAgentClientSync",
    "SocratesAgentClientError",
    "AgentNotFoundError",
    "AgentTimeoutError",
    "JobNotFoundError",
]

# Agent bus for inter-agent communication
from .agent_bus import AgentBus, AgentMessage, MessageType

# Governance integration (optional - requires socratic-morality)
try:
    from .governance import GovernanceAdapter, GovernedAgent

    _GOVERNANCE_AVAILABLE = True
except ImportError:
    _GOVERNANCE_AVAILABLE = False
    GovernanceAdapter = None  # type: ignore
    GovernedAgent = None  # type: ignore

__all__ = __all__ + [
    # Agent bus
    "AgentBus",
    "AgentMessage",
    "MessageType",
]

# Add governance to exports if available
if _GOVERNANCE_AVAILABLE:
    __all__ = __all__ + [
        "GovernedAgent",
        "GovernanceAdapter",
    ]

# REST API support (optional - requires FastAPI)
try:
    from .api_app import create_app, run_api_server
    from .api_routes import create_agent_router, create_governance_router, create_precedent_router

    __all__ = __all__ + [
        "create_app",
        "run_api_server",
        "create_agent_router",
        "create_governance_router",
        "create_precedent_router",
    ]
except ImportError:
    pass  # FastAPI not installed

# GitHub sync utilities
# Phase 3 - Configuration
from .config import AgentConfig, GovernanceConfig, OrchestratorConfig
from .github_sync_handler import (
    ConflictResolutionError,
    FileSizeExceededError,
    GitHubSyncHandler,
    NetworkSyncFailedError,
    PermissionDeniedError,
    RepositoryNotFoundError,
    TokenExpiredError,
    create_github_sync_handler,
)

__all__ += [
    # GitHub sync utilities
    "GitHubSyncHandler",
    "create_github_sync_handler",
    "ConflictResolutionError",
    "TokenExpiredError",
    "PermissionDeniedError",
    "RepositoryNotFoundError",
    "NetworkSyncFailedError",
    "FileSizeExceededError",
    # Configuration
    "GovernanceConfig",
    "AgentConfig",
    "OrchestratorConfig",
]
