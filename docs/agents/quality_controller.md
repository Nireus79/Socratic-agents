# QualityController Agent

**Quality assurance, testing, and maturity assessment for projects.**

## Overview

The QualityController agent manages quality assurance operations, analyzes code quality, identifies weak areas that need improvement, integrates with the maturity assessment system, and generates targeted skills to address quality gaps. It bridges quality metrics with skill-based improvement recommendations.

## Key Capabilities

### 1. **Code Quality Analysis**
- Detects code smells and anti-patterns
- Identifies weak areas requiring improvement
- Calculates quality scores (0-100)
- Tracks quality metrics over time

### 2. **Maturity Assessment**
- Determines project phase (discovery, analysis, design, implementation)
- Calculates phase completion percentage
- Identifies readiness for next phase
- Recommends phase-specific improvements

### 3. **Issue Detection**
- Code complexity analysis
- Test coverage assessment
- Performance bottlenecks
- Security vulnerabilities
- Documentation gaps

### 4. **Skill Generation**
- Generates skills to fix identified issues
- Recommends learning resources
- Tracks skill application
- Measures skill effectiveness

### 5. **Testing Framework**
- Test generation and validation
- Coverage tracking
- Test execution orchestration
- Reports and metrics

## Usage

### Basic: Check Code Quality

```python
from socratic_agents import QualityController

controller = QualityController()

result = controller.process({
    "action": "check",
    "code": python_code
})

print(f"Quality Score: {result['quality_score']}")
print(f"Issues Found: {len(result['issues'])}")
for issue in result['issues']:
    print(f"  - {issue['severity']}: {issue['description']}")
```

### Intermediate: Analyze Weak Areas

```python
result = controller.process({
    "action": "detect_weak_areas",
    "code": python_code,
    "language": "python"
})

print(f"Weak Areas: {result['weak_areas']}")
print(f"Quality Score: {result['quality_score']}")

# Get recommendations
recommendations = result.get('recommendations', [])
for rec in recommendations:
    print(f"  - {rec['category']}: {rec['description']}")
```

### Advanced: Full Quality Pipeline

```python
# 1. Detect issues
quality_result = controller.process({
    "action": "detect_weak_areas",
    "code": code,
    "language": "python"
})

weak_areas = quality_result['weak_areas']

# 2. Generate skills to fix issues
from socratic_agents import SkillGeneratorAgent
skill_gen = SkillGeneratorAgent()

skills = []
for weak_area in weak_areas:
    skill = skill_gen.process({
        "action": "generate",
        "maturity_data": {
            "weak_categories": [weak_area]
        }
    })
    skills.append(skill)

# 3. Track improvement
improvement = controller.process({
    "action": "track_improvement",
    "skills_applied": [s["skill_id"] for s in skills],
    "before_score": quality_result['quality_score']
})

print(f"Improvement: {improvement['improvement_percentage']}%")
```

## Request Format

### action: `check`
Perform basic quality check on code.

```python
request = {
    "action": "check",
    "code": code_string,                         # Required
    "language": "python",                        # Optional
    "checks": [                                  # Optional
        "style",
        "complexity",
        "coverage",
        "security"
    ]
}
```

**Returns:**
```python
{
    "status": "success",
    "quality_score": 75,                         # 0-100
    "issues": [
        {
            "type": "missing_docstring",
            "severity": "medium",
            "location": "line 42",
            "description": "Function lacks documentation"
        }
    ],
    "metrics": {
        "complexity": 8,
        "test_coverage": 85,
        "duplicated_lines": 12
    }
}
```

### action: `detect_weak_areas`
Identify areas needing improvement.

```python
request = {
    "action": "detect_weak_areas",
    "code": code_string,                         # Required
    "language": "python",                        # Optional
    "threshold": 70                              # Optional: score threshold
}
```

**Returns:**
```python
{
    "status": "success",
    "quality_score": 65,
    "weak_areas": [
        "documentation",
        "test_coverage",
        "code_complexity"
    ],
    "issues": [...],
    "recommendations": [
        {
            "category": "documentation",
            "description": "Add docstrings to functions",
            "priority": "high"
        }
    ]
}
```

### action: `assess_maturity`
Evaluate project maturity and readiness.

```python
request = {
    "action": "assess_maturity",
    "maturity_data": {                           # Required
        "current_phase": "analysis",
        "completion_percent": 60,
        "weak_categories": ["testing"]
    }
}
```

**Returns:**
```python
{
    "status": "success",
    "phase": "analysis",
    "phase_score": 75,
    "ready_for_next_phase": False,
    "completion_percentage": 60,
    "blockers": [
        "Test coverage below 80%",
        "Missing API documentation"
    ],
    "recommendations_for_phase": [
        "Increase test coverage to 85%",
        "Document all public APIs"
    ]
}
```

### action: `generate_skills`
Generate skills to fix identified issues.

```python
request = {
    "action": "generate_skills",
    "quality_issues": quality_result["issues"],   # Required
    "weak_areas": quality_result["weak_areas"],   # Required
    "code_context": code_string                   # Optional
}
```

**Returns:**
```python
{
    "status": "success",
    "skills_generated": 3,
    "skills": [
        {
            "skill_id": "skill_123",
            "name": "Improve Test Coverage",
            "area": "testing",
            "implementation": "..."
        }
    ]
}
```

### action: `track_improvement`
Track quality improvements over time.

```python
request = {
    "action": "track_improvement",
    "before_score": 65,                          # Required
    "after_score": 78,                           # Required
    "skills_applied": ["skill_123", "skill_456"],  # Optional
    "changes": ["Added tests", "Refactored functions"]  # Optional
}
```

**Returns:**
```python
{
    "status": "success",
    "improvement_points": 13,
    "improvement_percentage": 20,
    "skill_effectiveness": {
        "skill_123": 0.8,  # 80% effective
        "skill_456": 0.9
    }
}
```

## Configuration

### Initialization

```python
from socratic_agents import QualityController

# Basic initialization
controller = QualityController()

# With LLM client
from socrates_nexus import LLMClient
llm = LLMClient(provider="anthropic")
controller = QualityController(llm_client=llm)
```

### Configuration Options

| Option | Type | Default | Purpose |
|--------|------|---------|---------|
| `llm_client` | LLMClient | None | LLM for analysis |
| `quality_threshold` | int | 70 | Minimum acceptable score |
| `enable_skills` | bool | True | Enable skill generation |
| `track_history` | bool | True | Track quality over time |

## Quality Metrics

### Code Quality Factors
| Factor | Weight | Description |
|--------|--------|-------------|
| Complexity | 25% | Cyclomatic complexity |
| Coverage | 25% | Test coverage percentage |
| Documentation | 20% | Code documentation completeness |
| Style | 15% | Code style consistency |
| Security | 15% | Security vulnerabilities |

### Score Interpretation
- **90-100**: Excellent - Production ready
- **70-89**: Good - Minor improvements needed
- **50-69**: Fair - Significant work needed
- **Below 50**: Poor - Major refactoring required

## Issue Types

### Code Quality Issues
- `missing_docstring` - Function lacks documentation
- `high_complexity` - Complex function (CC > 10)
- `long_function` - Function too long (> 50 lines)
- `duplicate_code` - Code duplication detected
- `unused_variable` - Unused variable assigned

### Testing Issues
- `low_coverage` - Test coverage below threshold
- `no_tests` - No tests for module
- `failing_tests` - Tests are failing
- `slow_tests` - Tests take too long

### Documentation Issues
- `missing_docstring` - Function lacks docs
- `incomplete_docs` - Partial documentation
- `outdated_docs` - Documentation stale

### Security Issues
- `hardcoded_secret` - Secret in code
- `sql_injection` - SQL injection risk
- `insecure_deserialize` - Unsafe deserialization
- `weak_crypto` - Weak cryptography

## Best Practices

### 1. **Regular Quality Checks**
```python
# Schedule periodic quality assessments
import schedule

def check_quality():
    result = controller.process({
        "action": "detect_weak_areas",
        "code": get_latest_code()
    })
    log_quality_result(result)

schedule.every().day.at("10:00").do(check_quality)
```

### 2. **Address Issues Progressively**
```python
# Fix issues by priority
result = controller.process({"action": "detect_weak_areas", ...})

issues_by_priority = sorted(
    result["issues"],
    key=lambda x: {"high": 1, "medium": 2, "low": 3}[x["severity"]]
)

for issue in issues_by_priority:
    create_task_to_fix(issue)
```

### 3. **Use Skills for Improvement**
```python
# Generate and apply skills
quality = controller.process({"action": "detect_weak_areas", ...})
skill_gen = SkillGeneratorAgent()

skills = skill_gen.process({
    "action": "generate",
    "maturity_data": {
        "weak_categories": quality["weak_areas"]
    }
})

# Apply skills to improve
apply_skills_to_code(skills)
```

### 4. **Track Progress**
```python
# Measure improvement over time
before = controller.process({"action": "check", "code": old_code})

# Make improvements...

after = controller.process({"action": "check", "code": new_code})

improvement = controller.process({
    "action": "track_improvement",
    "before_score": before["quality_score"],
    "after_score": after["quality_score"]
})

print(f"Improvement: {improvement['improvement_percentage']}%")
```

## Integration Examples

### With SkillGeneratorAgent
```python
from socratic_agents import QualityController, SkillGeneratorAgent

controller = QualityController()
skill_gen = SkillGeneratorAgent()

# 1. Detect issues
quality = controller.process({
    "action": "detect_weak_areas",
    "code": code
})

# 2. Generate skills
skills = skill_gen.process({
    "action": "generate",
    "maturity_data": {
        "weak_categories": quality["weak_areas"]
    }
})

# 3. Track improvement
for skill in skills:
    apply_skill(skill)

# 4. Verify improvement
new_quality = controller.process({
    "action": "check",
    "code": improved_code
})
```

### With Maturity Assessment
```python
# Assess project readiness
maturity = controller.process({
    "action": "assess_maturity",
    "maturity_data": {
        "current_phase": "design",
        "completion_percent": 70,
        "weak_categories": ["testing", "documentation"]
    }
})

if maturity["ready_for_next_phase"]:
    advance_to_next_phase()
else:
    # Apply recommended improvements
    for rec in maturity["recommendations_for_phase"]:
        create_improvement_task(rec)
```

### With CodeGenerator
```python
from socratic_agents import QualityController, CodeGenerator

controller = QualityController()
generator = CodeGenerator()

# Find weak areas
quality = controller.process({
    "action": "detect_weak_areas",
    "code": code
})

# Generate improved code
for weak_area in quality["weak_areas"]:
    improved = generator.process({
        "action": "refactor",
        "code": code,
        "improvements": [weak_area]
    })
    code = improved["refactored_code"]

# Verify improvement
new_quality = controller.process({
    "action": "check",
    "code": code
})
```

## Common Patterns

### Pattern 1: Quality Gate
```python
def quality_gate(code, min_score=75):
    result = controller.process({
        "action": "check",
        "code": code
    })

    if result["quality_score"] >= min_score:
        return True, "Code passes quality gate"
    else:
        issues = "\n".join([
            f"  - {i['severity']}: {i['description']}"
            for i in result["issues"][:3]
        ])
        return False, f"Code quality too low:\n{issues}"
```

### Pattern 2: Continuous Improvement
```python
def improve_code_quality(code, target_score=85):
    current_score = 0
    iterations = 0

    while current_score < target_score and iterations < 5:
        quality = controller.process({
            "action": "detect_weak_areas",
            "code": code
        })

        for weak_area in quality["weak_areas"]:
            improved = generator.process({
                "action": "refactor",
                "code": code,
                "improvements": [weak_area]
            })
            code = improved["refactored_code"]

        current_score = quality["quality_score"]
        iterations += 1

    return code, current_score
```

### Pattern 3: Phase Readiness Check
```python
def is_ready_for_next_phase(code, current_phase):
    maturity = controller.process({
        "action": "assess_maturity",
        "maturity_data": {
            "current_phase": current_phase,
            "completion_percent": 75,
            "weak_categories": detect_weak_areas(code)
        }
    })

    return maturity["ready_for_next_phase"], maturity["blockers"]
```

## Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| Check code quality | <1s | Quick analysis |
| Detect weak areas | 2-5s | Detailed analysis |
| Assess maturity | <1s | State-based |
| Generate skills | 3-10s | May use LLM |
| Track improvement | <500ms | Calculation |

## Troubleshooting

### Quality Score Seems Wrong
- Verify all checks are enabled
- Check code metrics are calculated
- Ensure language is correct
- Review weighting in configuration

### Issues Not Detected
- Check `checks` parameter includes relevant checks
- Verify code is syntactically valid
- Check language support
- Enable verbose logging

### Skills Not Improving Quality
- Verify skills are correctly applied
- Check skill effectiveness ratings
- May need multiple iterations
- Review specific issues being addressed

---

**Related Agents:** SkillGeneratorAgent, CodeGenerator, CodeValidator

**Next:** [LearningAgent](./learning_agent.md)
