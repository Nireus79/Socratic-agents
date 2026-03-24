# API Reference: Complete Socrates Orchestration System

Complete API documentation for Phases 1-7 modularization.

---

## Phase 1: MaturityCalculator API

**Module**: `socrates_maturity.MaturityCalculator`

### Static Methods

#### `calculate_overall_maturity(phase_scores: Dict[str, float]) -> float`

Calculates overall maturity from phase scores.

**Parameters**:
- `phase_scores`: Dict mapping phase names to scores (0.0-1.0)

**Returns**: Overall maturity score (0.0-1.0)

**Example**:
```python
from socrates_maturity import MaturityCalculator

scores = {
    "discovery": 1.0,
    "analysis": 0.8,
    "design": 0.6,
    "implementation": 0.0,
}
maturity = MaturityCalculator.calculate_overall_maturity(scores)
# Returns: 0.8 (average of non-zero phases)
```

**Notes**:
- Only averages non-zero phases
- Ranges from 0.0 (no progress) to 1.0 (complete)

---

#### `estimate_current_phase(overall_maturity: float) -> str`

Estimates current maturity phase from overall maturity score.

**Parameters**:
- `overall_maturity`: Overall maturity score (0.0-1.0)

**Returns**: Phase name ("discovery", "analysis", "design", or "implementation")

**Ranges**:
- 0.0-0.25: discovery
- 0.25-0.50: analysis
- 0.50-0.75: design
- 0.75-1.0: implementation

**Example**:
```python
phase = MaturityCalculator.estimate_current_phase(0.6)
# Returns: "design"
```

---

#### `identify_weak_categories(category_scores: Dict[str, float]) -> List[str]`

Identifies weak categories (score < 0.6).

**Parameters**:
- `category_scores`: Dict mapping category names to scores (0.0-1.0)

**Returns**: List of weak category names

**Example**:
```python
scores = {
    "functional_requirements": 0.4,  # Weak
    "testing": 0.3,                   # Weak
    "documentation": 0.8,             # Strong
}
weak = MaturityCalculator.identify_weak_categories(scores)
# Returns: ["functional_requirements", "testing"]
```

---

#### `calculate_category_improvement(before: Dict, after: Dict) -> Dict[str, float]`

Calculates improvement in each category.

**Parameters**:
- `before`: Category scores before
- `after`: Category scores after

**Returns**: Dict mapping categories to improvement amounts

**Example**:
```python
before = {"testing": 0.3, "code_quality": 0.4}
after = {"testing": 0.6, "code_quality": 0.7}
improvement = MaturityCalculator.calculate_category_improvement(before, after)
# Returns: {"testing": 0.3, "code_quality": 0.3}
```

---

## Phase 5: PureOrchestrator API

**Module**: `src.socratic_agents.orchestration.PureOrchestrator`

### Constructor

```python
PureOrchestrator(
    agents: Dict[str, Any],
    get_maturity: Callable[[str, str], float],
    get_learning_effectiveness: Callable[[str], float],
    on_event: Optional[Callable[[CoordinationEvent, Dict], None]] = None,
)
```

**Parameters**:
- `agents`: Dict mapping agent names to agent instances
- `get_maturity`: Function that returns maturity for (user_id, phase)
- `get_learning_effectiveness`: Function that returns effectiveness for agent
- `on_event`: Optional callback for coordination events

---

### Methods

#### `can_execute_request(agent_name: str, current_phase: str, current_maturity: float) -> Tuple[bool, Optional[str]]`

Checks if request can execute based on maturity gating.

**Returns**: (can_execute, reason_if_blocked)

**Example**:
```python
can_execute, reason = orchestrator.can_execute_request(
    agent_name="code_validator",
    current_phase="implementation",
    current_maturity=0.8
)

if not can_execute:
    print(f"Request blocked: {reason}")
```

---

#### `execute_request(request: AgentRequest, current_maturity: float, current_phase: str) -> AgentResponse`

Executes agent request with maturity-driven gating.

**Example**:
```python
from src.socratic_agents.orchestration import AgentRequest

request = AgentRequest(
    agent_name="code_generator",
    action="generate",
    data={"requirements": "..."},
    user_id="user123",
)

response = orchestrator.execute_request(
    request,
    current_maturity=0.6,
    current_phase="design"
)

print(f"Status: {response.status}")
print(f"Gated: {response.gated}")
```

---

#### `apply_skills_to_agents(skills: List, agents_state: Dict) -> Dict[str, List[str]]`

Applies skills to target agents.

**Returns**: Dict mapping agent names to list of applied skill IDs

**Example**:
```python
skills = [AgentSkill(...), AgentSkill(...)]
applied = orchestrator.apply_skills_to_agents(skills, orchestrator.agents)

for agent_name, skill_ids in applied.items():
    print(f"{agent_name}: {len(skill_ids)} skills applied")
```

---

#### `record_feedback(agent_name: str, action: str, effectiveness: float, user_id: str) -> bool`

Records feedback about agent execution effectiveness.

**Example**:
```python
success = orchestrator.record_feedback(
    agent_name="code_generator",
    action="generate",
    effectiveness=0.85,
    user_id="user123"
)
```

---

#### `start_workflow(workflow_id: str, initial_data: Dict) -> str`

Starts a new multi-agent workflow.

**Example**:
```python
wf_id = orchestrator.start_workflow(
    "wf_123",
    {"project": "my_project", "user": "user123"}
)
```

---

#### `execute_workflow_step(workflow_id: str, request: AgentRequest) -> AgentResponse`

Executes a step in a workflow.

---

#### `complete_workflow(workflow_id: str) -> Dict[str, Any]`

Completes a workflow and returns results.

---

#### `get_available_agents_for_phase(phase: str) -> List[str]`

Gets agents available in a specific phase.

**Example**:
```python
agents = orchestrator.get_available_agents_for_phase("discovery")
# Returns: ["socratic_counselor", "context_analyzer", "knowledge_manager"]
```

---

#### `estimate_phase(maturity: float) -> str`

Estimates phase from maturity score.

---

## Phase 6: Integration API

### OrchestratorAdapter

**Module**: `src.socratic_agents.orchestration.OrchestratorAdapter`

#### `execute_with_gating(agent_name, action, data, user_id, current_maturity, current_phase) -> Dict`

Executes request with maturity gating.

**Example**:
```python
from src.socratic_agents.orchestration import OrchestratorAdapter, IntegrationMode

adapter = OrchestratorAdapter(
    pure_orchestrator,
    mode=IntegrationMode.HYBRID
)

response = adapter.execute_with_gating(
    agent_name="code_generator",
    action="generate",
    data={"requirements": "..."},
    user_id="user123",
    current_maturity=0.6
)

if response["status"] == "gated":
    print(f"Blocked: {response['error']}")
    print(f"Suggestion: {response['suggestion']}")
```

---

#### `apply_skills(skills, user_id) -> Dict`

Applies skills to agents.

---

#### `record_effectiveness(agent_name, action, effectiveness, user_id) -> bool`

Records effectiveness feedback.

---

#### `get_agent_availability(current_phase, current_maturity) -> Dict`

Gets available agents and thresholds.

**Returns**:
```python
{
    "phase": "design",
    "maturity": 0.6,
    "quality_threshold": 0.4,
    "available_agents": ["code_generator", "quality_controller"],
    "can_execute": True,
    "agents_count": 2,
}
```

---

### MaturityAwareOrchestrator

**Module**: `src.socratic_agents.orchestration.MaturityAwareOrchestrator`

#### `process_request(agent_name, request, enforce_gating=True) -> Dict`

Processes request with optional gating.

**Example**:
```python
from src.socratic_agents.orchestration import MaturityAwareOrchestrator

wrapper = MaturityAwareOrchestrator(
    existing_orchestrator,
    pure_orchestrator,
    maturity_tracker=get_user_maturity
)

# With gating
response = wrapper.process_request(
    "code_generator",
    {"action": "generate", "user_id": "user123"},
    enforce_gating=True
)

# Without gating (backward compatible)
response = wrapper.process_request(
    "code_generator",
    {"action": "generate", "user_id": "user123"},
    enforce_gating=False
)
```

---

#### `get_stats() -> Dict`

Gets orchestration statistics.

**Returns**:
```python
{
    "total_requests": 100,
    "gated_requests": 15,
    "pass_rate": 0.85,
    "skills_applied": 42,
}
```

---

## Phase 7: System Integration API

### SocratesIntegration

**Module**: `src.socratic_agents.orchestration.SocratesIntegration`

#### `get_user_maturity(user_id: str, phase: Optional[str]) -> float`

Gets user maturity score.

**Example**:
```python
from src.socratic_agents.orchestration import SocratesIntegration

integration = SocratesIntegration(database)

# Overall maturity
overall = integration.get_user_maturity("user123")

# Phase-specific maturity
phase_maturity = integration.get_user_maturity("user123", "analysis")
```

---

#### `get_user_phase(user_id: str) -> str`

Gets user's current phase.

**Example**:
```python
phase = integration.get_user_phase("user123")
# Returns: "design"
```

---

#### `record_agent_execution(user_id, agent_name, action, input_data, output_data, effectiveness, duration_ms) -> bool`

Records agent execution for learning.

**Example**:
```python
success = integration.record_agent_execution(
    user_id="user123",
    agent_name="code_generator",
    action="generate",
    input_data={"requirements": "..."},
    output_data={"code": "def hello(): pass"},
    effectiveness=0.85,
    duration_ms=250.0
)
```

---

#### `update_user_maturity(user_id, phase_scores) -> bool`

Updates user maturity scores.

**Example**:
```python
success = integration.update_user_maturity("user123", {
    "discovery": 1.0,
    "analysis": 0.8,
    "design": 0.6,
    "implementation": 0.0,
})
```

---

#### `get_recommended_next_steps(user_id) -> Dict`

Gets phase-specific recommendations.

**Returns**:
```python
{
    "current_phase": "design",
    "current_maturity": "60%",
    "next_phase": "implementation",
    "maturity_to_next_phase": "75%",
    "focus_areas": ["Code quality", "Testing coverage"],
    "available_agents": ["CodeGenerator", "QualityController"],
}
```

---

#### `create_maturity_aware_orchestrator(existing_orchestrator, pure_orchestrator) -> MaturityAwareOrchestrator`

Creates maturity-aware wrapper.

---

### WorkflowManager

**Module**: `src.socratic_agents.orchestration.WorkflowManager`

#### `start_discovery_workflow(user_id, project_id, project_description) -> str`

Starts discovery phase workflow.

**Example**:
```python
from src.socratic_agents.orchestration import WorkflowManager

manager = WorkflowManager(orchestrator, integration)

wf_id = manager.start_discovery_workflow(
    user_id="user123",
    project_id="proj456",
    project_description="Build a web application"
)
```

---

#### `start_analysis_workflow(user_id, project_id, code) -> str`

Starts analysis phase workflow.

---

#### `execute_workflow_step(workflow_id) -> bool`

Executes next step in workflow.

**Returns**: True if step executed, False if complete

**Example**:
```python
while manager.execute_workflow_step(wf_id):
    print("Executing workflow step...")

print("Workflow complete")
```

---

#### `complete_workflow(workflow_id) -> Dict`

Completes workflow and returns results.

**Returns**:
```python
{
    "workflow_id": "wf_123",
    "phase": "discovery",
    "completed_steps": 2,
    "results": {
        "socratic_counselor": {...},
        "context_analyzer": {...},
    }
}
```

---

## Enums and Constants

### CoordinationEvent

```python
class CoordinationEvent(Enum):
    WORKFLOW_STARTED = "workflow_started"
    PHASE_GATING_CHECK = "phase_gating_check"
    PHASE_GATE_PASSED = "phase_gate_passed"
    PHASE_GATE_FAILED = "phase_gate_failed"
    SKILLS_GENERATED = "skills_generated"
    SKILLS_APPLIED = "skills_applied"
    AGENT_EXECUTED = "agent_executed"
    FEEDBACK_RECORDED = "feedback_recorded"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"
```

---

### IntegrationMode

```python
class IntegrationMode(Enum):
    PURE = "pure"        # Full gating enforcement
    HYBRID = "hybrid"    # Optional gating
    LEGACY = "legacy"    # No gating (backward compatible)
```

---

### QUALITY_GATE_THRESHOLDS

```python
QUALITY_GATE_THRESHOLDS = {
    "discovery": 0.0,           # No quality bar
    "analysis": 0.2,            # Very low bar
    "design": 0.4,              # Moderate bar
    "implementation": 0.6,      # High bar
}
```

---

## Data Classes

### AgentRequest

```python
@dataclass
class AgentRequest:
    agent_name: str
    action: str
    data: Dict[str, Any]
    workflow_id: Optional[str] = None
    user_id: Optional[str] = None
```

---

### AgentResponse

```python
@dataclass
class AgentResponse:
    status: str  # "success", "error", "gated"
    agent: str
    action: str
    data: Dict[str, Any]
    gated: bool = False
    gating_reason: Optional[str] = None
```

---

## Error Handling

All API methods handle errors gracefully:

```python
try:
    response = orchestrator.execute_request(request)
    if response.gated:
        print(f"Request gated: {response.gating_reason}")
    elif response.status == "error":
        print(f"Error: {response.data.get('error')}")
    else:
        print(f"Success: {response.data}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Complete Example

```python
from socrates_maturity import MaturityCalculator
from src.socratic_agents.orchestration import (
    PureOrchestrator,
    SocratesIntegration,
    WorkflowManager,
)

# Initialize components
database = load_database()
integration = SocratesIntegration(database)

# Get user state
user_id = "user123"
maturity = integration.get_user_maturity(user_id)
phase = integration.get_user_phase(user_id)
recommendations = integration.get_recommended_next_steps(user_id)

# Create orchestrators
orchestrator = create_orchestrator()
manager = WorkflowManager(orchestrator, integration)

# Start workflow
if phase == "discovery":
    wf_id = manager.start_discovery_workflow(
        user_id, "proj123", "Build a calculator"
    )
elif phase == "analysis":
    wf_id = manager.start_analysis_workflow(
        user_id, "proj123", "def add(a,b): return a+b"
    )

# Execute workflow
while manager.execute_workflow_step(wf_id):
    pass

# Get results
results = manager.complete_workflow(wf_id)

# Record effectiveness
for agent_name, result in results["results"].items():
    integration.record_agent_execution(
        user_id=user_id,
        agent_name=agent_name,
        action="workflow_step",
        input_data={},
        output_data=result,
        effectiveness=0.85
    )
```

---

## API Version

Current version: **7.0.0**

Covers all phases of modularization (Phases 1-7).
