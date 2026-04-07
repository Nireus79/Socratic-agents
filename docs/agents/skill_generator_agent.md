# SkillGeneratorAgent

**Adaptive skill generation based on maturity phases and learning metrics.**

## Overview

The SkillGeneratorAgent generates adaptive behavioral skills for agents based on maturity phases and learning data. It analyzes weak categories and generates targeted skills to improve agent performance. Skills are customized based on learning velocity and engagement patterns, without modifying agent state directly.

## Key Capabilities

### 1. **Adaptive Skill Generation**
- Generate skills from maturity phase data
- Analyze weak categories and generate targeted skills
- Customize skills based on learning velocity
- Adjust confidence based on engagement patterns

### 2. **Skill Prioritization**
- Prioritize skills by weakness severity
- Consider engagement levels in prioritization
- Calculate expected impact of each skill
- Three-tier priority system (high, medium, low)

### 3. **Skill Effectiveness Tracking**
- Evaluate skill effectiveness after application
- Track feedback on skill usefulness
- Store effectiveness scores (0.0-1.0)
- Learn from skill application history

### 4. **Skill Management**
- List generated skills with filtering
- Filter by target agent or phase
- Maintain skill inventory
- Track all generated skills

## Usage

### Basic: Generate Skills from Maturity Data

```python
from socratic_agents import SkillGeneratorAgent

skill_gen = SkillGeneratorAgent()

# Generate skills for weak areas
result = skill_gen.process({
    "action": "generate",
    "maturity_data": {
        "current_phase": "implementation",
        "completion_percent": 65,
        "weak_categories": ["testing_coverage", "documentation"],
        "category_scores": {
            "code_quality": 0.8,
            "testing_coverage": 0.4,
            "documentation": 0.3,
            "architecture": 0.75,
            "performance": 0.7
        }
    }
})

print(f"Skills generated: {result['skills_generated']}")
for skill in result['skills']:
    print(f"  - {skill['id']}: {skill['config']}")
```

### Intermediate: Generate with Learning Data

```python
# Include learning metrics for customization
result = skill_gen.process({
    "action": "generate",
    "maturity_data": {
        "current_phase": "design",
        "completion_percent": 50,
        "weak_categories": ["architecture"],
        "category_scores": {
            "architecture": 0.45
        }
    },
    "learning_data": {
        "learning_velocity": "high",
        "engagement_score": 0.85
    }
})

# Skills will be high-intensity, high-confidence
for skill in result['skills']:
    print(f"Skill: {skill['id']}")
    print(f"  Config: {skill['config']}")
    print(f"  Confidence: {skill['confidence']}")
```

### Advanced: Evaluate and List Skills

```python
# Generate skills
gen_result = skill_gen.process({
    "action": "generate",
    "maturity_data": {
        "current_phase": "implementation",
        "completion_percent": 70,
        "weak_categories": ["testing_coverage"],
        "category_scores": {"testing_coverage": 0.5}
    }
})

skill_id = gen_result['skills'][0]['id']

# Apply skill, then evaluate effectiveness
effectiveness = skill_gen.process({
    "action": "evaluate",
    "skill_id": skill_id,
    "feedback": "helped improve test coverage",
    "effectiveness_score": 0.85
})

# List all skills for implementation phase
listing = skill_gen.process({
    "action": "list",
    "phase": "implementation"
})

print(f"Skills for implementation: {listing['skills_count']}")
```

## Request Format

### action: `generate`
Generate skills based on maturity and learning data.

```python
request = {
    "action": "generate",
    "maturity_data": {                          # Required
        "current_phase": "implementation",      # Maturity phase
        "completion_percent": 65,               # Phase completion %
        "weak_categories": ["testing"],         # Categories with low scores
        "category_scores": {                    # Scores for each category
            "code_quality": 0.8,
            "testing_coverage": 0.4,
            "documentation": 0.3,
            "architecture": 0.75,
            "performance": 0.7
        }
    },
    "learning_data": {                          # Optional
        "learning_velocity": "high",            # high|medium|low
        "engagement_score": 0.85                # 0.0-1.0
    },
    "context": {}                               # Optional
}
```

**Returns:**
```python
{
    "status": "success",
    "agent": "SkillGeneratorAgent",
    "phase": "implementation",
    "completion_percent": 65,
    "skills_generated": 2,
    "skills": [
        {
            "id": "implementation_testing_strategy_a1b2c3d4",
            "target_agent": "CodeValidator",
            "skill_type": "behavior_parameter",
            "config": {
                "focus_area": "testing",
                "coverage_target": 85,
                "include_integration_tests": true
            },
            "confidence": 0.87,
            "maturity_phase": "implementation",
            "category_focus": "testing_coverage"
        }
    ],
    "recommendations": [
        {
            "skill_id": "implementation_testing_strategy_a1b2c3d4",
            "priority": "high",
            "reason": "Addresses weak category 'testing_coverage' (0.4 score) with expected impact 85%",
            "expected_impact": 0.85
        }
    ]
}
```

### action: `evaluate`
Evaluate effectiveness of an applied skill.

```python
request = {
    "action": "evaluate",
    "skill_id": "implementation_testing_strategy_a1b2c3d4",  # Required
    "feedback": "helped improve coverage",                  # Optional
    "effectiveness_score": 0.85                            # Optional: 0.0-1.0
}
```

**Returns:**
```python
{
    "status": "success",
    "agent": "SkillGeneratorAgent",
    "skill_id": "implementation_testing_strategy_a1b2c3d4",
    "feedback": "helped improve coverage",
    "effectiveness_score": 0.85,
    "skill": {
        "id": "implementation_testing_strategy_a1b2c3d4",
        "target_agent": "CodeValidator",
        "config": {...},
        "confidence": 0.87,
        "effectiveness_score": 0.85,
        "feedback": "helped improve coverage"
    }
}
```

### action: `list`
List generated skills with optional filtering.

```python
request = {
    "action": "list",
    "agent_name": "CodeValidator",          # Optional: filter by agent
    "phase": "implementation"                # Optional: filter by phase
}
```

**Returns:**
```python
{
    "status": "success",
    "agent": "SkillGeneratorAgent",
    "agent_filter": "CodeValidator",
    "phase_filter": "implementation",
    "skills_count": 3,
    "skills": [
        {
            "id": "implementation_testing_strategy_a1b2c3d4",
            "target_agent": "CodeValidator",
            "skill_type": "behavior_parameter",
            "config": {...},
            "confidence": 0.87,
            "maturity_phase": "implementation",
            "category_focus": "testing_coverage"
        }
    ]
}
```

## Configuration

### Initialization

```python
from socratic_agents import SkillGeneratorAgent

# Basic initialization (uses default templates)
skill_gen = SkillGeneratorAgent()

# With LLM client (for future LLM-based skill generation)
from socrates_nexus import LLMClient
llm = LLMClient(provider="anthropic")
skill_gen = SkillGeneratorAgent(llm_client=llm)

# With custom templates
custom_templates = {
    "custom_phase": [
        {
            "id": "custom_skill",
            "target_agent": "SocraticCounselor",
            "trigger_category": "engagement",
            "config": {"intensity": "high"},
            "confidence": 0.9
        }
    ]
}
skill_gen = SkillGeneratorAgent(skill_templates=custom_templates)
```

## Maturity Phases

Skills are defined for each maturity phase:

| Phase | Duration | Skills | Focus |
|-------|----------|--------|-------|
| **discovery** | Initial | 3 skills | Problem definition, scope, audience |
| **analysis** | Early | 3 skills | Requirements, non-functional specs, data |
| **design** | Middle | 3 skills | Technology stack, architecture, integration |
| **implementation** | Core | 3 skills | Code quality, testing, documentation |

Each phase has 3 predefined skills addressing common weak areas.

## Skill Configuration

Skills customize agent behavior with parameters:

```python
{
    "focus_area": "testing",              # What to focus on
    "coverage_target": 85,                # Target coverage %
    "include_integration_tests": true,    # Additional options
    "intensity": "high"                   # high|medium|low
}
```

## Priority System

Skills are prioritized based on:

| Factor | Weight | Calculation |
|--------|--------|-------------|
| Category weakness | 50% | 1.0 - category_score |
| Engagement | 50% | learning_engagement_score |

**Result:**
- **High** (>70% expected impact) - Critical improvements
- **Medium** (40-70%) - Moderate improvements
- **Low** (<40%) - Minor improvements

## Learning Customization

Skills adapt to learning patterns:

| Learning Velocity | Effect | Intensity |
|-------------------|--------|-----------|
| **high** | Fast learner | high |
| **medium** | Steady progress | medium |
| **low** | Careful pace | low |

Engagement scores adjust skill confidence:
- Low engagement: 0.8x confidence multiplier
- High engagement: 1.2x confidence multiplier

## Best Practices

### 1. **Generate Before Applying**
```python
# Always generate skills first
gen_result = skill_gen.process({
    "action": "generate",
    "maturity_data": maturity_data
})

# Then apply the recommended skills
for recommendation in gen_result['recommendations']:
    if recommendation['priority'] in ['high', 'medium']:
        apply_skill(recommendation['skill_id'])
```

### 2. **Track Effectiveness**
```python
# After applying a skill, evaluate it
gen_result = skill_gen.process({
    "action": "generate",
    "maturity_data": maturity_data
})

# ... apply skills ...

# Then evaluate how well they worked
for skill in gen_result['skills']:
    skill_gen.process({
        "action": "evaluate",
        "skill_id": skill['id'],
        "feedback": "helpful",
        "effectiveness_score": 0.8
    })
```

### 3. **Use with QualityController**
```python
from socratic_agents import QualityController, SkillGeneratorAgent

quality = QualityController()
skill_gen = SkillGeneratorAgent()

# Check quality and identify weak areas
quality_result = quality.process({
    "action": "detect_weak_areas",
    "code": code_string
})

# Generate skills to address weak areas
skill_result = skill_gen.process({
    "action": "generate",
    "maturity_data": {
        "current_phase": quality_result['phase'],
        "completion_percent": quality_result['completion_percent'],
        "weak_categories": quality_result['weak_categories'],
        "category_scores": quality_result['category_scores']
    }
})

# Apply high-priority skills
for rec in skill_result['recommendations']:
    if rec['priority'] == 'high':
        apply_to_workflow(rec)
```

### 4. **Monitor Skill Inventory**
```python
def get_active_skills(skill_gen):
    # List all generated skills
    all_skills = skill_gen.process({"action": "list"})

    # Group by phase
    by_phase = {}
    for skill in all_skills['skills']:
        phase = skill['maturity_phase']
        if phase not in by_phase:
            by_phase[phase] = []
        by_phase[phase].append(skill)

    return by_phase
```

## Common Patterns

### Pattern 1: Basic Skill Generation

```python
def generate_improvement_skills(phase, weak_categories, category_scores):
    skill_gen = SkillGeneratorAgent()

    result = skill_gen.process({
        "action": "generate",
        "maturity_data": {
            "current_phase": phase,
            "completion_percent": 60,
            "weak_categories": weak_categories,
            "category_scores": category_scores
        }
    })

    return result['skills']
```

### Pattern 2: Skill Generation with Learning Data

```python
def generate_personalized_skills(maturity_data, learning_velocity, engagement):
    skill_gen = SkillGeneratorAgent()

    return skill_gen.process({
        "action": "generate",
        "maturity_data": maturity_data,
        "learning_data": {
            "learning_velocity": learning_velocity,
            "engagement_score": engagement
        }
    })
```

### Pattern 3: Skill Application and Evaluation

```python
def apply_and_evaluate_skills(skills, apply_func, evaluate_func):
    skill_gen = SkillGeneratorAgent()

    for skill in skills:
        # Apply skill
        apply_func(skill)

        # Get feedback
        feedback = evaluate_func(skill)

        # Evaluate in system
        skill_gen.process({
            "action": "evaluate",
            "skill_id": skill['id'],
            "feedback": feedback['text'],
            "effectiveness_score": feedback['score']
        })
```

## Integration Examples

### With CodeGenerator and QualityController

```python
from socratic_agents import CodeGenerator, QualityController, SkillGeneratorAgent

generator = CodeGenerator()
quality = QualityController()
skill_gen = SkillGeneratorAgent()

# 1. Generate code
code_result = generator.process({
    "action": "generate",
    "prompt": "API endpoint for authentication"
})

# 2. Check quality and identify weak areas
quality_result = quality.process({
    "action": "detect_weak_areas",
    "code": code_result["code"]
})

# 3. Generate skills to address weak areas
skills_result = skill_gen.process({
    "action": "generate",
    "maturity_data": {
        "current_phase": quality_result['phase'],
        "completion_percent": quality_result['completion_percent'],
        "weak_categories": quality_result['weak_categories'],
        "category_scores": quality_result['category_scores']
    }
})

# 4. Apply recommended skills for improvement
for recommendation in skills_result['recommendations']:
    if recommendation['priority'] == 'high':
        # Apply skill to improve this area
        improved = generator.process({
            "action": "refactor",
            "code": code_result["code"],
            "improvements": [recommendation['skill_id']]
        })
```

## Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| Generate skills | <100ms | Template lookup |
| Prioritize skills | <50ms | Scoring calculation |
| Evaluate skill | <10ms | Update effectiveness |
| List skills | <50ms | Filter and compile |

## Troubleshooting

### No Skills Generated for Weak Categories
- Verify phase is recognized (discovery, analysis, design, implementation)
- Check weak_categories match trigger_categories in templates
- Verify maturity_data structure is correct

### Skills Have Low Confidence
- Check engagement_score is reasonable (0.0-1.0)
- Review learning_velocity setting
- May indicate weak category doesn't match template triggers

### Cannot Find Skill by ID
- Verify skill_id format matches generation
- Check skill hasn't been deleted
- Use "list" action to see available skills

---

**Related Agents:** QualityController, CodeGenerator, CodeValidator

**Next:** [KnowledgeManager](./knowledge_manager.md)
