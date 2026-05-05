"""Socratic Agents Models

Extracted from socratic_system to make agents fully independent.
"""

from .knowledge import KnowledgeEntry
from .learning import KnowledgeBaseDocument, QuestionEffectiveness, UserBehaviorPattern
from .monitoring import TokenUsage
from .note import ProjectNote
from .project import ProjectContext
from .role import ROLE_EXAMPLES, ROLE_FOCUS_AREAS, VALID_ROLES, TeamMemberRole
from .user import User
from .workflow import (
    PathDecisionStrategy,
    WorkflowApprovalRequest,
    WorkflowDefinition,
    WorkflowEdge,
    WorkflowExecutionState,
    WorkflowNode,
    WorkflowNodeType,
    WorkflowPath,
)

__all__ = [
    # Models
    "ProjectContext",
    "ProjectNote",
    "KnowledgeEntry",
    "TeamMemberRole",
    "User",
    "TokenUsage",
    "WorkflowApprovalRequest",
    "WorkflowDefinition",
    "WorkflowNode",
    "WorkflowNodeType",
    "WorkflowEdge",
    "WorkflowPath",
    "WorkflowExecutionState",
    "PathDecisionStrategy",
    "QuestionEffectiveness",
    "UserBehaviorPattern",
    "KnowledgeBaseDocument",
    # Role definitions
    "VALID_ROLES",
    "ROLE_FOCUS_AREAS",
    "ROLE_EXAMPLES",
]
