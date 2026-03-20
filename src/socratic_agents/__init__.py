"""Socratic Agents - Multi-agent orchestration system for AI workflows."""

__version__ = "0.1.1"
__author__ = "Socratic Agents Contributors"

# Core base class
from .agents.base import BaseAgent
from .agents.code_generator import CodeGenerator
from .agents.code_validation_agent import CodeValidator
from .agents.conflict_detector import AgentConflictDetector
from .agents.context_analyzer import ContextAnalyzer
from .agents.document_context_analyzer import DocumentContextAnalyzer
from .agents.document_processor import DocumentProcessor
from .agents.github_sync_handler import GithubSyncHandler
from .agents.knowledge_analysis import KnowledgeAnalysis
from .agents.knowledge_manager import KnowledgeManager
from .agents.learning_agent import LearningAgent
from .agents.multi_llm_agent import MultiLlmAgent
from .agents.note_manager import NoteManager
from .agents.project_manager import ProjectManager
from .agents.quality_controller import QualityController
from .agents.question_queue_agent import QuestionQueueAgent
from .agents.skill_generator_agent import SkillGeneratorAgent

# Concrete agent implementations
from .agents.socratic_counselor import SocraticCounselor
from .agents.system_monitor import SystemMonitor
from .agents.user_manager import UserManager

# LLM-enhanced agent wrappers
from .llm_agents import (
    LLMAgentError,
    LLMPoweredCodeGenerator,
    LLMPoweredCodeValidator,
    LLMPoweredContextAnalyzer,
    LLMPoweredCounselor,
    LLMPoweredKnowledgeManager,
    LLMPoweredProjectManager,
    LLMPoweredQualityController,
)

# Data models
from .models import AgentSkill, SkillApplicationResult, SkillRecommendation


# Error classes for GitHub sync and integration
class ConflictResolutionError(Exception):
    """Raised when merge conflict cannot be resolved"""

    pass


class TokenExpiredError(Exception):
    """Raised when GitHub authentication token has expired"""

    pass


class PermissionDeniedError(Exception):
    """Raised when user lacks repository access"""

    pass


class RepositoryNotFoundError(Exception):
    """Raised when repository no longer exists or is inaccessible"""

    pass


class NetworkSyncFailedError(Exception):
    """Raised when sync fails after all retry attempts"""

    pass


class FileSizeExceededError(Exception):
    """Raised when file size exceeds GitHub limits"""

    pass


# Backward compatibility alias
ConflictDetector = AgentConflictDetector


# Factory functions
def create_github_sync_handler(db=None):
    """Factory function to create GitHub sync handler"""
    return GithubSyncHandler(db=db)


__all__ = [
    # Base class
    "BaseAgent",
    # Agent implementations
    "SocraticCounselor",
    "CodeGenerator",
    "CodeValidator",
    "KnowledgeManager",
    "LearningAgent",
    "MultiLlmAgent",
    "ProjectManager",
    "QualityController",
    "SkillGeneratorAgent",
    "ContextAnalyzer",
    "DocumentProcessor",
    "GithubSyncHandler",
    "SystemMonitor",
    "UserManager",
    "AgentConflictDetector",
    "ConflictDetector",  # Backward compatibility alias
    "KnowledgeAnalysis",
    "DocumentContextAnalyzer",
    "NoteManager",
    "QuestionQueueAgent",
    # Data models
    "AgentSkill",
    "SkillApplicationResult",
    "SkillRecommendation",
    # LLM-enhanced agent wrappers
    "LLMPoweredCounselor",
    "LLMPoweredCodeGenerator",
    "LLMPoweredCodeValidator",
    "LLMPoweredProjectManager",
    "LLMPoweredQualityController",
    "LLMPoweredKnowledgeManager",
    "LLMPoweredContextAnalyzer",
    "LLMAgentError",
    # Error classes
    "ConflictResolutionError",
    "TokenExpiredError",
    "PermissionDeniedError",
    "RepositoryNotFoundError",
    "NetworkSyncFailedError",
    "FileSizeExceededError",
    # Factory functions
    "create_github_sync_handler",
]
