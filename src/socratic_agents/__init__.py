from __future__ import annotations

"""
Socratic Agents - Socrates-Integrated Agent Library

⚠️  **IMPORTANT: SOCRATES-ONLY LIBRARY**

This library is designed exclusively for use within the Socrates monolith.
It is NOT designed for standalone or independent use.

Requirements:
- Socrates monolith must be installed locally
- socratic_system module must be available
- Agents require full Socrates context to function

Agents in this library (Socrates-integrated):
- SocraticCounselorAgent: Guides users through Socratic questioning
- ProjectManagerAgent: Manages project lifecycle
- QualityControllerAgent: Orchestrates maturity tracking
- CodeGeneratorAgent: Generates code based on project context
- LearningAgent: Tracks user behavior and effectiveness
- DocumentProcessorAgent: Processes and imports documents
- ConflictDetectorAgent: Identifies and resolves conflicts
- NoteManagerAgent: Manages project notes
- UserManagerAgent: Manages user accounts
- And 10+ more specialized agents

Future:
After Socrates architecture redesign, some agents will be refactored for
independence and modularity. This library will be updated accordingly.

For independent Socratic libraries, see:
- socratic-analyzer: Code analysis (standalone)
- socratic-learning: Learning algorithms (standalone)
- Socratic-workflow: Workflow definitions (standalone)
- Socratic-maturity: Maturity tracking (standalone)
"""

from .base import Agent
from .code_generator import CodeGeneratorAgent
from .code_validation_agent import CodeValidationAgent
from .conflict_detector import ConflictDetectorAgent
from .context_analyzer import ContextAnalyzerAgent
from .document_processor import DocumentProcessorAgent
from .events import EventType
from .knowledge_analysis import KnowledgeAnalysisAgent
from .knowledge_manager import KnowledgeManagerAgent
from .learning_agent import UserLearningAgent
from .models import (
    LLMProviderConfig,
    LLMUsageRecord,
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
    "LLMProviderConfig",
    "LLMUsageRecord",
    "ProviderMetadata",
    "get_provider_metadata",
    "list_available_providers",
    # Agent implementations
    "ProjectManagerAgent",
    "UserManagerAgent",
    "SocraticCounselorAgent",
    "ContextAnalyzerAgent",
    "CodeGeneratorAgent",
    "CodeValidationAgent",
    "SystemMonitorAgent",
    "ConflictDetectorAgent",
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

# Phase 3 - Governance Integration (New)
from .agent_bus import AgentBus, AgentMessage, MessageType
from .governance import GovernanceAdapter, GovernedAgent

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

__all__ = __all__ + [
    # Governance
    "GovernedAgent",
    "GovernanceAdapter",
    # Agent bus
    "AgentBus",
    "AgentMessage",
    "MessageType",
]

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
