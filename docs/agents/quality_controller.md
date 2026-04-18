# QualityController Agent

**Quality assurance, workflow optimization, and intelligent path selection with approval gating.**

## Overview

The QualityController is the quality and workflow orchestration engine for the Socratic system. It serves three critical functions:

1. **Code Quality Analysis** - Pattern-based assessment of code across 5 quality dimensions
2. **Maturity Estimation** - Tracks project progress through development phases
3. **Workflow Optimization** - Prevents greedy optimization by analyzing ALL execution paths, calculating comprehensive metrics (cost, risk, quality, ROI), recommending optimal paths, and requiring human approval before execution

The workflow optimization prevents "greedy" algorithm patterns where the easiest first step is always taken. Instead, it analyzes complete paths and ensures minimum total cost across all steps.

## Key Capabilities

### 1. **Code Quality Analysis**
- Pattern-based code quality assessment
- 5-category evaluation system
- Weak area identification
- Quality scoring (0-100)

### 2. **Category Assessment**
- Code Quality - Evaluates structure and patterns
- Testing Coverage - Checks for test statements
- Documentation - Looks for docstrings and comments
- Architecture - Assesses class and function organization
- Performance - Identifies performance issues

### 3. **Maturity Phase Estimation**
- Uses MaturityCalculator from socrates-maturity library
- Estimates project phase (discovery, analysis, design, implementation)
- Calculates completion percentage
- Identifies weak categories (score < 0.6)

### 4. **Skill Application**
- Applies skills from SkillGeneratorAgent
- Tracks applied skills for improvement
- Sets quality focus areas
- Logs all skill applications

### 5. **Complete Workflow Optimization**

The agent uses a sophisticated 4-step workflow optimization system:

#### Step 1: Path Enumeration
- Uses `WorkflowPathFinder` with depth-first search
- Discovers ALL valid execution routes from start to end nodes
- Tracks covered categories for each path

#### Step 2: Metric Calculation
For each path, calculates:

**Cost Metrics:**
- Token consumption (using operation-specific estimates)
- USD equivalent (using LLM provider pricing)
- Token/cost per operation type

**Risk Metrics:**
- Overall risk score (0-1.0)
- Incompleteness risk (40% of overall) - coverage gaps
- Complexity risk (30% of overall) - technical difficulty
- Rework probability (30% of overall) - likelihood of rework needed

**Quality Metrics:**
- Quality score (0-100)
- Coverage quality (based on categories covered)
- Complexity quality (based on path length)
- Expected maturity gain
- ROI (maturity points per 1000 tokens)

#### Step 3: Path Selection
Supports four decision strategies:

- **MINIMIZE_COST** - Selects path with lowest token consumption
- **MINIMIZE_RISK** - Selects path with minimal risk score
- **MAXIMIZE_QUALITY** - Selects path with highest quality score
- **BALANCED** - Weighted combination (50% cost, 30% risk, 20% quality) - **Default**

All metrics are normalized and combined using weighted formulas.

#### Step 4: Approval Request
- Generates human-readable approval requests
- Shows all analyzed paths with metrics
- Recommends optimal path with reasoning
- Requires explicit human approval before proceeding
- **Prevents greedy optimization** - doesn't auto-execute

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

### Advanced: Workflow Optimization

```python
controller = QualityController()

# Define workflow with all possible paths
workflow_definition = {
    "nodes": {
        "socratic": {
            "type": "question",
            "covers_categories": ["goals", "requirements", "audience"]
        },
        "generator": {
            "type": "code_generation",
            "covers_categories": ["architecture", "design"]
        },
        "validator": {
            "type": "validation",
            "covers_categories": ["testing", "validation"]
        }
    },
    "edges": [
        {"id": "e1", "source": "socratic", "target": "generator"},
        {"id": "e2", "source": "socratic", "target": "validator"},
        {"id": "e3", "source": "generator", "target": "validator"},
        {"id": "e4", "source": "validator", "target": "generator"}
    ],
    "start_nodes": ["socratic"],
    "end_nodes": ["validator"]
}

# Step 1: Request optimization and approval
approval = controller.process({
    "action": "optimize_workflow",
    "workflow_definition": workflow_definition
})

print(f"Approval ID: {approval['approval_id']}")
print(f"Paths analyzed: {approval['paths_analyzed']}")

# Step 2: Review paths and metrics
for path_idx, path_data in enumerate(approval['approval_request']['paths']):
    metrics = path_data['metrics']
    print(f"\nPath {path_idx}: {' -> '.join(path_data['path']['nodes'])}")
    print(f"  Cost: {metrics['cost']['tokens']} tokens (${metrics['cost']['usd']})")
    print(f"  Risk: {metrics['risk']['overall_score']:.1%}")
    print(f"  Quality: {metrics['quality']['score']:.0f}/100")
    print(f"  ROI: {metrics['maturity']['roi_per_1000_tokens']:.2f} points/1k tokens")

# Step 3: Submit approval decision
result = controller.process({
    "action": "submit_approval",
    "approval_id": approval['approval_id'],
    "approved": True
})

print(f"\n✓ {result['message']}")
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
    "issues": ["Code is too short"]
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
    "phase": "implementation",
    "category_scores": {
        "code_quality": 0.8,
        "testing_coverage": 0.4,
        "documentation": 0.3,
        "architecture": 0.75,
        "performance": 0.7
    },
    "weak_categories": ["testing_coverage", "documentation"],
    "completion_percent": 60.0
}
```

### action: `apply_skills`
Apply skills to improve quality.

```python
request = {
    "action": "apply_skills",
    "skills": [skill_dict_1, skill_dict_2]       # Required
}
```

**Returns:**
```python
{
    "status": "success",
    "agent": "QualityController",
    "skills_applied": 2,
    "applied_skills": ["skill_123", "skill_456"],
    "focus_area": "testing_coverage"
}
```

### action: `optimize_workflow`
Optimize workflow by analyzing all paths and requesting approval.

```python
request = {
    "action": "optimize_workflow",
    "workflow_definition": {                     # Required
        "nodes": {
            "node_id": {
                "type": "question",
                "covers_categories": ["goals", "requirements"]
            }
        },
        "edges": [
            {"id": "e1", "source": "node1", "target": "node2"}
        ],
        "start_nodes": ["node1"],
        "end_nodes": ["node2"]
    }
}
```

**Returns:**
```python
{
    "status": "pending_approval",
    "agent": "QualityController",
    "approval_id": "approval_a1b2c3d4",
    "paths_analyzed": 3,
    "approval_request": {
        "paths_analyzed": 3,
        "selected_path_index": 0,
        "selection_strategy": "balanced",
        "paths": [
            {
                "path": {
                    "nodes": ["node1", "node2"],
                    "covered_categories": ["goals", "requirements", "testing"],
                    "step_count": 2
                },
                "metrics": {
                    "cost": {"tokens": 900, "usd": 0.0405},
                    "risk": {
                        "overall_score": 0.367,
                        "incompleteness": 0.375,
                        "complexity": 0.2,
                        "rework_probability": 0.45
                    },
                    "quality": {
                        "score": 87.5,
                        "coverage_quality": 87.5,
                        "complexity_quality": 90.0
                    },
                    "maturity": {
                        "estimated_gain": 62.5,
                        "roi_per_1000_tokens": 69.44
                    },
                    "coverage": {
                        "categories_covered": 3,
                        "categories": ["goals", "requirements", "testing"],
                        "missing": ["audience", "constraints", "tech_stack", "architecture", "design"],
                        "coverage_percentage": 37.5
                    }
                }
            }
        ],
        "recommendation": {
            "reason": "Balanced selection: 900 tokens, 36.7% risk, 87.5% quality, 37.5% coverage",
            "selected_metrics": {...}
        }
    }
}
```

### action: `submit_approval`
Submit human approval or rejection for a pending workflow.

```python
request = {
    "action": "submit_approval",
    "approval_id": "approval_a1b2c3d4",          # Required
    "approved": true                              # Required
}
```

**Returns:**
```python
{
    "status": "success",
    "agent": "QualityController",
    "approval_id": "approval_a1b2c3d4",
    "approved": true,
    "selected_path_index": 0,
    "message": "Workflow approved. Selected path optimizes for: ...",
    "metrics": {...}
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
            "approval_id": "approval_a1b2c3d4",
            "paths_analyzed": 3,
            "selection_strategy": "balanced",
            "recommendation": {...}
        }
    ]
}
```

## Workflow Metrics Explained

### Cost Metrics
- **tokens** - Estimated LLM token consumption
- **usd** - USD cost at current pricing rates
- Calculated per operation type (question generation, response analysis, validation, etc.)

### Risk Metrics (0.0-1.0 scale)
- **overall_risk_score** - Weighted combination of all risks
- **incompleteness_risk** (40% weight) - Percentage of required categories not covered
- **complexity_risk** (30% weight) - Technical difficulty based on node types
- **rework_probability** (30% weight) - Likelihood of needing to rework

### Quality Metrics (0-100 scale)
- **quality_score** - Combined quality assessment
- **coverage_quality** - Based on category coverage
- **complexity_quality** - Based on path complexity
- Calculated as: coverage + complexity - risk_penalty

### ROI Calculation
- **roi_per_1000_tokens** - Maturity gain per 1000 tokens spent
- Higher ROI = better efficiency for gaining maturity points
- Accounts for both gains and costs

## Decision Strategies

The optimizer supports multiple strategies:

| Strategy | Focus | Best For |
|----------|-------|----------|
| MINIMIZE_COST | Lowest tokens | Budget-constrained projects |
| MINIMIZE_RISK | Lowest risk | High-stakes projects |
| MAXIMIZE_QUALITY | Highest quality | Quality-critical projects |
| BALANCED | 50% cost, 30% risk, 20% quality | Default - balanced approach |
| USER_CHOICE | All options | Manual evaluation |

## Best Practices

### 1. **Always Use Workflow Optimization for Major Decisions**

```python
# Good: Analyze all paths and get approval
approval = controller.process({
    "action": "optimize_workflow",
    "workflow_definition": all_possible_paths
})

# Bad: Just pick the first path
execute_path(paths[0])
```

### 2. **Review All Paths Before Approval**

```python
# Show user all analyzed options
for idx, path in enumerate(approval['approval_request']['paths']):
    metrics = path['metrics']
    print(f"Path {idx}: Cost={metrics['cost']['tokens']}, Risk={metrics['risk']['overall_score']:.1%}")

# Get explicit approval
user_decision = input("Approve path 0? (yes/no): ")
```

### 3. **Monitor Approval Decisions**

```python
# Track what's been approved vs rejected
pending = controller.process({"action": "get_pending_approvals"})
print(f"Approved: {pending['approved_count']}")
print(f"Rejected: {pending['rejected_count']}")
```

### 4. **Use Appropriate Strategy**

```python
# For cost-sensitive: MINIMIZE_COST
# For production: BALANCED (default)
# For research: MAXIMIZE_QUALITY
# For review: USER_CHOICE
```

## Integration Examples

### With SkillGeneratorAgent

```python
from socratic_agents import QualityController, SkillGeneratorAgent

controller = QualityController()
skill_gen = SkillGeneratorAgent()

# Detect weak areas
quality = controller.process({
    "action": "detect_weak_areas",
    "code": code
})

# Generate skills for weak areas
skills = skill_gen.process({
    "action": "generate",
    "maturity_data": {
        "weak_categories": quality["weak_categories"],
        "category_scores": quality["category_scores"]
    }
})

# Apply skills
controller.process({
    "action": "apply_skills",
    "skills": skills["skills"]
})
```

### Complete Workflow Optimization and Approval

```python
from socratic_agents import QualityController

controller = QualityController()

# 1. Optimize workflow
approval = controller.process({
    "action": "optimize_workflow",
    "workflow_definition": workflow
})

# 2. Get pending approvals
pending = controller.process({
    "action": "get_pending_approvals"
})

# 3. Submit approval
result = controller.process({
    "action": "submit_approval",
    "approval_id": approval['approval_id'],
    "approved": True
})

if result['approved']:
    # Proceed with approved path
    execute_workflow(result['selected_path_index'])
```

## Architecture Components

The workflow optimization system consists of four core components:

### WorkflowPathFinder
- Implements depth-first search algorithm
- Discovers all valid execution routes
- Tracks covered categories per path
- Returns WorkflowPath objects

### WorkflowCostCalculator
- Estimates token costs per operation
- Converts to USD using provider pricing
- Provides cost breakdown by operation type
- Supports multiple pricing models (input, output, balanced)

### WorkflowRiskCalculator
- Calculates three risk dimensions
- Incompleteness risk (coverage gaps)
- Complexity risk (technical difficulty)
- Rework probability (likelihood of rework)
- Identifies missing categories

### WorkflowOptimizer
- Orchestrates the 4-step optimization process
- Implements decision strategies
- Normalizes and weights metrics
- Generates approval requests

## Common Patterns

### Pattern 1: Quality Gate

```python
def quality_gate(code, min_score=75):
    result = controller.process({
        "action": "check",
        "code": code
    })
    return result["quality_score"] >= min_score
```

### Pattern 2: Workflow Approval Flow

```python
def approve_workflow(workflow):
    # Analyze
    approval = controller.process({
        "action": "optimize_workflow",
        "workflow_definition": workflow
    })

    # Review
    recommendation = approval['approval_request']['recommendation']
    print(f"Recommended: {recommendation['reason']}")

    # Decide
    approved = get_user_decision()

    # Submit
    result = controller.process({
        "action": "submit_approval",
        "approval_id": approval['approval_id'],
        "approved": approved
    })

    return result
```

### Pattern 3: Prevent Greedy Optimization

```python
def prevent_greedy(possible_paths):
    """Analyze ALL paths before choosing."""
    # QualityController prevents:
    # - Picking easiest first step immediately
    # - Making local optimal choices

    # Instead does:
    # - Analyze all complete paths
    # - Calculate total costs for all paths
    # - Recommend global optimum
    # - Require human approval

    approval = controller.process({
        "action": "optimize_workflow",
        "workflow_definition": {
            "paths": possible_paths  # ALL paths
        }
    })

    return approval
```

## Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| Check code quality | <10ms | Pattern-based analysis |
| Detect weak areas | <50ms | Category assessment |
| Path enumeration | <100ms | DFS traversal |
| Metric calculation | <500ms | Cost, risk, quality |
| Path optimization | <200ms | Selection strategy |
| Total workflow optimization | 1-2s | Complete 4-step process |

## Implementation Notes

### Phase 1-2 (Completed)
- Code quality analysis
- Weak area detection
- Maturity phase estimation
- Skill application

### Phase 3 (Implemented)
- Complete WorkflowOptimizer with 4 decision strategies
- Full metric calculation (cost, risk, quality, ROI)
- Approval gating system
- Prevents greedy optimization

### Architecture Respects Original Design
- Uses WorkflowPathFinder for path enumeration
- Uses WorkflowCostCalculator for token/USD costs
- Uses WorkflowRiskCalculator for comprehensive risk metrics
- Uses DecisionStrategy enum for all optimization strategies
- Implements balanced normalization and weighted combination

---

**Related Agents:** SkillGeneratorAgent, CodeGenerator, CodeValidator, SocraticCounselor

**Next:** [LearningAgent](./learning_agent.md)
