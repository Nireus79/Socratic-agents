"""
Services module for Socrates AI.

Provides:
1. Abstract service interfaces for dependency injection
2. Service adapters for orchestrator backward compatibility
3. Specialized services (document understanding, orchestration)

All agents can be initialized with either:
- Individual services (recommended for new code)
- Orchestrator instance (backward compatible)
"""

# Abstract service interfaces
from socratic_agents.services.base import (
    ConfigService,
    DatabaseService,
    EventEmitterService,
    LLMService,
    ServiceRegistry,
    VectorDatabaseService,
)

# Service adapters (wrap orchestrator for compatibility)
from socratic_agents.services.adapters import (
    OrchestratorConfigAdapter,
    OrchestratorDatabaseAdapter,
    OrchestratorEventEmitterAdapter,
    OrchestratorLLMAdapter,
    OrchestratorVectorDBAdapter,
    create_service_adapters,
)

# Specialized services
from socratic_agents.services.document_understanding import DocumentUnderstandingService
from socratic_agents.services.orchestrator_service import (
    OrchestratorService,
    get_orchestrator_service,
)

__all__ = [
    # Abstract service interfaces
    "EventEmitterService",
    "DatabaseService",
    "LLMService",
    "VectorDatabaseService",
    "ConfigService",
    "ServiceRegistry",
    # Service adapters
    "OrchestratorEventEmitterAdapter",
    "OrchestratorDatabaseAdapter",
    "OrchestratorLLMAdapter",
    "OrchestratorVectorDBAdapter",
    "OrchestratorConfigAdapter",
    "create_service_adapters",
    # Specialized services
    "DocumentUnderstandingService",
    "OrchestratorService",
    "get_orchestrator_service",
]
