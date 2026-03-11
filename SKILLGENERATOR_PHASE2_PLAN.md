# SkillGeneratorAgent Phase 2: Integration Plan

**Status**: 🚀 IN PROGRESS
**Target Duration**: 2 weeks
**Target LOC**: ~400
**Date Started**: March 10, 2026

---

## Phase 2 Overview

Integrate SkillGeneratorAgent with QualityControllerAgent and LearningAgent to enable:
1. **Automatic weak area detection** - QualityController identifies problems
2. **Skill generation on demand** - SkillGenerator creates solutions
3. **Personalization** - LearningAgent customizes recommendations
4. **Effectiveness tracking** - System learns from results

---

## Architecture: Integration Flow

```
QualityControllerAgent (Quality Analysis)
    ↓ detects weak areas
    ├→ category_scores: {quality: 0.3, testing: 0.4, ...}
    ├→ weak_categories: ["code_quality", "testing_coverage"]
    └→ triggers SkillGenerator

SkillGeneratorAgent (Skill Generation)
    ↓ generates skills based on weaknesses
    ├→ analyzes maturity phase & learning data
    ├→ creates 1-3 applicable skills
    └→ passes to LearningAgent for personalization

LearningAgent (Personalization & Learning)
    ↓ personalizes recommendations
    ├→ adjusts priorities based on user patterns
    ├→ suggests best skills for user type
    ├→ records feedback on skill effectiveness
    └→ improves future recommendations
```

---

## Implementation: 3 Components

### 1. Enhanced QualityControllerAgent (~100 LOC)

**New Methods**:
```python
def detect_weak_areas(self, code: str) -> Dict[str, Any]
    # Returns category scores and weak_categories
    # Format: {"problem_definition": 0.3, "scope": 0.8, ...}

def request_skill_generation(self, weak_areas: Dict) -> Dict[str, Any]
    # Calls SkillGeneratorAgent.process()
    # Returns: {"skills": [...], "recommendations": [...]}

def apply_skills(self, skills: List[Dict]) -> Dict[str, Any]
    # Applies recommended skills to quality checks
    # Tracks which skills are being used
```

**Changes**:
- Add `quality_focus_area` field to track current focus
- Add `generated_skills` list to store active skills
- Add `skill_application_log` for tracking

**Integration Flow**:
```python
def process(self, request):
    action = request.get("action")
    if action == "check":
        quality = self.check_quality(request.get("code"))
        if quality < 70:  # Low quality - request skills
            weak_areas = self.detect_weak_areas(request.get("code"))
            skills = self.request_skill_generation(weak_areas)
            return {**quality, "recommended_skills": skills}
    elif action == "apply_skills":
        return self.apply_skills(request.get("skills"))
```

### 2. Enhanced LearningAgent (~120 LOC)

**New Methods**:
```python
def personalize_skills(self, skills: List[Dict], user_profile: Dict) -> List[Dict]
    # Adjusts skill recommendations based on learning patterns
    # Returns personalized/prioritized skills

def track_skill_feedback(self, skill_id: str, feedback: str) -> Dict[str, Any]
    # Records user feedback on skill effectiveness
    # Updates learning metrics

def predict_skill_effectiveness(self, skill: Dict) -> float
    # Uses historical data to estimate effectiveness
    # Range: 0.0-1.0

def get_user_learning_profile(self) -> Dict[str, Any]
    # Returns user's learning characteristics
    # velocity, engagement, preferred_styles, etc.
```

**Changes**:
- Add `skill_effectiveness_history` to track past skill results
- Add `user_profile` dictionary with learning characteristics
- Add `personalization_rules` based on patterns

**Integration Flow**:
```python
def process(self, request):
    action = request.get("action")
    if action == "record":
        self.record_interaction(request.get("interaction"))
    elif action == "personalize_skills":
        skills = request.get("skills")
        user_profile = self.get_user_learning_profile()
        return self.personalize_skills(skills, user_profile)
    elif action == "track_feedback":
        return self.track_skill_feedback(
            request.get("skill_id"),
            request.get("feedback")
        )
```

### 3. Agent Orchestration (~80 LOC)

**New File**: `src/socratic_agents/integrations/skill_orchestrator.py`

```python
class SkillOrchestrator:
    """Orchestrates skill generation, personalization, and application."""

    def __init__(self):
        self.quality_controller = QualityController()
        self.skill_generator = SkillGeneratorAgent()
        self.learning_agent = LearningAgent()

    def process_quality_issue(self, code: str) -> Dict[str, Any]:
        """
        End-to-end workflow:
        1. Detect weak areas
        2. Generate skills
        3. Personalize recommendations
        4. Return prioritized skills
        """
        # Step 1: Detect weak areas
        weak_areas = self.quality_controller.detect_weak_areas(code)

        # Step 2: Generate skills
        maturity_data = self._extract_maturity_from_code(code)
        learning_data = self.learning_agent.get_user_learning_profile()

        skills_result = self.skill_generator.process({
            "action": "generate",
            "maturity_data": maturity_data,
            "learning_data": learning_data
        })

        # Step 3: Personalize
        personalized = self.learning_agent.process({
            "action": "personalize_skills",
            "skills": skills_result["skills"]
        })

        return {
            "status": "success",
            "weak_areas": weak_areas,
            "skills": personalized,
            "recommendations": skills_result["recommendations"]
        }

    def apply_and_track_skill(self, skill_id: str, skill: Dict) -> Dict[str, Any]:
        """Apply a skill and track its effectiveness."""
        # Apply skill through QualityController
        result = self.quality_controller.apply_skills([skill])

        # Record for learning
        self.learning_agent.track_skill_feedback(skill_id, "applied")

        return result

    def _extract_maturity_from_code(self, code: str) -> Dict[str, Any]:
        """Extract maturity characteristics from code."""
        # Parse code to determine maturity phase
        # Based on code patterns, complexity, completeness
        return {
            "current_phase": "implementation",  # Simplified example
            "completion_percent": self._estimate_completion(code),
            "weak_categories": [],
            "category_scores": {}
        }
```

---

## Integration Tests (~120 LOC)

**File**: `tests/integration/test_skill_integration.py`

**Test Cases**:

1. **Quality Detection → Skill Generation**
   - QualityController detects weak areas
   - SkillGeneratorAgent generates appropriate skills
   - Verify skills target correct agents

2. **Skill Personalization**
   - LearningAgent personalizes recommendations
   - Priorities adjusted based on user patterns
   - High-engagement users get harder skills

3. **End-to-End Workflow**
   - SkillOrchestrator runs complete workflow
   - Weak areas → skills → personalization → tracking
   - Verify all components interact correctly

4. **Effectiveness Tracking**
   - Skills applied and tracked
   - Feedback recorded in LearningAgent
   - Future recommendations adjusted

5. **Cross-Agent Communication**
   - QualityController → SkillGenerator → LearningAgent
   - Data flows correctly between agents
   - No data loss or corruption

---

## Implementation Steps

### Step 1: Enhance QualityControllerAgent (1 day)
- [ ] Add `detect_weak_areas()` method
- [ ] Add `request_skill_generation()` method
- [ ] Add `apply_skills()` method
- [ ] Update `process()` for skill generation workflow
- [ ] Update tests for new methods

### Step 2: Enhance LearningAgent (1 day)
- [ ] Add `personalize_skills()` method
- [ ] Add `track_skill_feedback()` method
- [ ] Add `predict_skill_effectiveness()` method
- [ ] Add `get_user_learning_profile()` method
- [ ] Update `process()` for skill personalization
- [ ] Update tests for new methods

### Step 3: Create SkillOrchestrator (1 day)
- [ ] Create `skill_orchestrator.py`
- [ ] Implement `process_quality_issue()` workflow
- [ ] Implement `apply_and_track_skill()` method
- [ ] Add orchestration logic
- [ ] Create integration tests for orchestrator

### Step 4: Integration Testing (1 day)
- [ ] Create end-to-end test suite
- [ ] Test cross-agent communication
- [ ] Test data flow between components
- [ ] Test error handling & edge cases
- [ ] Verify effectiveness tracking

### Step 5: Documentation & Examples (1 day)
- [ ] Update agent docstrings
- [ ] Create usage examples
- [ ] Document integration architecture
- [ ] Create Phase 2 completion report

---

## Success Criteria

- [ ] QualityControllerAgent successfully detects weak areas
- [ ] SkillGeneratorAgent generates skills for detected weaknesses
- [ ] LearningAgent personalizes skill recommendations
- [ ] Skills applied and tracked for effectiveness
- [ ] All integration tests passing (10+ tests)
- [ ] Cross-agent communication working
- [ ] No regressions in existing agent functionality
- [ ] Black formatting: 100% compliant
- [ ] MyPy: 0 errors
- [ ] Test coverage: 70%+ for new code

---

## Phase 2 Deliverables

**Files to Create/Modify**:
- `src/socratic_agents/agents/quality_controller.py` (enhance)
- `src/socratic_agents/agents/learning_agent.py` (enhance)
- `src/socratic_agents/integrations/skill_orchestrator.py` (new)
- `tests/integration/test_skill_integration.py` (new)

**Total LOC**: ~400
- QualityController enhancements: ~100 LOC
- LearningAgent enhancements: ~120 LOC
- SkillOrchestrator: ~80 LOC
- Integration tests: ~120 LOC

**Commits Expected**: 4-5
- Agent enhancements
- Orchestrator implementation
- Integration tests
- Documentation

---

## Next: Phase 3 (Learning & Feedback)

After Phase 2 completes:
1. Advanced effectiveness tracking
2. Skill recommendation learning
3. Automatic optimization
4. Metrics & analytics dashboard

---

**Status**: 🚀 READY TO IMPLEMENT
**Next Step**: Enhance QualityControllerAgent
