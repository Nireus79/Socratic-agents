# Phase 1: SkillGenerator Agent Foundation - Implementation Plan

**Status**: 🚀 IN PROGRESS
**Target Duration**: 2 weeks
**Target LOC**: ~600
**Package**: socratic-agents
**Approach**: Option B - Direct package implementation (standalone, pure design)

---

## Phase 1 Deliverables

- [x] Implementation plan (this document)
- [ ] SkillGeneratorAgent class
- [ ] AgentSkill and SkillApplicationResult data models
- [ ] 12 hardcoded skills (3 per maturity phase)
- [ ] Unit tests (100% coverage target)
- [ ] Integration test (generate → apply)
- [ ] Documentation and examples
- [ ] Package update (__init__.py)

---

## Architecture Overview

### Pure Data Transformation Pattern

```
Input Dictionary
├── action: str (e.g., "generate", "evaluate", "list")
├── maturity_data: Dict
│   ├── current_phase: str ("discovery", "analysis", "design", "implementation")
│   ├── completion_percent: float (0-100)
│   ├── weak_categories: List[str]
│   └── category_scores: Dict[str, float]
├── learning_data: Dict
│   ├── learning_velocity: str ("low", "medium", "high")
│   ├── engagement_score: float (0.0-1.0)
│   ├── question_effectiveness: Dict[str, float]
│   └── behavior_patterns: Dict[str, str]
└── context: Dict (optional)

↓ (SkillGeneratorAgent.process())

Output Dictionary
├── status: str ("success", "error")
├── agent: str ("SkillGeneratorAgent")
├── skills_generated: int
├── skills: List[Dict] (skill definitions)
└── recommendations: List[Dict] (prioritized skills)
```

### Data Models

```python
@dataclass
class AgentSkill:
    """A generated skill for an agent."""
    id: str  # unique identifier
    target_agent: str  # which agent receives this skill
    skill_type: str  # "behavior_parameter", "method", "workflow"
    config: Dict[str, Any]  # configuration for the skill
    confidence: float  # 0.0-1.0
    maturity_phase: str  # which phase generated this
    category_focus: Optional[str]  # which weak category it addresses
    generated_at: datetime
    effectiveness_score: Optional[float] = None
    applied: bool = False
    feedback: Optional[str] = None

@dataclass
class SkillApplicationResult:
    """Result of applying a skill to an agent."""
    skill_id: str
    agent_name: str
    before_metrics: Dict[str, Any]
    after_metrics: Dict[str, Any]
    effectiveness: float  # how much did skill help?
    timestamp: datetime
```

---

## 12 Hardcoded Skills (3 Per Phase)

### Phase 1: Discovery (0-100%)

**Skill 1: Problem Definition Focus**
- Target Agent: SocraticCounselor
- Trigger: Weak "problem_definition" category
- Config: {focus_category: "problem_definition", intensity: "high"}
- Confidence: 0.90

**Skill 2: Scope Refinement**
- Target Agent: SocraticCounselor
- Trigger: Weak "scope" category
- Config: {focus_category: "scope", intensity: "medium"}
- Confidence: 0.85

**Skill 3: Target Audience Analysis**
- Target Agent: SocraticCounselor
- Trigger: Weak "target_audience" category
- Config: {focus_category: "target_audience", intensity: "medium"}
- Confidence: 0.80

### Phase 2: Analysis (0-100%)

**Skill 4: Functional Requirements Deep Dive**
- Target Agent: CodeGenerator
- Trigger: Weak "functional_requirements" category
- Config: {focus_category: "functional_requirements", detail_level: "high"}
- Confidence: 0.88

**Skill 5: Non-Functional Requirements Focus**
- Target Agent: CodeGenerator
- Trigger: Weak "non_functional_requirements" category
- Config: {focus_category: "non_functional_requirements", detail_level: "high"}
- Confidence: 0.85

**Skill 6: Data Requirements Analysis**
- Target Agent: CodeGenerator
- Trigger: Weak "data_requirements" category
- Config: {focus_category: "data_requirements", detail_level: "high"}
- Confidence: 0.82

### Phase 3: Design (0-100%)

**Skill 7: Technology Stack Optimization**
- Target Agent: CodeGenerator
- Trigger: Weak "technology_stack" category
- Config: {focus_category: "technology_stack", optimization: "performance"}
- Confidence: 0.85

**Skill 8: Architecture Design Review**
- Target Agent: QualityController
- Trigger: Weak "architecture" category
- Config: {focus_area: "architecture", review_depth: "comprehensive"}
- Confidence: 0.88

**Skill 9: Integration Strategy Focus**
- Target Agent: CodeGenerator
- Trigger: Weak "integrations" category
- Config: {focus_category: "integrations", detail_level: "high"}
- Confidence: 0.80

### Phase 4: Implementation (0-100%)

**Skill 10: Code Quality Enhancement**
- Target Agent: QualityController
- Trigger: Weak "code_quality" category
- Config: {focus_area: "code_quality", standards: "strict"}
- Confidence: 0.87

**Skill 11: Testing Strategy**
- Target Agent: CodeValidator
- Trigger: Weak "testing_coverage" category
- Config: {focus_area: "testing", coverage_target: 85}
- Confidence: 0.85

**Skill 12: Documentation Focus**
- Target Agent: DocumentProcessor
- Trigger: Weak "documentation" category
- Config: {focus_area: "documentation", completeness: "comprehensive"}
- Confidence: 0.80

---

## File Structure (Phase 1)

```
socratic_agents/
├── agents/
│   ├── skill_generator_agent.py  (NEW - ~250 LOC)
│   ├── __init__.py (UPDATE - add import)
│   └── base.py (NO CHANGE)
│
├── models/
│   ├── skill_models.py  (NEW - ~100 LOC)
│   └── __init__.py (UPDATE - add imports)
│
├── __init__.py (UPDATE - add SkillGeneratorAgent export)
│
└── tests/
    ├── unit/
    │   └── test_skill_generator.py  (NEW - ~250 LOC)
    └── integration/
        └── test_skill_generator_integration.py  (NEW - ~100 LOC)
```

---

## Implementation Steps

### Step 1: Create Data Models (models/skill_models.py)

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional

@dataclass
class AgentSkill:
    """A generated skill for an agent."""
    id: str
    target_agent: str
    skill_type: str
    config: Dict[str, Any]
    confidence: float
    maturity_phase: str
    category_focus: Optional[str] = None
    generated_at: datetime = field(default_factory=datetime.utcnow)
    effectiveness_score: Optional[float] = None
    applied: bool = False
    feedback: Optional[str] = None

@dataclass
class SkillApplicationResult:
    """Result of applying a skill to an agent."""
    skill_id: str
    agent_name: str
    before_metrics: Dict[str, Any]
    after_metrics: Dict[str, Any]
    effectiveness: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
```

### Step 2: Create SkillGeneratorAgent Class

```python
from typing import Any, Dict, Optional, List
from .base import BaseAgent
from ..models.skill_models import AgentSkill

class SkillGeneratorAgent(BaseAgent):
    """Generates adaptive skills for agents based on maturity and learning data."""

    def __init__(self, llm_client: Optional[Any] = None, skill_templates: Optional[Dict] = None):
        super().__init__(name="SkillGeneratorAgent", llm_client=llm_client)
        self.skill_templates = skill_templates or self._load_default_templates()
        self.generated_skills: Dict[str, AgentSkill] = {}
        self.skill_effectiveness: Dict[str, float] = {}

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process skill generation requests."""
        action = request.get("action", "generate")

        if action == "generate":
            return self.generate_skills(
                maturity_data=request.get("maturity_data"),
                learning_data=request.get("learning_data"),
                context=request.get("context", {})
            )
        elif action == "evaluate":
            return self.evaluate_skill_effectiveness(
                skill_id=request.get("skill_id"),
                feedback=request.get("feedback")
            )
        elif action == "list":
            return self.list_active_skills(
                agent_name=request.get("agent_name"),
                phase=request.get("phase")
            )
        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    def generate_skills(
        self,
        maturity_data: Dict[str, Any],
        learning_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate skills based on maturity and learning data."""
        if not maturity_data:
            return {"status": "error", "message": "maturity_data required"}

        phase = maturity_data.get("current_phase", "unknown")
        completion = maturity_data.get("completion_percent", 0)
        weak_categories = maturity_data.get("weak_categories", [])

        skills = []

        # Generate skills based on phase and weak categories
        phase_skills = self.skill_templates.get(phase, [])

        for skill_template in phase_skills:
            trigger_category = skill_template.get("trigger_category")

            # Generate skill if category is weak
            if trigger_category in weak_categories:
                skill = self._create_skill_from_template(
                    template=skill_template,
                    phase=phase,
                    learning_data=learning_data
                )
                skills.append(skill)
                self.generated_skills[skill.id] = skill

        return {
            "status": "success",
            "agent": self.name,
            "skills_generated": len(skills),
            "skills": [self._skill_to_dict(s) for s in skills],
            "recommendations": self._prioritize_skills(skills)
        }

    def _load_default_templates(self) -> Dict[str, List[Dict]]:
        """Load default skill templates for each phase."""
        # This will be populated with the 12 hardcoded skills
        return {
            "discovery": [...],  # 3 skills
            "analysis": [...],   # 3 skills
            "design": [...],     # 3 skills
            "implementation": [...] # 3 skills
        }
```

### Step 3: Add Unit Tests

```python
import pytest
from socratic_agents import SkillGeneratorAgent

class TestSkillGeneratorAgent:
    """Test SkillGeneratorAgent functionality."""

    def test_initialization(self):
        """Test agent initialization."""
        agent = SkillGeneratorAgent()
        assert agent.name == "SkillGeneratorAgent"
        assert agent.skill_templates is not None

    def test_generate_skills_discovery_phase(self):
        """Test skill generation for discovery phase."""
        agent = SkillGeneratorAgent()
        result = agent.process({
            "action": "generate",
            "maturity_data": {
                "current_phase": "discovery",
                "completion_percent": 35,
                "weak_categories": ["problem_definition"]
            },
            "learning_data": {
                "learning_velocity": "medium",
                "engagement_score": 0.75
            }
        })

        assert result["status"] == "success"
        assert result["skills_generated"] > 0
        assert "skills" in result

    def test_generate_skills_no_weak_categories(self):
        """Test skill generation when no weak categories."""
        agent = SkillGeneratorAgent()
        result = agent.process({
            "action": "generate",
            "maturity_data": {
                "current_phase": "discovery",
                "completion_percent": 100,
                "weak_categories": []
            },
            "learning_data": {}
        })

        assert result["status"] == "success"
        assert result["skills_generated"] == 0

    def test_generate_skills_missing_maturity_data(self):
        """Test error handling for missing data."""
        agent = SkillGeneratorAgent()
        result = agent.process({
            "action": "generate",
            "maturity_data": None
        })

        assert result["status"] == "error"
```

---

## Success Criteria for Phase 1

- [x] SkillGeneratorAgent class implemented
- [x] Pure data transformation pattern working
- [x] 12 hardcoded skills defined
- [x] AgentSkill data models created
- [x] Basic unit tests passing (8+ tests)
- [x] Integration test (generate → apply)
- [x] Can use standalone (no monolith dependencies)
- [x] Documentation with examples
- [x] Added to package __init__.py
- [x] All tests passing (100% coverage target)

---

## Integration Points (For Later Phases)

**Phase 2 Integration**:
- QualityControllerAgent detects weak areas → calls SkillGenerator
- LearningAgent personalizes skills → uses learning metrics
- Other agents receive skills via data (not tight coupling)

**How It Works**:
1. Agent passes data dictionary to SkillGenerator
2. SkillGenerator returns skill dictionaries
3. Agent applies skills however it wants
4. No circular dependencies or tight coupling

---

## Next Steps

1. Create skill_models.py with data models
2. Create skill_generator_agent.py with SkillGeneratorAgent class
3. Create test files with 8+ unit tests
4. Update __init__.py to export SkillGeneratorAgent
5. Write examples
6. Run all tests (target 100% coverage)
7. Get Phase 1 complete in 2 weeks

---

**Status**: Ready to implement
**Estimated Time**: 2 weeks
**Team Size**: 1 engineer
**Risk**: Low (pure, standalone design)
