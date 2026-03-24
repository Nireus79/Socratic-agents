# Integration Guide: Adding Modularized Orchestration to Socrates

Step-by-step guide for integrating the Phase 5-7 orchestration system into the main Socrates application.

---

## Prerequisites

- Socrates system installed and running
- Access to the main `AgentOrchestrator` class
- Database connection available
- All 19 socratic-agents imported

---

## Step 1: Install Dependencies

The orchestration layer requires:

```bash
# Already in environment
pip install socrates-maturity  # Phase 1
pip install socratic-agents     # Phases 2-4

# For Phase 5-7 (already included in socratic-agents)
# - PureOrchestrator
# - OrchestratorAdapter
# - MaturityAwareOrchestrator
# - SocratesIntegration
# - WorkflowManager
```

---

## Step 2: Initialize SocratesIntegration

In your Socrates initialization code:

```python
from socratic_system.orchestration import AgentOrchestrator
from src.socratic_agents.orchestration import (
    SocratesIntegration,
    PureOrchestrator,
    MaturityAwareOrchestrator,
)

# Your existing orchestrator
existing_orchestrator = AgentOrchestrator(api_key)

# Initialize integration
database = existing_orchestrator.database
integration = SocratesIntegration(database)

# Create pure orchestrator
agents = {
    "socratic_counselor": existing_orchestrator.socratic_counselor,
    "code_generator": existing_orchestrator.code_generator,
    "code_validator": existing_orchestrator.code_validation_agent,
    # ... all 19 agents
}

pure_orchestrator = PureOrchestrator(
    agents=agents,
    get_maturity=integration.get_user_maturity,
    get_learning_effectiveness=integration.get_agent_effectiveness,
)

# Wrap with maturity awareness
maturity_orchestrator = MaturityAwareOrchestrator(
    existing_orchestrator=existing_orchestrator,
    pure_orchestrator=pure_orchestrator,
    maturity_tracker=integration.get_user_maturity,
)
```

---

## Step 3: Replace Request Processing

### Before (without gating):

```python
response = orchestrator.process_request(
    agent_name="code_generator",
    request={"action": "generate", "code": "..."}
)
```

### After (with maturity gating):

```python
# Option 1: With gating (recommended)
response = maturity_orchestrator.process_request(
    agent_name="code_generator",
    request={"action": "generate", "code": "...", "user_id": "user123"},
    enforce_gating=True
)

if response["status"] == "gated":
    print(f"Request blocked: {response['error']}")
    print(f"Suggestion: {response.get('suggestion')}")
    return

# Option 2: Without gating (backward compatible)
response = maturity_orchestrator.process_request(
    agent_name="code_generator",
    request={"action": "generate", "code": "..."},
    enforce_gating=False  # Skip gating
)
```

---

## Step 4: Implement Workflow Management

### Discovery Phase Workflow

```python
from src.socratic_agents.orchestration import WorkflowManager

manager = WorkflowManager(maturity_orchestrator, integration)

# Start discovery workflow
workflow_id = manager.start_discovery_workflow(
    user_id="user123",
    project_id="proj456",
    project_description="Build a REST API"
)

# Execute workflow steps
success = True
while success:
    success = manager.execute_workflow_step(workflow_id)
    if success:
        print("Completed workflow step...")

# Get results
results = manager.complete_workflow(workflow_id)
print(f"Workflow results: {results}")
```

### Analysis Phase Workflow

```python
workflow_id = manager.start_analysis_workflow(
    user_id="user123",
    project_id="proj456",
    code=user_code
)

while manager.execute_workflow_step(workflow_id):
    pass

results = manager.complete_workflow(workflow_id)
```

---

## Step 5: Track User Maturity

After code analysis or workflow completion, update maturity:

```python
# Get quality assessment
quality_result = orchestrator.quality_controller.detect_weak_areas(code)

# Calculate new maturity
category_scores = quality_result["category_scores"]
overall_maturity = MaturityCalculator.calculate_overall_maturity({
    "discovery": 1.0,
    "analysis": overall_from_scores,
    "design": 0.0,
    "implementation": 0.0,
})

# Update in system
phase_scores = {
    "discovery": 1.0,
    "analysis": overall_from_scores,
    "design": 0.0,
    "implementation": 0.0,
}

integration.update_user_maturity("user123", phase_scores)

# Get recommendations
recommendations = integration.get_recommended_next_steps("user123")
print(f"Next focus: {recommendations['focus_areas']}")
```

---

## Step 6: Record Effectiveness

After agent execution, record how effective it was:

```python
# Execute agent
response = maturity_orchestrator.process_request(
    "code_generator",
    {"action": "generate", "requirements": "..."},
    enforce_gating=True
)

if response["status"] == "success":
    # Record effectiveness
    integration.record_agent_execution(
        user_id="user123",
        agent_name="code_generator",
        action="generate",
        input_data={"requirements": "..."},
        output_data=response,
        effectiveness=0.85,  # 0.0-1.0 score
        duration_ms=250.0
    )
```

---

## Step 7: Apply Skills

When skills are generated, apply them to agents:

```python
from src.socratic_agents.skill_generator import SkillGenerator

# Get quality assessment
weak_areas = quality_result["weak_categories"]
scores = quality_result["category_scores"]
phase = quality_result["phase"]

# Generate skills
skills = SkillGenerator.generate(
    phase=phase,
    weak_categories=weak_areas,
    category_scores=scores,
    learning_velocity="high",
    engagement_score=0.8
)

# Apply skills through orchestrator adapter
from src.socratic_agents.orchestration import OrchestratorAdapter

adapter = OrchestratorAdapter(pure_orchestrator)
applied = adapter.apply_skills(skills, user_id="user123")

print(f"Applied skills to: {list(applied.keys())}")
```

---

## Step 8: Handle Gated Requests

When a request is gated (blocked by maturity):

```python
response = maturity_orchestrator.process_request(
    "code_validator",  # Requires high maturity
    {"action": "validate", "code": "..."},
    enforce_gating=True
)

if response["status"] == "gated":
    # User not ready for this phase
    error = response["error"]  # Detailed reason
    suggestion = response.get("suggestion", "")  # What to do

    # Inform user
    print(f"Cannot execute yet: {error}")
    print(f"Recommendation: {suggestion}")

    # Show what's available now
    phase = integration.get_user_phase("user123")
    available = pure_orchestrator.get_available_agents_for_phase(phase)
    print(f"Available agents: {available}")
```

---

## Step 9: Progressive Migration

You can gradually migrate from the old system:

### Phase 1: Run both in parallel

```python
# Old way (still works)
old_response = existing_orchestrator.process_request(agent_name, request)

# New way (with gating)
new_response = maturity_orchestrator.process_request(
    agent_name,
    request,
    enforce_gating=True
)

# Compare results, verify new way works
```

### Phase 2: Switch to new system with gating disabled

```python
# New system, but gating disabled for compatibility
response = maturity_orchestrator.process_request(
    agent_name,
    request,
    enforce_gating=False  # Behaves like old system
)
```

### Phase 3: Enable gating for new users

```python
# Enable gating only for new users
if user["created_at"] > cutoff_date:
    enforce_gating = True
else:
    enforce_gating = False

response = maturity_orchestrator.process_request(
    agent_name,
    request,
    enforce_gating=enforce_gating
)
```

### Phase 4: Full migration

```python
# All users with gating enabled
response = maturity_orchestrator.process_request(
    agent_name,
    request,
    enforce_gating=True
)
```

---

## Configuration

### Quality Thresholds

Adjust quality requirements per phase:

```python
from src.socratic_agents.orchestration import QUALITY_GATE_THRESHOLDS

# Current thresholds
print(QUALITY_GATE_THRESHOLDS)
# {
#     "discovery": 0.0,
#     "analysis": 0.2,
#     "design": 0.4,
#     "implementation": 0.6,
# }

# To customize, create your own:
CUSTOM_THRESHOLDS = {
    "discovery": 0.0,
    "analysis": 0.1,      # Easier analysis
    "design": 0.3,        # Easier design
    "implementation": 0.5, # Easier implementation
}
```

### Integration Modes

Choose based on your needs:

```python
from src.socratic_agents.orchestration import IntegrationMode

# Pure mode: Full gating (recommended for new systems)
adapter = OrchestratorAdapter(pure_orch, IntegrationMode.PURE)

# Hybrid mode: Optional gating (safe migration)
adapter = OrchestratorAdapter(pure_orch, IntegrationMode.HYBRID)

# Legacy mode: No gating (backward compatible)
adapter = OrchestratorAdapter(pure_orch, IntegrationMode.LEGACY)
```

---

## Event Handling

Listen to coordination events:

```python
from src.socratic_agents.orchestration import CoordinationEvent

def on_coordination_event(event: CoordinationEvent, data: dict):
    if event == CoordinationEvent.PHASE_GATE_PASSED:
        print(f"Agent execution allowed: {data['agent']}")
    elif event == CoordinationEvent.PHASE_GATE_FAILED:
        print(f"Agent blocked: {data['agent']} - {data['reason']}")
    elif event == CoordinationEvent.SKILLS_APPLIED:
        print(f"Skills applied to {data['agents_affected']}")
    elif event == CoordinationEvent.FEEDBACK_RECORDED:
        print(f"Effectiveness recorded: {data['effectiveness']}")

pure_orchestrator = PureOrchestrator(
    agents=agents,
    get_maturity=...,
    get_learning_effectiveness=...,
    on_event=on_coordination_event  # Handle all events
)
```

---

## Troubleshooting

### Issue: All requests getting gated

**Cause**: User maturity not being updated

**Solution**:
```python
# Make sure to update maturity after workflows
integration.update_user_maturity(user_id, phase_scores)

# Verify maturity is updating
maturity = integration.get_user_maturity(user_id)
phase = integration.get_user_phase(user_id)
print(f"User maturity: {maturity:.0%}, Phase: {phase}")
```

### Issue: Agents not available in phase

**Cause**: Phase not matching agent gates

**Solution**:
```python
# Check what's available
phase = integration.get_user_phase(user_id)
available = pure_orchestrator.get_available_agents_for_phase(phase)
print(f"Available in {phase}: {available}")

# Check agent gates
phase_gates = pure_orchestrator._get_phase_gates("agent_name")
print(f"Agent available in: {phase_gates}")
```

### Issue: Skills not applying

**Cause**: Agent doesn't have `apply_skill` method

**Solution**:
```python
# Verify agent supports skills
agent = agents["agent_name"]
if hasattr(agent, "apply_skill"):
    print("Agent supports skills")
else:
    print("Agent doesn't support skills (expected for some agents)")
```

---

## Performance Optimization

### 1. Cache Maturity Scores

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_cached_maturity(user_id: str, phase: str) -> float:
    return integration.get_user_maturity(user_id, phase)

pure_orchestrator = PureOrchestrator(
    agents=agents,
    get_maturity=get_cached_maturity,
    get_learning_effectiveness=...,
)
```

### 2. Batch Record Executions

```python
# Instead of recording each execution individually:
batch = []
for agent_name, result in workflow_results.items():
    batch.append({
        "agent": agent_name,
        "effectiveness": calculate_effectiveness(result),
    })

# Record in batch
for item in batch:
    integration.record_agent_execution(
        user_id,
        item["agent"],
        "workflow",
        {},
        result,
        item["effectiveness"]
    )
```

### 3. Use Lazy Loading

The adapter caches agents:

```python
# First call: loads agent
response = adapter.execute_with_gating(...)

# Subsequent calls: uses cached agent (fast)
response = adapter.execute_with_gating(...)
```

---

## Best Practices

1. **Always update maturity after workflows**
   - Users can't progress without updates
   - Updates trigger phase changes

2. **Record effectiveness scores**
   - Enables learning and skill refinement
   - Tracks agent performance

3. **Handle gated requests gracefully**
   - Show reason to user
   - Provide next steps
   - Offer available alternatives

4. **Use workflows for complex sequences**
   - Coordinates multiple agents
   - Handles gating automatically
   - Aggregates results

5. **Start with gating disabled**
   - Migrate gradually
   - Verify new system works
   - Enable for new users first

---

## Complete Integration Example

See `INTEGRATION_EXAMPLE.md` for a complete working example.

---

## Support

For issues or questions:
1. Check API_REFERENCE.md for detailed API docs
2. Check ARCHITECTURE.md for system design
3. See test files for usage examples
4. Review TROUBLESHOOTING.md for common issues
