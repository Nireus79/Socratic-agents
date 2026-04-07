# QuestionQueueAgent

**Question queuing, prioritization, and delivery management.**

## Overview

The QuestionQueueAgent manages a queue of questions with priority-based ordering. It enables questions to be collected, prioritized, and delivered in a controlled manner. This agent is useful when questions need to be batched, prioritized, or delivered asynchronously rather than immediately.

## Key Capabilities

### 1. **Question Queuing**
- Add questions to a managed queue
- Support for priority levels (high, normal, low)
- Automatic priority-based sorting
- Queue size tracking

### 2. **Priority Management**
- Three priority levels: high, normal, low
- Automatic queue reordering based on priority
- High-priority questions delivered first
- Stable ordering within same priority level

### 3. **Question Retrieval**
- Get next question in queue
- Retrieve by question ID
- List entire queue
- Track processed questions

### 4. **Queue Tracking**
- Track queued questions count
- Track processed questions count
- Maintain processing history
- Status monitoring (queued, processed)

## Usage

### Basic: Add a Question

```python
from socratic_agents import QuestionQueueAgent

queue = QuestionQueueAgent()

# Add a normal priority question
result = queue.process({
    "action": "add",
    "question": "What is the main purpose of your project?",
    "priority": "normal"
})

print(f"Question ID: {result['question_id']}")
print(f"Queue size: {result['queue_size']}")
```

### Intermediate: Manage Priorities

```python
# Add high-priority question
high_priority = queue.process({
    "action": "add",
    "question": "What are critical requirements?",
    "priority": "high"
})

# Add low-priority question
low_priority = queue.process({
    "action": "add",
    "question": "What future enhancements do you want?",
    "priority": "low"
})

# Get next question (will be high-priority)
next_q = queue.process({"action": "next"})
print(next_q["next_question"]["question"])
```

### Advanced: Queue Management Flow

```python
# 1. Build question queue
questions = [
    ("What is the problem?", "high"),
    ("Who are users?", "normal"),
    ("What features needed?", "normal"),
    ("Future improvements?", "low")
]

for question, priority in questions:
    queue.process({
        "action": "add",
        "question": question,
        "priority": priority
    })

# 2. Process questions in priority order
status = queue.process({"action": "list"})
print(f"Queued: {status['queued']}, Processed: {status['processed']}")

# 3. Get and process each question
while True:
    next_q = queue.process({"action": "next"})
    if "next_question" not in next_q:
        break

    question_id = next_q["next_question"]["id"]
    # ... present question to user, get answer ...

    # Mark as processed
    queue.process({
        "action": "process",
        "question_id": question_id
    })
```

## Request Format

### action: `add`
Add a question to the queue.

```python
request = {
    "action": "add",
    "question": "What is the goal?",         # Required
    "priority": "normal"                    # Optional: high|normal|low
}
```

**Returns:**
```python
{
    "status": "success",
    "agent": "QuestionQueueAgent",
    "question_id": "q_1",
    "queue_size": 5
}
```

### action: `next`
Get the next question in the queue.

```python
request = {
    "action": "next"
}
```

**Returns:**
```python
{
    "status": "success",
    "agent": "QuestionQueueAgent",
    "next_question": {
        "id": "q_3",
        "question": "What are requirements?",
        "priority": "high",
        "status": "queued"
    }
}
```

Or if queue is empty:
```python
{
    "status": "success",
    "agent": "QuestionQueueAgent",
    "message": "Queue is empty"
}
```

### action: `process`
Mark a question as processed and move it to history.

```python
request = {
    "action": "process",
    "question_id": "q_3"                    # Required
}
```

**Returns:**
```python
{
    "status": "success",
    "agent": "QuestionQueueAgent",
    "question_id": "q_3",
    "processed": true
}
```

### action: `list`
Get complete queue status and list.

```python
request = {
    "action": "list"
}
```

**Returns:**
```python
{
    "status": "success",
    "agent": "QuestionQueueAgent",
    "queued": 3,
    "processed": 2,
    "queue": [
        {
            "id": "q_1",
            "question": "What is the goal?",
            "priority": "high",
            "status": "queued"
        },
        {
            "id": "q_2",
            "question": "Who are users?",
            "priority": "normal",
            "status": "queued"
        },
        {
            "id": "q_4",
            "question": "What about testing?",
            "priority": "normal",
            "status": "queued"
        }
    ]
}
```

## Configuration

### Initialization

```python
from socratic_agents import QuestionQueueAgent

# Basic initialization
queue = QuestionQueueAgent()

# With LLM client (for future enhancement)
from socrates_nexus import LLMClient
llm = LLMClient(provider="anthropic")
queue = QuestionQueueAgent(llm_client=llm)
```

## Priority Levels

| Priority | Order | Use Case |
|----------|-------|----------|
| **high** | First (0) | Critical requirements, blockers |
| **normal** | Second (1) | Standard questions, features |
| **low** | Third (2) | Enhancement ideas, future work |

Default: "normal"

## Common Patterns

### Pattern 1: Simple Queue Processing

```python
def process_question_queue(questions):
    queue = QuestionQueueAgent()

    # Add all questions
    for q in questions:
        queue.process({
            "action": "add",
            "question": q,
            "priority": "normal"
        })

    # Process in order
    while True:
        next_q = queue.process({"action": "next"})
        if "next_question" not in next_q:
            break

        q_id = next_q["next_question"]["id"]
        print(f"Question: {next_q['next_question']['question']}")

        queue.process({"action": "process", "question_id": q_id})
```

### Pattern 2: Priority-Based Batching

```python
def batch_by_priority(questions_with_priority):
    queue = QuestionQueueAgent()

    # Add all questions with priorities
    for q, priority in questions_with_priority:
        queue.process({
            "action": "add",
            "question": q,
            "priority": priority
        })

    # Get queue status
    status = queue.process({"action": "list"})

    # Process all, automatically in priority order
    processed = []
    while True:
        next_q = queue.process({"action": "next"})
        if "next_question" not in next_q:
            break
        processed.append(next_q["next_question"])
        queue.process({
            "action": "process",
            "question_id": next_q["next_question"]["id"]
        })

    return processed
```

### Pattern 3: Dynamic Priority Adjustment

```python
def handle_urgent_questions(base_questions, urgent_questions):
    queue = QuestionQueueAgent()

    # Add base questions as normal priority
    for q in base_questions:
        queue.process({
            "action": "add",
            "question": q,
            "priority": "normal"
        })

    # Add urgent questions as high priority
    for q in urgent_questions:
        queue.process({
            "action": "add",
            "question": q,
            "priority": "high"
        })

    # Queue now has high-priority questions at the front
    return queue.process({"action": "list"})
```

### Pattern 4: Integration with SocraticCounselor

```python
from socratic_agents import SocraticCounselor, QuestionQueueAgent

counselor = SocraticCounselor()
queue = QuestionQueueAgent()

# Generate questions via counselor
for i in range(5):
    q_result = counselor.guide("topic", level="beginner")
    queue.process({
        "action": "add",
        "question": q_result["question"],
        "priority": "normal"
    })

# Present queued questions to user
while True:
    next_q = queue.process({"action": "next"})
    if "next_question" not in next_q:
        break

    # Ask user
    user_answer = input(f"{next_q['next_question']['question']}: ")

    # Mark processed
    queue.process({
        "action": "process",
        "question_id": next_q["next_question"]["id"]
    })
```

## Best Practices

### 1. **Use Priorities Effectively**
```python
# Critical blockers: high
queue.process({
    "action": "add",
    "question": "What are your constraints?",
    "priority": "high"
})

# Main questions: normal
queue.process({
    "action": "add",
    "question": "What are requirements?",
    "priority": "normal"
})

# Future exploration: low
queue.process({
    "action": "add",
    "question": "What about scaling?",
    "priority": "low"
})
```

### 2. **Monitor Queue Health**
```python
def check_queue_health(queue):
    status = queue.process({"action": "list"})

    if status["queued"] > 10:
        print(f"Warning: Large queue ({status['queued']} items)")

    if status["queued"] == 0:
        print("Queue complete")

    print(f"Progress: {status['processed']} processed, {status['queued']} remaining")
```

### 3. **Batch Processing**
```python
def process_batch(queue, batch_size=3):
    processed = []

    for _ in range(batch_size):
        next_q = queue.process({"action": "next"})
        if "next_question" not in next_q:
            break

        q_id = next_q["next_question"]["id"]
        # Process question...
        processed.append(q_id)

        queue.process({"action": "process", "question_id": q_id})

    return processed
```

### 4. **Error Handling**
```python
def safe_add_question(queue, question, priority="normal"):
    if not question or not question.strip():
        print("Error: Question cannot be empty")
        return None

    result = queue.process({
        "action": "add",
        "question": question,
        "priority": priority
    })

    if result["status"] != "success":
        print(f"Error adding question: {result.get('message')}")
        return None

    return result["question_id"]
```

## Integration Examples

### With LearningAgent

```python
from socratic_agents import QuestionQueueAgent, LearningAgent

queue = QuestionQueueAgent()
learner = LearningAgent()

# Add questions to queue
queue.process({
    "action": "add",
    "question": "What is recursion?",
    "priority": "high"
})

# Process from queue
next_q = queue.process({"action": "next"})
question = next_q["next_question"]["question"]
q_id = next_q["next_question"]["id"]

# Get user answer (in real scenario)
user_answer = input(f"{question}: ")

# Track interaction in learning system
learner.process({
    "action": "track_interaction",
    "user_id": "user_1",
    "interaction_type": "question_answered",
    "topic": "recursion",
    "success": True,
    "time_spent": 120
})

# Mark as processed
queue.process({
    "action": "process",
    "question_id": q_id
})
```

## Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| Add question | <1ms | O(n log n) due to sorting |
| Get next | <1ms | O(1) head access |
| Process question | <1ms | O(n) to remove from queue |
| List queue | <1ms | O(n) to compile list |

## Troubleshooting

### Queue Not Respecting Priorities
- Verify priority values are exactly: "high", "normal", or "low"
- Check that questions are being added correctly
- Call "list" action to see actual queue order

### Question Not Found
- Verify question_id matches format: "q_N"
- Check question hasn't already been processed
- Confirm question_id was returned from "add" action

### Queue Appearing Empty
- Check if all questions have been processed
- Use "list" action to see queued and processed counts
- Verify you're checking "next_question" key in response

---

**Related Agents:** SocraticCounselor, LearningAgent

**Next:** [SkillGeneratorAgent](./skill_generator_agent.md)
