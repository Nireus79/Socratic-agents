"""Agent implementations for Socratic Agents."""

from .base import BaseAgent
from .code_generator import CodeGenerator
from .code_validation_agent import CodeValidator
from .conflict_detector import ConflictDetector
from .context_analyzer import ContextAnalyzer
from .document_context_analyzer import DocumentContextAnalyzer
from .document_processor import DocumentProcessor
from .github_sync_handler import GithubSyncHandler
from .knowledge_analysis import KnowledgeAnalysis
from .knowledge_manager import KnowledgeManager
from .learning_agent import LearningAgent
from .multi_llm_agent import MultiLlmAgent
from .note_manager import NoteManager
from .project_manager import ProjectManager
from .quality_controller import QualityController
from .question_queue_agent import QuestionQueueAgent
from .socratic_counselor import SocraticCounselor
from .system_monitor import SystemMonitor
from .user_manager import UserManager

__all__ = [
    "BaseAgent",
    "SocraticCounselor",
    "CodeGenerator",
    "CodeValidator",
    "KnowledgeManager",
    "LearningAgent",
    "MultiLlmAgent",
    "ProjectManager",
    "QualityController",
    "ContextAnalyzer",
    "DocumentProcessor",
    "GithubSyncHandler",
    "SystemMonitor",
    "UserManager",
    "ConflictDetector",
    "KnowledgeAnalysis",
    "DocumentContextAnalyzer",
    "NoteManager",
    "QuestionQueueAgent",
]
