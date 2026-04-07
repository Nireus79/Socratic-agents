# SocraticCounselor Agent

**Core dialogue orchestration engine for Socratic learning interactions.**

## Overview

The SocraticCounselor is the primary agent for implementing Socratic dialogue - a method of teaching through questions that guide learners to discover knowledge themselves. It orchestrates complete dialogue flows, manages question generation, processes responses, and tracks learning progress.

## Key Capabilities

### 1. **Question Generation**
- Dynamic question creation using LLM or static templates
- Phase-aware questions (discovery, analysis, design, implementation)
- Context-aware questions based on project state
- Question deduplication to avoid repetition

### 2. **Response Processing**
- Processes user answers to questions
- Extracts insights from responses
- Automatically generates next questions
- Tracks answer effectiveness

### 3. **Learning Guidance**
- Direct guidance on any topic
- Level-appropriate questions (beginner, intermediate, advanced)
- Contextual learning paths
- Skill-based recommendations

### 4. **Conflict Detection**
- Identifies inconsistencies in specifications
- Detects goal divergence
- Manages resolution strategies

### 5. **State Management**
- Maintains conversation history
- Tracks pending questions
- Stores answered questions
- Manages project phases

## Usage

### Basic: Get a Guiding Question

```python
from socratic_agents import SocraticCounselor

counselor = SocraticCounselor()

# Get a question on a topic
result = counselor.guide("Python recursion", level="beginner")

print(result["question"])  # "What is the base case for recursion?"
print(result["topic"])      # "Python recursion"
print(result["level"])      # "beginner"
```

### Advanced: Full Dialogue Flow

```python
# Create a project context
project = {
    "name": "MyApp",
    "phase": "discovery",
    "conversation_history": [],
    "pending_questions": []
}

# Step 1: Generate initial question
q_result = counselor.process({
    "action": "generate_question",
    "project": project,
    "user_id": "user_1"
})
print("Question:", q_result["question"])

# Step 2: Process user's response
response_result = counselor.process({
    "action": "process_response",
    "project": project,
    "user_id": "user_1",
    "response": "The app should solve task management"
})

# Step 3: Next question is automatically generated
print("Next question:", response_result["next_question"])
```

## Request Format

### action: `generate_question`
Generate the next Socratic question for a project.

```python
request = {
    "action": "generate_question",
    "project": project_context,      # Required
    "user_id": "user_123"             # Required
}
```

**Returns:**
```python
{
    "status": "success",
    "question": "What are the core requirements?",
    "existing": false,                # true if returning existing unanswered question
    "question_id": "q_123"
}
```

### action: `process_response`
Process a user's answer and generate insights.

```python
request = {
    "action": "process_response",
    "project": project_context,       # Required
    "user_id": "user_123",            # Required
    "response": "Users need task lists"  # Required
}
```

**Returns:**
```python
{
    "status": "success",
    "insights": ["User-centric focus", "MVP identified"],
    "next_question": "How will users prioritize tasks?",
    "phase_progress": 0.6
}
```

### action: `guide`
Generate guidance questions on any topic.

```python
request = {
    "action": "guide",
    "topic": "machine learning",      # Required
    "level": "intermediate"           # Optional: beginner|intermediate|advanced
}
```

**Returns:**
```python
{
    "status": "success",
    "question": "What is the difference between supervised and unsupervised learning?",
    "topic": "machine learning",
    "level": "intermediate"
}
```

### action: `extract_insights_only`
Extract insights from text without generating questions.

```python
request = {
    "action": "extract_insights_only",
    "response": "The system needs real-time updates and offline support"
}
```

**Returns:**
```python
{
    "status": "success",
    "insights": ["Real-time requirements", "Offline capability needed"]
}
```

### action: `detect_conflicts`
Detect inconsistencies in specifications.

```python
request = {
    "action": "detect_conflicts",
    "items": ["Minimize latency", "Reduce server costs", "Real-time updates"],
    "agent_states": {
        "agent_1": {"goal": "fast"},
        "agent_2": {"goal": "cheap"}
    }
}
```

**Returns:**
```python
{
    "status": "success",
    "conflicts_found": 1,
    "conflicts": [{"type": "goal_divergence", "severity": "high"}]
}
```

### action: `check_phase_completion`
Determine if current phase is complete.

```python
request = {
    "action": "check_phase_completion",
    "project": project_context
}
```

**Returns:**
```python
{
    "status": "success",
    "phase_complete": true,
    "completion_percentage": 85,
    "next_phase": "analysis"
}
```

### action: `advance_phase`
Move project to next phase.

```python
request = {
    "action": "advance_phase",
    "project": project_context
}
```

**Returns:**
```python
{
    "status": "success",
    "new_phase": "analysis",
    "phase_questions": [...questions for new phase...]
}
```

## Configuration

### Initialization

```python
from socratic_agents import SocraticCounselor

# Minimal setup
counselor = SocraticCounselor()

# With LLM client
from socrates_nexus import LLMClient
llm = LLMClient(provider="anthropic", model="claude-opus")
counselor = SocraticCounselor(llm_client=llm)

# With database persistence
counselor = SocraticCounselor(
    llm_client=llm,
    database=db_client,
    batch_size=3
)
```

### Configuration Options

| Option | Type | Default | Purpose |
|--------|------|---------|---------|
| `llm_client` | LLMClient | None | LLM for dynamic question generation |
| `database` | Database | None | Persistence for state and history |
| `batch_size` | int | 1 | Questions per generation request |
| `use_dynamic_questions` | bool | True | Use LLM or static templates |
| `max_questions_per_phase` | int | 5 | Maximum questions in a phase |

## Static Questions

Default questions by phase (used when LLM unavailable):

### Discovery Phase
- "What specific problem does your project solve?"
- "Who is your target audience or user base?"
- "What are the core features you envision?"
- "Are there similar solutions that exist?"
- "What are your success criteria?"

### Analysis Phase
- "What technical challenges do you anticipate?"
- "What are your performance requirements?"
- "How will you handle user authentication?"
- "What third-party integrations do you need?"
- "How will you test and validate?"

### Design Phase
- "How will you structure the architecture?"
- "What design patterns will you use?"
- "How will you organize code and modules?"
- "What development workflow will you follow?"
- "How will you handle error cases?"

### Implementation Phase
- "What will be your first milestone?"
- "How will you handle deployment and DevOps?"
- "What monitoring and logging will you implement?"
- "How will you document your code?"
- "What's your plan for maintenance?"

## State Management

### Project Context
The agent maintains complete project state:

```python
project = {
    "name": "ProjectName",
    "phase": "discovery",                    # Current phase
    "conversation_history": [],              # All dialogue
    "pending_questions": [],                 # Unanswered questions
    "maturity_scores": {},                   # Phase scores
    "question_effectiveness": []             # Question ratings
}
```

### Pending Questions
Questions await user responses:

```python
{
    "id": "q_123",
    "question": "What is the main purpose?",
    "phase": "discovery",
    "status": "unanswered",                  # unanswered|answered|skipped
    "answer": None,
    "effectiveness_score": null
}
```

## Advanced Features

### Subscription Validation
```python
# Free tier: 5 questions/day
# Pro tier: Unlimited questions

user = {"subscription_tier": "pro"}
can_ask, error = counselor._check_subscription_limit(user)
```

### Hint Generation
```python
request = {
    "action": "generate_hint",
    "question": "What is your target audience?",
    "project": project
}
result = counselor.process(request)
```

### Question Reopen
```python
request = {
    "action": "reopen_question",
    "question_id": "q_123",
    "project": project
}
# User can re-answer previously answered question
```

### Skip Question
```python
request = {
    "action": "skip_question",
    "project": project
}
# Skip current question and move to next
```

## Best Practices

### 1. **Maintain Project Context**
```python
# Store and retrieve project state between interactions
project = load_project_from_database("project_123")
result = counselor.process({
    "action": "generate_question",
    "project": project,
    "user_id": "user_123"
})
save_project_to_database(project)
```

### 2. **Handle Responses Carefully**
```python
# Always check status
if result["status"] == "error":
    print(f"Error: {result['message']}")
    return

# Use insights from responses
insights = result.get("insights", [])
for insight in insights:
    store_requirement(insight)
```

### 3. **Track Effectiveness**
```python
# Rate question usefulness
counselor.process({
    "action": "rate_question",
    "question_id": "q_123",
    "effectiveness_score": 0.9  # 0.0 to 1.0
})
```

### 4. **Use Phases Appropriately**
```python
# Each phase has specific question focus
if project["phase"] == "discovery":
    # Ask about goals and scope
    pass
elif project["phase"] == "design":
    # Ask about architecture and structure
    pass
```

## Integration Examples

### With Learning System
```python
from socratic_agents import SocraticCounselor, LearningAgent

counselor = SocraticCounselor()
learner = LearningAgent()

# Track learning while counseling
for i in range(5):
    q_result = counselor.guide("recursion", level="beginner")

    # Track interaction
    learner.process({
        "action": "track_interaction",
        "user_id": "user_1",
        "topic": "recursion",
        "question": q_result["question"]
    })
```

### With Code Generation
```python
from socratic_agents import SocraticCounselor, CodeGenerator

counselor = SocraticCounselor()
generator = CodeGenerator()

# Generate requirements through dialogue
result = counselor.guide("sorting algorithm")
requirements = extract_requirements(result["question"])

# Then generate code based on discovered requirements
code_result = generator.process({
    "prompt": f"Implement {requirements}"
})
```

### With Quality Control
```python
from socratic_agents import SocraticCounselor, QualityController

counselor = SocraticCounselor()
quality = QualityController()

# Get insights from dialogue
insights = counselor.process({
    "action": "extract_insights_only",
    "response": user_response
})

# Check quality implications
quality_result = quality.process({
    "action": "analyze",
    "insights": insights
})
```

## Common Patterns

### Pattern 1: One-Off Guidance
```python
result = counselor.guide("Python closures", level="intermediate")
print(result["question"])
```

### Pattern 2: Multi-Turn Dialogue
```python
project = create_project("MyApp")

for turn in range(5):
    q_result = counselor.process({
        "action": "generate_question",
        "project": project,
        "user_id": "user_1"
    })

    user_answer = input(q_result["question"] + ": ")

    a_result = counselor.process({
        "action": "process_response",
        "project": project,
        "user_id": "user_1",
        "response": user_answer
    })

    print("Insights:", a_result.get("insights"))
```

### Pattern 3: Async Dialogue
```python
import asyncio

async def dialogue_flow():
    result = await counselor.process_async({
        "action": "generate_question",
        "project": project,
        "user_id": "user_1"
    })
    return result

asyncio.run(dialogue_flow())
```

## Troubleshooting

### No Questions Generated
- Check LLM client is configured: `counselor.llm_client is not None`
- Verify project context is valid
- Check logs for LLM errors

### Same Question Repeated
- Agent avoids repeating questions in same session
- Check `pending_questions` for unanswered questions
- Use `reopen_question` action to retry

### Phase Not Advancing
- Ensure questions are answered: `check_phase_completion`
- Check completion percentage: `result["completion_percentage"]`
- Manually advance with `advance_phase` action

### Performance Issues
- Use static questions (`use_dynamic_questions=False`)
- Batch multiple question generations
- Enable async processing with `process_async()`

## Advanced Configuration

### Custom Static Questions

```python
counselor.static_questions["custom_phase"] = [
    "What is the primary goal?",
    "Who are the stakeholders?"
]

# Then use in guidance
result = counselor.process({
    "action": "generate_question",
    "project": project,
    "phase": "custom_phase"
})
```

### Question Filtering

```python
# Avoid certain question types
counselor.excluded_question_types = ["implementation", "testing"]

result = counselor.guide("topic")  # Won't ask about implementation
```

## Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| Generate Question (static) | <10ms | Uses template |
| Generate Question (LLM) | 1-5s | Calls LLM |
| Process Response | <100ms | Local processing |
| Extract Insights | <500ms | May use LLM |
| Check Completion | <50ms | State calculation |

---

**Related Agents:** LearningAgent, QualityController, KnowledgeManager

**Next:** [CodeGenerator Agent](./code_generator.py.md)
