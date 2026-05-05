# Service Injection Architecture

## Overview

The Socratic Agents library now supports **service injection** for decoupling agents from the orchestrator. This enables:

1. **Distributed Use**: Agents work independently without requiring a local orchestrator
2. **Testability**: Easy to mock services for unit testing
3. **Flexibility**: Services can be implemented for different backends (local, API, cloud)
4. **Backward Compatibility**: Existing orchestrator-based code continues to work

## Architecture

### Service Interfaces

All agents depend on abstract service interfaces, not concrete implementations:

```
┌─────────────────┐
│   Agent         │
└────────┬────────┘
         │ depends on
         ├─ DatabaseService
         ├─ LLMService
         ├─ VectorDatabaseService
         ├─ ConfigService
         └─ EventEmitterService
```

### Two Initialization Patterns

#### 1. Service Injection (Recommended)

```python
from socratic_agents import ProjectManagerAgent
from socratic_agents.services import (
    OrchestratorDatabaseAdapter,
    OrchestratorLLMAdapter,
    # ... other adapters
)

agent = ProjectManagerAgent(
    name="ProjectManager",
    database=database_service,
    llm=llm_service,
    vector_db=vector_service,
    config=config_service,
    event_emitter=event_service
)

result = agent.process({"action": "create_project", ...})
```

**Advantages**:
- No dependency on orchestrator
- Works in distributed scenarios
- Easy to mock for testing
- Explicit dependency declaration

#### 2. Orchestrator-Based (Legacy, Still Supported)

```python
from socratic_agents import ProjectManagerAgent

agent = ProjectManagerAgent(
    name="ProjectManager",
    orchestrator=orchestrator_instance
)

result = agent.process({"action": "create_project", ...})
```

**Advantages**:
- Backward compatible with existing code
- Requires orchestrator to have database, llm, vector_db, config, event_emitter attributes

## Service Interfaces

### EventEmitterService
Used for emitting and listening to events.

```python
class EventEmitterService(ABC):
    def on(self, event_type: str, callback: Callable) -> None
    def off(self, event_type: str, callback: Callable) -> None
    def emit(self, event_type: str, data: Dict) -> None
```

### DatabaseService
Used for database operations.

```python
class DatabaseService(ABC):
    def load_user(self, user_id: str) -> Optional[User]
    def save_user(self, user: User) -> bool
    def get_project(self, project_id: str) -> Optional[Project]
    def save_project(self, project: Project) -> bool
    def get_project_notes(self, project_id: str) -> List[Note]
    def save_note(self, project_id: str, note: Note) -> bool
    @property
    def db_path(self) -> str
```

### LLMService
Used for LLM operations.

```python
class LLMService(ABC):
    def generate_response(self, prompt: str, context: Optional[str]) -> str
    def generate_artifact(self, context: str, artifact_type: str) -> str
    def generate_documentation(self, project: Project, artifact: Optional[str]) -> str
    def generate_question(self, project: Project, context: Optional[str]) -> str
```

### VectorDatabaseService
Used for vector database operations.

```python
class VectorDatabaseService(ABC):
    def search_similar(self, query: str, top_k: int) -> List[Dict]
    def add_text(self, text: str, metadata: Optional[Dict]) -> bool
    def delete_by_metadata(self, metadata: Dict) -> bool
```

### ConfigService
Used for configuration access.

```python
class ConfigService(ABC):
    @property
    def data_dir(self) -> str

    @property
    def api_key(self) -> Optional[str]

    @property
    def claude_model(self) -> str

    def get(self, key: str, default: Any) -> Any
```

## Creating Custom Service Implementations

Implement the abstract interfaces for your specific backend:

```python
from socratic_agents.services import DatabaseService
import mybackend

class MyDatabaseService(DatabaseService):
    def __init__(self, connection_string: str):
        self.conn = mybackend.connect(connection_string)

    def load_user(self, user_id: str):
        return self.conn.query("SELECT * FROM users WHERE id = ?", user_id)

    # ... implement other methods

    @property
    def db_path(self) -> str:
        return self.conn.path
```

## Using Orchestrator-Based Adapters

The library provides adapters that wrap an orchestrator as services. This allows gradual migration:

```python
from socratic_agents.services import create_service_adapters

# Extract services from orchestrator
services = create_service_adapters(orchestrator)

# Create agent with services
agent = ProjectManagerAgent(
    name="ProjectManager",
    **services  # Unpack all services
)
```

## Migration Path

1. **Existing Code**: Continue using orchestrator-based initialization
2. **New Code**: Use service injection
3. **Gradual Migration**: Replace agents one at a time, using adapters for transitional code
4. **Full Migration**: All agents using service injection

## Testing with Service Injection

```python
from unittest.mock import Mock
from socratic_agents import ProjectManagerAgent

# Create mock services
mock_db = Mock(spec=DatabaseService)
mock_db.get_project.return_value = Project(...)
mock_llm = Mock(spec=LLMService)
mock_llm.generate_response.return_value = "Generated response"

# Create agent with mocks
agent = ProjectManagerAgent(
    name="ProjectManager",
    database=mock_db,
    llm=mock_llm,
    vector_db=Mock(),
    config=Mock(),
    event_emitter=Mock()
)

# Test agent logic
result = agent.process({"action": "analyze_project", ...})
assert result["status"] == "success"
```

## Distributed Architecture

For distributed usage (e.g., via REST API):

```
┌──────────────────┐
│   External       │
│   Client         │
└────────┬─────────┘
         │
         │ REST API
         │
┌────────▼──────────┐
│  API Gateway      │
└────────┬──────────┘
         │
┌────────▼───────────────┐
│ Agent Service         │
│ + Service Impls       │
│ + Orchestrator (local)│
└───────────────────────┘
```

External clients connect via:

```python
from socratic_agents import SocratesAgentClient

client = SocratesAgentClient("http://api.example.com")
result = await client.invoke_agent_async(
    "project_manager",
    action="create_project",
    name="My Project"
)
```

## Best Practices

1. **Always inject services** in new code
2. **Use abstract interfaces** - implement `DatabaseService`, not concrete class
3. **Mock services for testing** - don't require orchestrator in tests
4. **Don't access orchestrator directly** - use injected services
5. **Keep services simple** - each service has one responsibility
