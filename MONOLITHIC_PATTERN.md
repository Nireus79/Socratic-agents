# Monolithic Pattern Implementation Guide

## Overview

The socratic-agents library v0.3.0 implements the **Monolithic Socrates Pattern** - a proven workflow for guided learning through structured dialogue.

## The Core Pattern

### Question Generation Workflow

```
Extract Previously Asked Questions
    ↓ (type="assistant" + phase filtering from conversation_history)
    ↓
Pass "recently_asked" to SocraticCounselor with:
    "[CRITICAL] Previously asked questions (DO NOT REPEAT OR REPHRASE THESE)"
    ↓
Claude generates NEW unique question
    ↓
Store question in conversation_history (type="assistant", phase, response_turn)
    ↓
Return to user
```

### Answer Processing Workflow

```
User submits answer
    ↓
Extract specs with confidence scores
    ↓
Filter by confidence >= 0.7 (HIGH QUALITY ONLY)
    ↓
Merge filtered specs into project fields:
    - goals
    - requirements
    - tech_stack
    - constraints
    ↓
Detect conflicts (using only high-confidence specs)
    ↓
Update project maturity
    ↓
Save project
    ↓
Auto-generate follow-up question
    ↓
Store follow-up in conversation_history
    ↓
Return specs, conflicts, maturity, next question
```

## Implementation Details

### Recently Asked Extraction (CRITICAL)

```python
def extract_recently_asked(project, phase):
    """Extract questions to avoid repeating (MONOLITHIC PATTERN)."""
    recently_asked = []
    for msg in project.conversation_history:
        if (
            msg.get("type") == "assistant"  # Only questions
            and msg.get("phase") == phase   # Only this phase
            and msg.get("content")           # Has content
        ):
            recently_asked.append(msg.get("content"))
    return recently_asked
```

### Spec Merging with Filtering (CRITICAL)

```python
def merge_specs(project, extracted_specs):
    """Merge high-confidence specs only."""
    for goal in extracted_specs.get("goals", []):
        confidence = goal.get("confidence_score", 1.0) if isinstance(goal, dict) else 0.7
        if goal and confidence >= 0.7 and goal not in project.goals:
            project.goals.append(goal)
    # ... similar for requirements, tech_stack, constraints
```

### Confidence Filtering (CRITICAL)

Only specs with confidence >= 0.7:
- Participate in conflict detection
- Drive maturity updates
- Get merged into project
- Are used for decision-making

### Response Turn Tracking (FOR AUDITABILITY)

```python
response_turn = len([m for m in project.conversation_history if m.get("type") == "assistant"]) + 1

project.conversation_history.append({
    "type": "assistant",
    "content": question,
    "phase": phase,
    "response_turn": response_turn,  # Trace back to understand origin
})
```

## Agent Responsibilities

- **SocraticCounselor**: Generate questions with recently_asked, extract specs
- **QualityController**: Assign confidence scores, validate specs
- **ConflictDetector**: Filter by confidence >= 0.7, detect conflicts
- **LearningAgent**: Track progression, filter by phase

## Testing the Pattern

See examples/monolithic_question_workflow.py for working demonstrations.

## Version History

- v0.2.9: Core SocraticCounselor with recently_asked support
- v0.3.0: Complete monolithic pattern implementation (this version)
