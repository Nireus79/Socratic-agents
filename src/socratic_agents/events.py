"""
Comprehensive event system for Socratic agents.

Defines all 93 event types for system-wide communication and monitoring.
Organized by functional domain for clarity and scalability.
"""

from enum import Enum


class EventType(Enum):
    """Complete event type enumeration - 93 event types across all domains."""

    # ==================== WORKFLOW EVENTS (12) ====================
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"
    WORKFLOW_PAUSED = "workflow_paused"
    WORKFLOW_RESUMED = "workflow_resumed"
    WORKFLOW_CANCELLED = "workflow_cancelled"
    PHASE_STARTED = "phase_started"
    PHASE_COMPLETED = "phase_completed"
    PHASE_CHANGED = "phase_changed"
    PHASE_GATING_CHECK = "phase_gating_check"
    PHASE_GATE_PASSED = "phase_gate_passed"
    PHASE_GATE_FAILED = "phase_gate_failed"

    # ==================== AGENT EVENTS (15) ====================
    AGENT_INITIALIZED = "agent_initialized"
    AGENT_STARTED = "agent_started"
    AGENT_COMPLETED = "agent_completed"
    AGENT_FAILED = "agent_failed"
    AGENT_TIMEOUT = "agent_timeout"
    AGENT_QUEUED = "agent_queued"
    AGENT_EXECUTING = "agent_executing"
    AGENT_CACHED = "agent_cached"
    AGENT_CACHE_HIT = "agent_cache_hit"
    AGENT_CACHE_MISS = "agent_cache_miss"
    AGENT_ERROR = "agent_error"
    AGENT_RETRY = "agent_retry"
    AGENT_SKIPPED = "agent_skipped"
    AGENT_DEPRECATED = "agent_deprecated"
    AGENT_UPDATED = "agent_updated"

    # ==================== SKILL EVENTS (14) ====================
    SKILL_GENERATED = "skill_generated"
    SKILL_VALIDATED = "skill_validated"
    SKILL_APPLIED = "skill_applied"
    SKILL_FAILED = "skill_failed"
    SKILL_COMPOSED = "skill_composed"
    SKILL_VERSIONED = "skill_versioned"
    SKILL_DEPRECATED = "skill_deprecated"
    SKILL_COMPATIBILITY_CHECK = "skill_compatibility_check"
    SKILL_PARAMETER_OPTIMIZED = "skill_parameter_optimized"
    SKILL_EFFECTIVENESS_ANALYZED = "skill_effectiveness_analyzed"
    SKILL_RECOMMENDATION_GENERATED = "skill_recommendation_generated"
    SKILL_ORCHESTRATION_STARTED = "skill_orchestration_started"
    SKILL_ORCHESTRATION_COMPLETED = "skill_orchestration_completed"
    SKILL_INTERACTION_TRACKED = "skill_interaction_tracked"

    # ==================== QUALITY & VALIDATION EVENTS (11) ====================
    QUALITY_GATE_PASSED = "quality_gate_passed"
    QUALITY_GATE_FAILED = "quality_gate_failed"
    CODE_REVIEWED = "code_reviewed"
    CODE_VALIDATED = "code_validated"
    DESIGN_VALIDATED = "design_validated"
    ARCHITECTURE_VALIDATED = "architecture_validated"
    PERFORMANCE_VALIDATED = "performance_validated"
    SECURITY_VALIDATED = "security_validated"
    TEST_COVERAGE_ANALYZED = "test_coverage_analyzed"
    VALIDATION_STARTED = "validation_started"
    VALIDATION_COMPLETED = "validation_completed"

    # ==================== LEARNING & FEEDBACK EVENTS (12) ====================
    LEARNING_STARTED = "learning_started"
    LEARNING_COMPLETED = "learning_completed"
    FEEDBACK_RECORDED = "feedback_recorded"
    FEEDBACK_ANALYZED = "feedback_analyzed"
    PATTERN_DETECTED = "pattern_detected"
    BEHAVIOR_ANALYZED = "behavior_analyzed"
    RECOMMENDATION_GENERATED = "recommendation_generated"
    EFFECTIVENESS_CALCULATED = "effectiveness_calculated"
    USER_INTERACTION = "user_interaction"
    QUESTION_ANSWERED = "question_answered"
    LEARNING_GOAL_ACHIEVED = "learning_goal_achieved"

    # ==================== CONFLICT RESOLUTION EVENTS (8) ====================
    CONFLICT_DETECTED = "conflict_detected"
    CONFLICT_ANALYZED = "conflict_analyzed"
    CONFLICT_RESOLVED = "conflict_resolved"
    CONFLICT_ESCALATED = "conflict_escalated"
    CONSENSUS_REACHED = "consensus_reached"
    CONSENSUS_FAILED = "consensus_failed"
    DECISION_MADE = "decision_made"
    RESOLUTION_APPROVED = "resolution_approved"

    # ==================== KNOWLEDGE & CONTEXT EVENTS (10) ====================
    KNOWLEDGE_INDEXED = "knowledge_indexed"
    KNOWLEDGE_RETRIEVED = "knowledge_retrieved"
    KNOWLEDGE_UPDATED = "knowledge_updated"
    KNOWLEDGE_DELETED = "knowledge_deleted"
    CONTEXT_ANALYZED = "context_analyzed"
    CONTEXT_ENRICHED = "context_enriched"
    DOCUMENT_PROCESSED = "document_processed"
    DOCUMENT_ANALYZED = "document_analyzed"
    SEMANTIC_SEARCH_PERFORMED = "semantic_search_performed"
    KNOWLEDGE_GRAPH_UPDATED = "knowledge_graph_updated"

    # ==================== PERFORMANCE & MONITORING EVENTS (11) ====================
    PERFORMANCE_METRIC_RECORDED = "performance_metric_recorded"
    LATENCY_THRESHOLD_EXCEEDED = "latency_threshold_exceeded"
    TOKEN_LIMIT_APPROACHING = "token_limit_approaching"
    TOKEN_LIMIT_EXCEEDED = "token_limit_exceeded"
    COST_THRESHOLD_EXCEEDED = "cost_threshold_exceeded"
    RESOURCE_USAGE_HIGH = "resource_usage_high"
    HEALTH_CHECK_PASSED = "health_check_passed"
    HEALTH_CHECK_FAILED = "health_check_failed"
    BOTTLENECK_DETECTED = "bottleneck_detected"
    OPTIMIZATION_OPPORTUNITY = "optimization_opportunity"
    MONITORING_ALERT = "monitoring_alert"

    # ==================== DATA & PERSISTENCE EVENTS (8) ====================
    DATA_SAVED = "data_saved"
    DATA_LOADED = "data_loaded"
    DATA_VALIDATED = "data_validated"
    DATA_TRANSFORMED = "data_transformed"
    DATABASE_ERROR = "database_error"
    CACHE_UPDATED = "cache_updated"
    BACKUP_CREATED = "backup_created"
    RECOVERY_STARTED = "recovery_started"

    # ==================== USER & SESSION EVENTS (7) ====================
    USER_AUTHENTICATED = "user_authenticated"
    USER_SESSION_STARTED = "user_session_started"
    USER_SESSION_ENDED = "user_session_ended"
    USER_PREFERENCE_CHANGED = "user_preference_changed"
    USER_ROLE_CHANGED = "user_role_changed"
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_DENIED = "permission_denied"

    # ==================== ERROR & RECOVERY EVENTS (6) ====================
    ERROR_OCCURRED = "error_occurred"
    ERROR_RECOVERED = "error_recovered"
    FATAL_ERROR = "fatal_error"
    RETRY_SCHEDULED = "retry_scheduled"
    RETRY_EXCEEDED = "retry_exceeded"
    FALLBACK_TRIGGERED = "fallback_triggered"

    # ==================== COORDINATION EVENTS (3) ====================
    WORKFLOW_COORDINATION = "workflow_coordination"
    MULTI_AGENT_SYNC = "multi_agent_sync"
    ORCHESTRATION_COMPLETE = "orchestration_complete"


# Event categories for filtering and processing
EVENT_CATEGORIES = {
    "workflow": [
        EventType.WORKFLOW_STARTED,
        EventType.WORKFLOW_COMPLETED,
        EventType.WORKFLOW_FAILED,
        EventType.WORKFLOW_PAUSED,
        EventType.WORKFLOW_RESUMED,
        EventType.WORKFLOW_CANCELLED,
        EventType.PHASE_STARTED,
        EventType.PHASE_COMPLETED,
        EventType.PHASE_CHANGED,
        EventType.PHASE_GATING_CHECK,
        EventType.PHASE_GATE_PASSED,
        EventType.PHASE_GATE_FAILED,
    ],
    "agent": [
        EventType.AGENT_INITIALIZED,
        EventType.AGENT_STARTED,
        EventType.AGENT_COMPLETED,
        EventType.AGENT_FAILED,
        EventType.AGENT_TIMEOUT,
        EventType.AGENT_QUEUED,
        EventType.AGENT_EXECUTING,
        EventType.AGENT_CACHED,
        EventType.AGENT_CACHE_HIT,
        EventType.AGENT_CACHE_MISS,
        EventType.AGENT_ERROR,
        EventType.AGENT_RETRY,
        EventType.AGENT_SKIPPED,
        EventType.AGENT_DEPRECATED,
        EventType.AGENT_UPDATED,
    ],
    "skill": [
        EventType.SKILL_GENERATED,
        EventType.SKILL_VALIDATED,
        EventType.SKILL_APPLIED,
        EventType.SKILL_FAILED,
        EventType.SKILL_COMPOSED,
        EventType.SKILL_VERSIONED,
        EventType.SKILL_DEPRECATED,
        EventType.SKILL_COMPATIBILITY_CHECK,
        EventType.SKILL_PARAMETER_OPTIMIZED,
        EventType.SKILL_EFFECTIVENESS_ANALYZED,
        EventType.SKILL_RECOMMENDATION_GENERATED,
        EventType.SKILL_ORCHESTRATION_STARTED,
        EventType.SKILL_ORCHESTRATION_COMPLETED,
        EventType.SKILL_INTERACTION_TRACKED,
    ],
    "quality": [
        EventType.QUALITY_GATE_PASSED,
        EventType.QUALITY_GATE_FAILED,
        EventType.CODE_REVIEWED,
        EventType.CODE_VALIDATED,
        EventType.DESIGN_VALIDATED,
        EventType.ARCHITECTURE_VALIDATED,
        EventType.PERFORMANCE_VALIDATED,
        EventType.SECURITY_VALIDATED,
        EventType.TEST_COVERAGE_ANALYZED,
        EventType.VALIDATION_STARTED,
        EventType.VALIDATION_COMPLETED,
    ],
    "learning": [
        EventType.LEARNING_STARTED,
        EventType.LEARNING_COMPLETED,
        EventType.FEEDBACK_RECORDED,
        EventType.FEEDBACK_ANALYZED,
        EventType.PATTERN_DETECTED,
        EventType.BEHAVIOR_ANALYZED,
        EventType.RECOMMENDATION_GENERATED,
        EventType.EFFECTIVENESS_CALCULATED,
        EventType.USER_INTERACTION,
        EventType.QUESTION_ANSWERED,
        EventType.KNOWLEDGE_UPDATED,
        EventType.LEARNING_GOAL_ACHIEVED,
    ],
    "conflict": [
        EventType.CONFLICT_DETECTED,
        EventType.CONFLICT_ANALYZED,
        EventType.CONFLICT_RESOLVED,
        EventType.CONFLICT_ESCALATED,
        EventType.CONSENSUS_REACHED,
        EventType.CONSENSUS_FAILED,
        EventType.DECISION_MADE,
        EventType.RESOLUTION_APPROVED,
    ],
    "knowledge": [
        EventType.KNOWLEDGE_INDEXED,
        EventType.KNOWLEDGE_RETRIEVED,
        EventType.KNOWLEDGE_UPDATED,
        EventType.KNOWLEDGE_DELETED,
        EventType.CONTEXT_ANALYZED,
        EventType.CONTEXT_ENRICHED,
        EventType.DOCUMENT_PROCESSED,
        EventType.DOCUMENT_ANALYZED,
        EventType.SEMANTIC_SEARCH_PERFORMED,
        EventType.KNOWLEDGE_GRAPH_UPDATED,
    ],
    "performance": [
        EventType.PERFORMANCE_METRIC_RECORDED,
        EventType.LATENCY_THRESHOLD_EXCEEDED,
        EventType.TOKEN_LIMIT_APPROACHING,
        EventType.TOKEN_LIMIT_EXCEEDED,
        EventType.COST_THRESHOLD_EXCEEDED,
        EventType.RESOURCE_USAGE_HIGH,
        EventType.HEALTH_CHECK_PASSED,
        EventType.HEALTH_CHECK_FAILED,
        EventType.BOTTLENECK_DETECTED,
        EventType.OPTIMIZATION_OPPORTUNITY,
        EventType.MONITORING_ALERT,
    ],
    "data": [
        EventType.DATA_SAVED,
        EventType.DATA_LOADED,
        EventType.DATA_VALIDATED,
        EventType.DATA_TRANSFORMED,
        EventType.DATABASE_ERROR,
        EventType.CACHE_UPDATED,
        EventType.BACKUP_CREATED,
        EventType.RECOVERY_STARTED,
    ],
    "user": [
        EventType.USER_AUTHENTICATED,
        EventType.USER_SESSION_STARTED,
        EventType.USER_SESSION_ENDED,
        EventType.USER_PREFERENCE_CHANGED,
        EventType.USER_ROLE_CHANGED,
        EventType.PERMISSION_GRANTED,
        EventType.PERMISSION_DENIED,
    ],
    "error": [
        EventType.ERROR_OCCURRED,
        EventType.ERROR_RECOVERED,
        EventType.FATAL_ERROR,
        EventType.RETRY_SCHEDULED,
        EventType.RETRY_EXCEEDED,
        EventType.FALLBACK_TRIGGERED,
    ],
    "coordination": [
        EventType.WORKFLOW_COORDINATION,
        EventType.MULTI_AGENT_SYNC,
        EventType.ORCHESTRATION_COMPLETE,
    ],
}


class EventBus:
    """Simple in-memory event bus for emitting and subscribing to events."""

    def __init__(self):
        """Initialize event bus with subscriber tracking."""
        self.subscribers = {}

    def subscribe(self, event_type: EventType, callback):
        """
        Subscribe to an event type.

        Args:
            event_type: EventType to subscribe to
            callback: Callable to invoke when event is emitted
        """
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: EventType, callback):
        """
        Unsubscribe from an event type.

        Args:
            event_type: EventType to unsubscribe from
            callback: Callable to remove
        """
        if event_type in self.subscribers:
            self.subscribers[event_type] = [
                cb for cb in self.subscribers[event_type] if cb != callback
            ]

    def emit(self, event_type: EventType, data=None):
        """
        Emit an event to all subscribers.

        Args:
            event_type: EventType to emit
            data: Optional event data
        """
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                try:
                    callback(event_type, data)
                except Exception as e:
                    # Log error but don't fail event emission
                    print(f"Error in event callback for {event_type}: {e}")

    def subscribe_category(self, category: str, callback):
        """
        Subscribe to all events in a category.

        Args:
            category: Category name (from EVENT_CATEGORIES)
            callback: Callable to invoke for category events
        """
        if category in EVENT_CATEGORIES:
            for event_type in EVENT_CATEGORIES[category]:
                self.subscribe(event_type, callback)

    def unsubscribe_category(self, category: str, callback):
        """
        Unsubscribe from all events in a category.

        Args:
            category: Category name (from EVENT_CATEGORIES)
            callback: Callable to remove
        """
        if category in EVENT_CATEGORIES:
            for event_type in EVENT_CATEGORIES[category]:
                self.unsubscribe(event_type, callback)
