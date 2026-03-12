"""Socratic Agents - Multi-agent orchestration system for AI workflows."""

__version__ = "0.1.1"
__author__ = "Socratic Agents Contributors"

# Core base class
from .agents.base import BaseAgent
from .agents.code_generator import CodeGenerator
from .agents.code_validation_agent import CodeValidator
from .agents.conflict_detector import ConflictDetector
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
    "ConflictDetector",
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
]
