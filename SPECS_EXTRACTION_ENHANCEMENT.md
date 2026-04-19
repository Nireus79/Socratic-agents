# Specs Extraction Enhancement - Status and Confidence Scoring

## Overview

The specs extraction in `SocraticCounselor` has been enhanced to return structured results with status indicators and confidence scoring, replacing silent failures with clear, actionable information.

## What Changed

### Previous Behavior
```python
return {"status": "success", "insights": {...}}
```
- Only indicated success/error at top level
- No confidence scoring
- No way to distinguish "no specs found" from "extraction failed"
- Limited metadata about extraction quality

### New Behavior
```python
{
    "status": "success|partial|empty|failed",
    "confidence_score": 0.0-1.0,
    "specs": {
        "goals": [...],
        "requirements": [...],
        "gaps": [...],
        "decisions": [...],
        "questions": [...]
    },
    "metadata": {
        "extraction_method": "llm|fallback",
        "item_count": int,
        "error": str or None
    }
}
```

## Status Values

| Status | Criteria | Confidence | Meaning |
|--------|----------|------------|---------|
| `success` | 8+ items | 0.85-0.95 | High-quality extraction |
| `partial` | 3-7 items | 0.6 | Some specs extracted |
| `empty` | 0 items | 0.0 | No specs found |
| `failed` | Exception | 0.0 | Extraction error |

## Confidence Scoring

Confidence is calculated based on extraction quality:

```
0 items      → 0.0 confidence
1-2 items    → 0.5 confidence (fallback only)
3-7 items    → 0.6 confidence
8+ items     → 0.75-0.95 confidence (scales with item count)
```

## Extraction Methods

### LLM-based (Primary)
- Uses LLM to intelligently extract specs
- Higher confidence and accuracy
- Handles natural language variations
- Returns detailed structured results

### Fallback (Keyword-based)
- Used when no LLM client available
- Keyword matching on common patterns
- Lower confidence but always returns something
- Fast and deterministic

## Usage Examples

### Handling Success
```python
result = agent.process({
    "action": "extract_insights_only",
    "response": user_input
})

if result["status"] == "success":
    print(f"Extracted {result['metadata']['item_count']} specs")
    use_specs(result["specs"])
elif result["status"] == "partial":
    print(f"Partial extraction, confidence: {result['confidence_score']}")
    use_specs_with_caution(result["specs"])
```

### Filtering by Confidence
```python
if result["confidence_score"] > 0.7:
    save_to_database(result["specs"])
else:
    queue_for_manual_review(result)
```

### Error Handling
```python
if result["status"] == "failed":
    error_msg = result["metadata"]["error"]
    log_extraction_error(error_msg)
    fallback_to_manual_input()
```

## Benefits

1. **Clear Status Indication**
   - No more silent failures
   - Explicit success/partial/empty/failed states
   - Easier debugging

2. **Quality Metrics**
   - Confidence scores inform decision-making
   - Item counts show extraction volume
   - Extraction method is documented

3. **Error Context**
   - Actual exception messages in metadata
   - Helps with troubleshooting
   - Enables logging and monitoring

4. **Backward Compatibility**
   - Still returns `specs` field with extracted data
   - Callers can check status before using specs
   - Graceful fallback to keyword extraction

## Implementation Details

### New Helper Methods

#### `_extract_goals_fallback(text: str) -> List[str]`
Extracts goals using keywords: "goal", "objective", "aim", "purpose", "want to", "build", "create", "develop"

#### `_extract_requirements_fallback(text: str) -> List[str]`
Extracts requirements using keywords: "require", "need", "must", "should", "feature", "support"

### Confidence Calculation
```python
item_count = sum of all extracted items
if item_count == 0:
    status = "empty", confidence = 0.0
elif item_count < 3:
    status = "partial", confidence = 0.6
elif item_count < 8:
    status = "success", confidence = 0.75 + (item_count / 100)
else:
    status = "success", confidence = min(0.85 + (item_count / 100), 0.95)
```

## Testing

Comprehensive test suite in `tests/unit/test_specs_extraction_status.py`:

- Empty response handling
- LLM-based success/partial extraction
- Fallback extraction
- Malformed JSON handling
- Exception handling
- Confidence score bounds
- Specs structure normalization
- Duplicate prevention

## Migration Guide

### For Existing Code

If you were checking `result["status"] == "success"`:
```python
# Old code still works
if result["status"] == "success":
    process(result["specs"])

# But now you can also check confidence
if result["status"] in ["success", "partial"] and result["confidence_score"] > 0.5:
    process(result["specs"])
```

### For New Code

Take advantage of the new features:
```python
result = agent._extract_insights_only(request)

# Check detailed status
if result["status"] == "success":
    # High-confidence extraction
    use_specs(result["specs"])
elif result["status"] == "partial":
    # Some extraction, but low confidence
    review_manually(result["specs"])
elif result["status"] == "empty":
    # Nothing extracted
    prompt_user_for_input()
elif result["status"] == "failed":
    # Extraction error
    log_error(result["metadata"]["error"])
```

## Future Enhancements

1. **Pluggable Extraction Methods**
   - Support for domain-specific extractors
   - Custom keyword sets
   - Machine learning-based extraction

2. **Extraction Caching**
   - Cache similar responses
   - Reduce LLM calls
   - Improve performance

3. **Continuous Learning**
   - Track extraction quality metrics
   - Improve confidence scoring over time
   - A/B test extraction methods

4. **Multi-LLM Support**
   - Try multiple LLMs
   - Ensemble confidence scores
   - Fallback to better models

## References

- Related to: Socrates AI system specs extraction
- Upstream: https://github.com/Nireus79/Socratic-agents
- Integration: Used in socrates-api orchestrator for validation
