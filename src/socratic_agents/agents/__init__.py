"""Agent implementations for Socratic Agents."""

from .base import BaseAgent
from .socratic_counselor import SocraticCounselor
from .code_generator import CodeGenerator
from .code_validation_agent import CodeValidator
from .knowledge_manager import KnowledgeManager
from .learning_agent import LearningAgent
from .multi_llm_agent import MultiLlmAgent
from .project_manager import ProjectManager
from .quality_controller import QualityController
from .context_analyzer import ContextAnalyzer
from .document_processor import DocumentProcessor
from .github_sync_handler import GithubSyncHandler
from .system_monitor import SystemMonitor
from .user_manager import UserManager
from .conflict_detector import ConflictDetector
from .knowledge_analysis import KnowledgeAnalysis
from .document_context_analyzer import DocumentContextAnalyzer
from .note_manager import NoteManager
from .question_queue_agent import QuestionQueueAgent

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
