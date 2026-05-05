# Agent Refactoring Template

This document defines the standard pattern for refactoring agents to be independent.

## Pattern: From Orchestrator Coupling to Service Injection

### Import Changes
```python
# BEFORE:
from socratic_system.database.X import Y
from socratic_system.utils.Z import W
from socratic_system.models import ProjectContext

# AFTER:
from .interfaces import DatabaseService, LLMService, FileSystemService, AuthService
from typing import Optional, Any, Dict

# ProjectContext and other models passed as data (Dict), not imported
```

### Constructor Changes
```python
# BEFORE:
def __init__(self, orchestrator: "AgentOrchestrator"):
    super().__init__("AgentName", orchestrator)
    self.orchestrator = orchestrator

# AFTER:
def __init__(
    self,
    name: str = "AgentName",
    database_service: Optional[DatabaseService] = None,
    llm_service: Optional[LLMService] = None,
    file_service: Optional[FileSystemService] = None,
    auth_service: Optional[AuthService] = None,
    agent_bus: Optional[Any] = None,
):
    super().__init__(name, agent_bus)
    self.database_service = database_service
    self.llm_service = llm_service
    self.file_service = file_service
    self.auth_service = auth_service
```

### Method Changes
```python
# BEFORE:
self.orchestrator.database.save_project(...)
self.orchestrator.claude_client.generate(...)
self.orchestrator.process_request("other_agent", data)

# AFTER:
await self.database_service.save_project(...)
await self.llm_service.generate(...)
await self.agent_bus.send_request("other_agent", data)
```

### Async Pattern
```python
# Make all methods async
def process(self, request) -> Dict:
    # BEFORE

# AFTER
async def process(self, request) -> Dict:
```

## Service Validation
Always check services are configured:
```python
if not self.llm_service:
    return {"status": "error", "message": "LLM service not configured"}
```

## Data Models
Pass ProjectContext as Dict instead of importing model:
```python
# BEFORE:
from socratic_system.models import ProjectContext
project: ProjectContext = ...

# AFTER:
project: Dict[str, Any] = ...  # Contains project_id, name, specs, etc.
```
