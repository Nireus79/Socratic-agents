"""
Pure Orchestration + Integration + System Integration (Phases 5-7)

Coordinates agents with maturity-driven workflow gating and feedback loops.

Key components:
- PureOrchestrator: Core coordination logic (Phase 5)
- SkillApplier: Applies skills to agents
- CoordinationEvent: Events emitted during coordination
- OrchestratorAdapter: Adapts pure orchestrator to Socrates infrastructure (Phase 6)
- MaturityAwareOrchestrator: Wraps existing orchestrator with maturity awareness (Phase 6)
- SocratesIntegration: Integration helpers for main Socrates system (Phase 7)
- WorkflowManager: Manages complete multi-agent workflows (Phase 7)
"""

from .agent_orchestrator import AgentOrchestrator
from .integration import (
    IntegrationMode,
    MaturityAwareOrchestrator,
    OrchestratorAdapter,
)
from .orchestrator import (
    MATURITY_PHASE_THRESHOLDS,
    QUALITY_GATE_THRESHOLDS,
    AgentRequest,
    AgentResponse,
    CoordinationEvent,
    PureOrchestrator,
)
from .skill_applier import SkillApplier
from .socrates_integration import (
    SocratesIntegration,
    WorkflowManager,
)

__all__ = [
    "AgentOrchestrator",
    "PureOrchestrator",
    "CoordinationEvent",
    "AgentRequest",
    "AgentResponse",
    "SkillApplier",
    "MATURITY_PHASE_THRESHOLDS",
    "QUALITY_GATE_THRESHOLDS",
    "OrchestratorAdapter",
    "MaturityAwareOrchestrator",
    "IntegrationMode",
    "SocratesIntegration",
    "WorkflowManager",
]
