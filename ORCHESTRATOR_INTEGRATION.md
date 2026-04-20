# Orchestrator Integration Guide - v0.3.0

## Overview

The SocratesIntegration class now includes complete Answer Processing Workflow orchestration.

## Answer Processing Workflow

### Method: `process_answer_workflow()`

Implements the complete monolithic pattern workflow:

1. **Extract Specs** - Extract from user response
2. **Filter by Confidence >= 0.7** - Keep high-quality specs only
3. **Merge Into Project** - Add to goals, requirements, tech_stack, constraints
4. **Detect Conflicts** - Find contradictions
5. **Update Maturity** - Update project progression
6. **Auto-Generate Follow-up** - Generate next question avoiding repeats
7. **Store in Conversation History** - Persist for next generation

### Return Value

```python
{
    "status": "success",                    # or "error"
    "specs": {...},                         # High-confidence specs
    "conflicts": [...],                     # Detected conflicts
    "maturity": {...},                      # Updated scores
    "next_question": "What features...",    # Follow-up question
}
```

## Helper Methods

- `_filter_specs_by_confidence(specs, min_confidence=0.7)` - Filter specs
- `_merge_specs_into_project(project, specs)` - Merge into project fields
- `_extract_recently_asked(project, phase)` - Extract previous questions
- `_get_last_question(project)` - Get current question

## Complete Example

```python
result = integration.process_answer_workflow(
    project=project,
    user_response="Basic arithmetic operations",
    current_user=user_id,
    counselor=counselor_instance,
    detector=detector_instance,
)

if result["status"] == "success":
    print(f"Specs: {result['specs']}")
    print(f"Conflicts: {result['conflicts']}")
    print(f"Next question: {result['next_question']}")
    db.save_project(project)
```

## Monolithic Pattern Compliance

✅ Question Generation - Extract + pass + store + avoid repeats
✅ Answer Processing - Extract + filter + merge + detect + update + generate follow-up
✅ Conversation History - Persist + type filter + phase filter + response turn
✅ Confidence Filtering - >= 0.7 at all decision points

## v0.3.0 Complete

All core workflow orchestration now implemented and documented.
