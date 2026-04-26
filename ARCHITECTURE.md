# Socratic Agents Architecture

**Status: Socrates-Integrated (v0.1.0)**
**Target: Post-redesign independent agents (v1.0+)**

---

## Overview

Socratic Agents is a collection of 19+ specialized agents designed to operate within the Socrates monolith. The agents work together through a centralized orchestrator to handle complex AI workflows.

⚠️ **Important**: This library is tightly coupled to Socrates internals. It is NOT designed for standalone use.

---

## Design Principles

### 1. Socrates-First Architecture

All agents are built with the assumption that Socrates systems are available:
- Centralized database
- Shared vector database
- Unified LLM client
- Shared user/project context
- Event system

### 2. Orchestration-Based

Agents don't directly manage resources. Instead:
- **AgentOrchestrator** manages all external dependencies
- Agents receive orchestrator instance
- All system access goes through orchestrator
- This enables future separation of concerns

### 3. Event-Driven

Agents emit events for monitoring and integration:
- State changes
- Action completions
- Errors and warnings
- Progress updates

---

## Component Hierarchy

```
AgentOrchestrator (Central Hub)
├── Database Connection (socratic_system)
├── Vector Database (socratic_system)
├── Claude Client (Multi-provider)
├── Event System
└── Agent Pool
    ├── SocraticCounselorAgent
    ├── ProjectManagerAgent
    ├── QualityControllerAgent
    ├── CodeGeneratorAgent
    ├── UserLearningAgent
    ├── ConflictDetectorAgent
    └── ... (13+ more agents)
```

---

## Agent Categories

### Tier 1: Core Dialogue Agents
**Purpose**: Guide users and orchestrate main workflows

- **SocraticCounselorAgent** - Main dialogue engine
  - Generates Socratic questions
  - Processes user responses
  - Extracts insights
  - Tracks conversation history
  - Coordinates with other agents

- **QuestionQueueAgent** - Question management
  - Manages question queues
  - Prioritizes questions
  - Tracks answered/pending

### Tier 2: Project & Coordination Agents
**Purpose**: Manage project lifecycle and quality

- **ProjectManagerAgent** - Project operations
  - Create/load/save projects
  - Manage collaborators
  - Handle archival
  - Manage team roles

- **QualityControllerAgent** - Quality assurance
  - Track maturity
  - Manage approval workflows
  - Calculate metrics
  - Generate quality reports

### Tier 3: Technical Agents
**Purpose**: Handle code and technical tasks

- **CodeGeneratorAgent** - Code generation
  - Generates artifacts
  - Handles documentation
  - Manages multi-file projects

- **CodeValidationAgent** - Code validation
  - Syntax checking
  - Quality metrics
  - Test execution

- **DocumentProcessorAgent** - Document handling
  - File import
  - Content extraction
  - Vector database storage

### Tier 4: Learning & Analysis Agents
**Purpose**: Learn from interactions and analyze

- **UserLearningAgent** - User behavior learning
  - Tracks question effectiveness
  - Learns behavior patterns
  - Recommends questions
  - Manages knowledge documents

- **ConflictDetectorAgent** - Conflict detection
  - Detects specification conflicts
  - Proposes resolutions
  - Manages conflict tracking

- **KnowledgeManagerAgent** - Knowledge enrichment
  - Manages knowledge suggestions
  - Reviews user knowledge
  - Exports/imports knowledge

### Tier 5: Support Agents
**Purpose**: Provide system support

- **SystemMonitorAgent** - System health
  - Token usage tracking
  - Health checks
  - Statistics collection

- **UserManagerAgent** - User management
  - User registration
  - Preference management
  - Account operations

---

## Dependencies

### Internal Dependencies (socratic_system)
```
All Agents
    ↓
AgentOrchestrator
    ↓
    ├── socratic_system.database
    ├── socratic_system.models
    ├── socratic_system.utils
    ├── socratic_system.services
    └── socratic_system.core
```

### External Dependencies
- `pydantic>=2.0.0` - Data validation
- `loguru>=0.7.0` - Logging
- `colorama>=0.4.0` - Terminal colors
- `socratic-maturity>=0.1.0` - Maturity models

### Framework Integrations (Optional)
- `langchain>=0.1.0` - LangChain tools
- `langgraph>=0.0.1` - LangGraph integration
- `openclaw` - Openclaw skills

---

## Agent Lifecycle

### Initialization
```python
from socratic_agents import AgentOrchestrator, SpecificAgent

orchestrator = AgentOrchestrator(
    database=socrates_db,
    vector_db=socrates_vector_db,
    claude_client=socrates_llm_client
)
agent = SpecificAgent(orchestrator)
```

### Processing
```python
request = {
    "action": "specific_action",
    "param1": value1,
    # ... agent-specific parameters
}
result = agent.process(request)
```

### Output Format
```python
{
    "status": "success" | "error",
    "result": result_data,
    "errors": [error_list],
    "metadata": {
        "execution_time": float,
        "tokens_used": int,
        # ... agent-specific metadata
    }
}
```

---

## Communication Between Agents

### Direct Communication (via Orchestrator)
```python
# Agent A calls Agent B through orchestrator
result = self.orchestrator.process_request("agent_name", request)
```

### Event-Based Communication
```python
# Agent emits event
self.emit_event(EventType.ACTION_COMPLETED, data)

# Other agents listen for events
@event_listener(EventType.ACTION_COMPLETED)
def on_action_completed(event):
    # Handle event
```

### Shared Context
```python
# All agents access context through orchestrator
project = self.orchestrator.load_project(project_id)
user = self.orchestrator.load_user(user_id)
```

---

## Error Handling

All agents follow consistent error handling patterns:

1. **Input Validation** - Validate request parameters
2. **Try-Except** - Graceful error catching
3. **Logging** - Detailed error logging
4. **Status Return** - Include error in response
5. **Cleanup** - Resource cleanup in finally blocks

---

## Async Support

Agents support both sync and async operations:

```python
# Synchronous
result = agent.process(request)

# Asynchronous
result = await agent.process_async(request)
```

---

## Testing Strategy

### Unit Tests
- Test individual agent logic
- Mock orchestrator
- No external dependencies required
- Run with pytest

### Integration Tests
- Test with Socrates systems
- Requires Socrates environment
- Full workflow testing
- Database operations

### Test Markers
```bash
pytest -m unit           # Unit tests only
pytest -m integration    # Integration tests only
pytest -m "not slow"     # Skip slow tests
```

---

## Monitoring & Observability

### Logging
- Agent lifecycle events
- Action execution
- Errors and warnings
- Performance metrics

### Event Emission
- Real-time status updates
- Progress tracking
- Integration hooks
- Audit trail

---

## Future: Post-Redesign (v1.0+)

After Socrates architecture redesign:

### Phase 1: Decouple Internal Dependencies
- Define clear interfaces
- Enable dependency injection
- Reduce tight coupling
- Enable testing without Socrates

### Phase 2: Extract Independent Agents
Some agents will become modular packages:
- Core logic extracted
- Minimal external dependencies
- Published as separate PyPI packages
- Examples:
  - `socratic-counselor` - Dialogue agent
  - `socratic-code-generator` - Code generation
  - `socratic-quality` - Quality assurance

### Phase 3: Backward Compatibility
- Provide integration layer
- Support both old and new patterns
- Gradual migration path
- Documentation and examples

---

## Current Status

✅ **Socrates Integration**: Complete
🔄 **Documentation**: In progress
📅 **Modularization Target**: After Socrates redesign
🚀 **Independent Publishing**: Post-redesign v1.0+

---

## See Also

- [README.md](README.md) - Library overview and installation
- [Socratic Ecosystem](https://github.com/Nireus79/Socrates-nexus/blob/main/ECOSYSTEM.md)
- [Socrates Monolith Docs](../Socrates/docs/)

---

**Socratic Agents - Part of the Socrates AI Platform**
