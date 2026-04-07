# QualityController Agent

**Quality assurance, workflow optimization, and maturity assessment for projects.**

## Overview

The QualityController agent is the quality and workflow gatekeeper for the Socratic system. It:

1. **Analyzes code quality** through pattern detection
2. **Identifies weak areas** for skill-based improvement
3. **Estimates maturity phases** using the MaturityCalculator
4. **Manages workflow approval** to prevent greedy optimization
5. **Enumerates execution paths** and recommends optimal routes
6. **Calculates cost/risk/quality metrics** for workflow comparison
7. **Requires human approval** before execution proceeds

The agent prevents "greedy" optimization by requiring deliberate human approval of major workflow decisions, ensuring minimum total cost across all steps rather than just easiest first steps.

## Key Capabilities

### 1. **Code Quality Analysis**
- Checks for code length and structure
- Detects TODO/FIXME comments
- Assesses code patterns (classes, functions, imports)
- Returns quality score (0-100)

### 2. **Category Assessment**
- Code Quality - Evaluates code structure and patterns
- Testing Coverage - Checks for test and assert statements
- Documentation - Looks for docstrings and comments
- Architecture - Assesses class and function organization
- Performance - Identifies loops and import patterns

### 3. **Maturity Phase Estimation**
- Uses MaturityCalculator from socrates-maturity library
- Estimates current project phase based on code metrics
- Calculates completion percentage
- Identifies weak categories (score < 0.6)

### 4. **Skill Application**
- Applies skills from SkillGeneratorAgent
- Tracks applied skills for future reference
- Sets quality focus area from skills
- Logs skill application history

### 5. **Workflow Approval System**
- Enumerates multiple execution paths
- Calculates cost, risk, and quality metrics
- Recommends optimal path (minimum total cost)
- Requests human approval before proceeding
- **Prevents greedy optimization** - doesn't take easiest first step
- Tracks approved and rejected workflows

### 6. **Workflow Metrics Calculation**
- **Cost Metrics** - Token consumption and USD equivalents
- **Risk Metrics** - Risk score, incompleteness risk, complexity risk
- **Quality Metrics** - Coverage quality, complexity quality
- **ROI Calculation** - Maturity gain per token

### 7. **Testing & Reporting**
- Runs stored test suites
- Generates quality reports
- Tracks quality scores over time
- Reports on test execution

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
print(f"Issues: {result['issues']}")
```

### Intermediate: Detect Weak Areas

```python
result = controller.process({
    "action": "detect_weak_areas",
    "code": python_code
})

print(f"Current Phase: {result['phase']}")
print(f"Category Scores: {result['category_scores']}")
print(f"Weak Categories: {result['weak_categories']}")
print(f"Completion: {result['completion_percent']}%")
```

### Advanced: Apply Skills and Report

```python
# 1. Check quality
quality_result = controller.process({
    "action": "check",
    "code": code
})

weak_areas = quality_result['issues']

# 2. Get skills from SkillGeneratorAgent
from socratic_agents import SkillGeneratorAgent
skill_gen = SkillGeneratorAgent()

skills = skill_gen.process({
    "action": "generate",
    "maturity_data": {
        "weak_categories": ["testing_coverage", "documentation"]
    }
})

# 3. Apply skills to quality controller
application = controller.process({
    "action": "apply_skills",
    "skills": skills.get("skills", [])
})

# 4. Generate report
report = controller.process({
    "action": "report"
})

print(f"Quality Score: {report['overall_score']}")
print(f"Tests Run: {report['tests_run']}")
```

### Workflow Approval System: Request and Approve

```python
controller = QualityController()

# 1. Request approval for multiple workflow paths
approval_result = controller.process({
    "action": "approve_workflow",
    "workflows": [
        {
            "steps": ["SocraticCounselor", "CodeGenerator", "CodeValidator"],
            "estimated_maturity_gain": 30,
            "missing_categories": 1
        },
        {
            "steps": ["SocraticCounselor", "CodeValidator", "CodeGenerator"],
            "estimated_maturity_gain": 25,
            "missing_categories": 2
        }
    ]
})

print(f"Workflow ID: {approval_result['workflow_id']}")
print(f"Recommended path: {approval_result['approval_request']['recommended_path_id']}")
print(f"Paths analyzed: {approval_result['paths_analyzed']}")

# 2. Check pending approvals
pending = controller.process({
    "action": "get_pending_approvals"
})

# 3. Submit approval decision
approval = controller.process({
    "action": "submit_approval",
    "workflow_id": approval_result['workflow_id'],
    "approved": True
})

print(f"Approval status: {approval['message']}")
```

## Request Format

### action: `check`
Perform basic quality check on code.

```python
request = {
    "action": "check",
    "code": code_string                          # Required
}
```

**Returns:**
```python
{
    "status": "success",
    "agent": "QualityController",
    "quality_score": 80,                         # 0-100
    "issues": [
        "Code is too short",
        "Contains TODO comments"
    ]
}
```

### action: `detect_weak_areas`
Analyze code and identify weak categories.

```python
request = {
    "action": "detect_weak_areas",
    "code": code_string                          # Required
}
```

**Returns:**
```python
{
    "status": "success",
    "agent": "QualityController",
    "phase": "discovery",                        # Estimated maturity phase
    "category_scores": {
        "code_quality": 0.8,
        "testing_coverage": 0.6,
        "documentation": 0.5,
        "architecture": 0.7,
        "performance": 0.7
    },
    "weak_categories": [                         # Categories with score < 0.6
        "documentation"
    ],
    "completion_percent": 35.0
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

### action: `approve_workflow`
Request approval for workflow paths by analyzing metrics and recommending optimal route.

```python
request = {
    "action": "approve_workflow",
    "workflows": [                                    # Required
        {
            "steps": ["agent1", "agent2", "agent3"],
            "estimated_maturity_gain": 30,
            "missing_categories": 1
        },
        {
            "steps": ["agent1", "agent3", "agent2"],
            "estimated_maturity_gain": 25,
            "missing_categories": 2
        }
    ]
}
```

**Returns:**
```python
{
    "status": "pending_approval",
    "agent": "QualityController",
    "workflow_id": "workflow_a1b2c3d4",
    "paths_analyzed": 2,
    "approval_request": {
        "id": "workflow_a1b2c3d4",
        "status": "pending",
        "paths": [
            {
                "path_id": "path_0",
                "path": ["agent1", "agent2", "agent3"],
                "metrics": {
                    "token_cost": 1500,
                    "usd_cost": 0.003,
                    "total_cost": 1500,
                    "risk_score": 0.367,
                    "quality_score": 87.5,
                    "roi": 0.02,
                    "step_count": 3
                }
            }
        ],
        "recommended_path_id": "path_0",
        "recommendation_reason": "Lowest total cost: 1500 tokens"
    }
}
```

### action: `submit_approval`
Submit user approval or rejection for a pending workflow.

```python
request = {
    "action": "submit_approval",
    "workflow_id": "workflow_a1b2c3d4",    # Required
    "approved": true                        # Required: true to approve, false to reject
}
```

**Returns:**
```python
{
    "status": "success",
    "agent": "QualityController",
    "workflow_id": "workflow_a1b2c3d4",
    "approved": true,
    "message": "Workflow approved. Using recommended path: path_0"
}
```

### action: `get_pending_approvals`
Get all pending workflow approvals.

```python
request = {
    "action": "get_pending_approvals"
}
```

**Returns:**
```python
{
    "status": "success",
    "agent": "QualityController",
    "pending_count": 2,
    "approved_count": 5,
    "rejected_count": 1,
    "pending_approvals": [
        {
            "id": "workflow_a1b2c3d4",
            "status": "pending",
            "paths": [...],
            "recommended_path_id": "path_0",
            "recommendation_reason": "Lowest total cost: 1500 tokens"
        }
    ]
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

## Workflow Metrics

### Cost Metrics
- **token_cost** - Estimated token consumption for the workflow
- **usd_cost** - Approximate USD cost at ~$0.002 per 1k tokens
- **total_cost** - Overall cost metric used for optimization

### Risk Metrics
- **risk_score** - Overall risk (0.0-1.0)
- **incompleteness_risk** - Risk from missing categories
- **complexity_risk** - Risk from workflow complexity

### Quality Metrics
- **quality_score** - Estimated quality (0-100)
- **roi** - Return on investment (maturity gain per token)
- **step_count** - Number of steps in workflow

## Best Practices

### 1. **Use Workflow Approval for Critical Paths**
```python
# Always request approval for important workflow decisions
approval = controller.process({
    "action": "approve_workflow",
    "workflows": candidate_workflows
})

# Wait for human decision before proceeding
if approval["status"] == "pending_approval":
    # Present options to user
    # User decides and submits approval
    pass
```

### 2. **Prevent Greedy Optimization**
```python
# DON'T: Just take the first successful path
# risk of greedy approach

# DO: Compare all paths and let QualityController recommend
approval = controller.process({
    "action": "approve_workflow",
    "workflows": [path1, path2, path3]  # All options
})

# QualityController analyzes all and recommends minimum-cost path
recommended = approval["approval_request"]["recommended_path_id"]
```

### 3. **Monitor Approval Decisions**
```python
# Track what's been approved vs rejected
pending = controller.process({"action": "get_pending_approvals"})

print(f"Pending: {pending['pending_count']}")
print(f"Approved: {pending['approved_count']}")
print(f"Rejected: {pending['rejected_count']}")
```

### 4. **Regular Quality Checks**
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

### With Workflow Approval System

```python
from socratic_agents import QualityController

controller = QualityController()

# 1. Define possible workflows for reaching goals
workflows = [
    {
        "steps": ["SocraticCounselor", "CodeGenerator", "CodeValidator"],
        "estimated_maturity_gain": 35,
        "missing_categories": 1
    },
    {
        "steps": ["SocraticCounselor", "CodeValidator", "CodeGenerator"],
        "estimated_maturity_gain": 30,
        "missing_categories": 2
    },
    {
        "steps": ["CodeGenerator", "SocraticCounselor", "CodeValidator"],
        "estimated_maturity_gain": 25,
        "missing_categories": 2
    }
]

# 2. Request QualityController to analyze and recommend optimal path
approval = controller.process({
    "action": "approve_workflow",
    "workflows": workflows
})

# 3. System analyzes all paths and recommends minimum-cost option
print(f"Workflow ID: {approval['workflow_id']}")
print(f"Recommended path: {approval['approval_request']['recommended_path_id']}")

# 4. Show all options to user for review
for path in approval['approval_request']['paths']:
    metrics = path['metrics']
    print(f"\n{path['path_id']}: {' -> '.join(path['path'])}")
    print(f"  Cost: {metrics['token_cost']} tokens (${metrics['usd_cost']})")
    print(f"  Risk: {metrics['risk_score']} (quality: {metrics['quality_score']})")

# 5. User reviews and approves/rejects
user_approval = controller.process({
    "action": "submit_approval",
    "workflow_id": approval['workflow_id'],
    "approved": True
})

if user_approval["approved"]:
    print(f"✓ {user_approval['message']}")
    # Proceed with approved workflow
else:
    print("✗ Workflow rejected - try different approach")
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

### Pattern 4: Prevent Greedy Optimization

```python
def approve_optimal_workflow(candidate_workflows):
    """
    Compare all workflow options and get approval for optimal (min cost) path.

    Prevents greedy algorithm pattern where easiest first step is always taken.
    Instead analyzes all paths and approves minimum-cost complete path.
    """
    controller = QualityController()

    # Request analysis of all candidate paths
    approval = controller.process({
        "action": "approve_workflow",
        "workflows": candidate_workflows
    })

    # QualityController recommends minimum-cost path
    recommended = approval['approval_request']['recommended_path_id']

    # Get user approval before proceeding
    result = controller.process({
        "action": "submit_approval",
        "workflow_id": approval['workflow_id'],
        "approved": True
    })

    return result['approved'], recommended
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

## Implementation Notes

### Current Implementation (Phase 1-2)
The current implementation includes:
- ✅ Code quality analysis (pattern-based)
- ✅ Weak area detection (5-category assessment)
- ✅ Maturity phase estimation
- ✅ Skill application tracking

### Workflow Approval System (Phase 3)
The workflow approval system is now implemented and includes:
- ✅ Path enumeration and metric calculation
- ✅ Cost, risk, and quality analysis
- ✅ Optimal path recommendation (minimum cost)
- ✅ Human approval gate (prevents greedy algorithms)
- ✅ Workflow tracking (approved/rejected/pending)

### Future Enhancement Plans
Planned improvements for future versions:
- Integration with real token cost APIs
- Advanced path finding algorithms
- Machine learning-based ROI prediction
- Workflow history analytics

---

**Related Agents:** SkillGeneratorAgent, CodeGenerator, CodeValidator, SocraticCounselor

**Next:** [LearningAgent](./learning_agent.md)
