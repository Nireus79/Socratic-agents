"""Event types and event system for Socratic Agents."""

from enum import Enum


class EventType(Enum):
    """Event types emitted by agents during processing."""

    # Logging events
    LOG_DEBUG = "log_debug"
    LOG_INFO = "log_info"
    LOG_WARNING = "log_warning"
    LOG_ERROR = "log_error"

    # Code generation events
    CODE_GENERATED = "code_generated"
    CODE_ANALYSIS_COMPLETE = "code_analysis_complete"

    # Knowledge and learning events
    KNOWLEDGE_SUGGESTION = "knowledge_suggestion"
    DOCUMENT_IMPORTED = "document_imported"
    QUESTIONS_REGENERATED = "questions_regenerated"

    # Workflow and approval events
    WORKFLOW_NODE_ENTERED = "workflow_node_entered"
    WORKFLOW_NODE_COMPLETED = "workflow_node_completed"
    WORKFLOW_APPROVAL_REQUESTED = "workflow_approval_requested"
    WORKFLOW_APPROVED = "workflow_approved"
    WORKFLOW_REJECTED = "workflow_rejected"

    # Quality and maturity events
    QUALITY_CHECK_PASSED = "quality_check_passed"
    QUALITY_CHECK_WARNING = "quality_check_warning"
    PHASE_READY_TO_ADVANCE = "phase_ready_to_advance"
    PHASE_ADVANCED = "phase_advanced"
    PHASE_MATURITY_UPDATED = "phase_maturity_updated"
