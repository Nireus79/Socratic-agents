# LearningAgent

**Continuous learning analytics, personalization, and performance optimization.**

## Overview

The LearningAgent provides comprehensive learning analytics and personalization. It tracks user interactions, builds learning profiles, detects learning patterns, provides personalized recommendations, and measures learning effectiveness. It integrates with the socratic-learning library to provide sophisticated analytics.

## Key Capabilities

### 1. **Learning Analytics**
- Track user interactions and engagement
- Measure learning progress and milestones
- Analyze learning patterns and trends
- Calculate learning velocity and retention

### 2. **User Profiling**
- Build comprehensive user learning profiles
- Track learning styles and preferences
- Identify knowledge gaps
- Monitor skill development

### 3. **Personalization**
- Generate personalized learning recommendations
- Adapt difficulty levels based on performance
- Suggest optimal learning sequences
- Customize question and content delivery

### 4. **Pattern Detection**
- Identify learning patterns
- Detect knowledge gaps
- Find concept relationships
- Recognize misconceptions

### 5. **Performance Tracking**
- Measure question effectiveness
- Track answer quality
- Monitor engagement metrics
- Assess readiness for advancement

## Usage

### Basic: Track Learning Interaction

```python
from socratic_agents import LearningAgent

learner = LearningAgent()

# Track a learning interaction
result = learner.process({
    "action": "track_interaction",
    "user_id": "user_123",
    "interaction_type": "question_answered",
    "topic": "Python recursion",
    "success": True,
    "time_spent": 120  # seconds
})

print(f"Interaction tracked: {result['interaction_id']}")
```

### Intermediate: Get User Learning Profile

```python
# Get comprehensive learning profile
profile_result = learner.process({
    "action": "get_profile",
    "user_id": "user_123"
})

print("User Profile:")
print(f"  Total Questions: {profile_result['total_questions']}")
print(f"  Success Rate: {profile_result['success_rate']}%")
print(f"  Average Time: {profile_result['avg_time']}s")
print(f"  Topics Learned: {profile_result['topics_learned']}")
```

### Advanced: Get Personalized Recommendations

```python
# Get learning recommendations
recommendations = learner.process({
    "action": "personalize_learning",
    "user_id": "user_123",
    "next_topics": ["data_structures", "algorithms"],
    "difficulty_adjustment": "auto"
})

print("Recommended Learning Path:")
for rec in recommendations["learning_path"]:
    print(f"  - {rec['topic']} at {rec['difficulty']} level")

print(f"Estimated Time: {recommendations['estimated_hours']} hours")
```

## Request Format

### action: `track_interaction`
Track a learning interaction or event.

```python
request = {
    "action": "track_interaction",
    "user_id": "user_123",                        # Required
    "interaction_type": "question_answered",      # Required
    "topic": "recursion",                         # Required
    "success": True,                              # Required
    "time_spent": 120,                            # Optional: seconds
    "difficulty": "intermediate",                 # Optional
    "response_quality": 0.85                      # Optional: 0.0-1.0
}
```

**Returns:**
```python
{
    "status": "success",
    "interaction_id": "int_123",
    "user_id": "user_123",
    "timestamp": "2026-04-07T10:30:00Z",
    "learning_progress": 0.65,
    "mastery_level": "developing"
}
```

### action: `get_profile`
Retrieve comprehensive user learning profile.

```python
request = {
    "action": "get_profile",
    "user_id": "user_123"                         # Required
}
```

**Returns:**
```python
{
    "status": "success",
    "user_id": "user_123",
    "profile": {
        "total_interactions": 150,
        "total_questions": 120,
        "success_rate": 78.5,
        "average_time": 95,  # seconds
        "topics_learned": ["recursion", "sorting", "searching"],
        "current_level": "intermediate",
        "learning_style": "practical",
        "preferred_difficulty": "medium"
    },
    "progress": {
        "overall_progress": 0.65,
        "topic_progress": {
            "recursion": 0.85,
            "sorting": 0.70,
            "searching": 0.60
        }
    }
}
```

### action: `personalize_learning`
Get personalized learning path and recommendations.

```python
request = {
    "action": "personalize_learning",
    "user_id": "user_123",                        # Required
    "next_topics": ["algorithms", "data_structures"],  # Optional
    "difficulty_adjustment": "auto"               # Optional: auto|increase|decrease
}
```

**Returns:**
```python
{
    "status": "success",
    "user_id": "user_123",
    "learning_path": [
        {
            "sequence": 1,
            "topic": "Big O Notation",
            "difficulty": "beginner",
            "estimated_time": 30,
            "prerequisite_topics": []
        },
        {
            "sequence": 2,
            "topic": "Common Algorithms",
            "difficulty": "intermediate",
            "estimated_time": 60,
            "prerequisite_topics": ["Big O Notation"]
        }
    ],
    "estimated_hours": 2.5,
    "recommendations": [
        "Focus on problem-solving skills",
        "Practice more coding exercises"
    ]
}
```

### action: `detect_patterns`
Identify learning patterns and knowledge gaps.

```python
request = {
    "action": "detect_patterns",
    "user_id": "user_123"                         # Required
}
```

**Returns:**
```python
{
    "status": "success",
    "patterns": [
        {
            "pattern": "slow_on_recursion",
            "confidence": 0.85,
            "description": "User takes longer to answer recursion questions"
        }
    ],
    "knowledge_gaps": [
        {
            "topic": "tail_recursion",
            "gap_severity": "high",
            "recommended_action": "Review tail recursion concepts"
        }
    ],
    "strengths": ["mathematical_thinking", "debugging"]
}
```

### action: `measure_effectiveness`
Evaluate effectiveness of learning content.

```python
request = {
    "action": "measure_effectiveness",
    "user_id": "user_123",
    "content_id": "question_456"                  # Optional
}
```

**Returns:**
```python
{
    "status": "success",
    "effectiveness_score": 0.87,
    "metrics": {
        "correct_answers": 18,
        "total_attempts": 20,
        "average_time": 120,
        "retention": 0.90,
        "engagement": 0.85
    }
}
```

### action: `track_feedback`
Track user feedback on learning content.

```python
request = {
    "action": "track_feedback",
    "user_id": "user_123",
    "skill_id": "skill_123",
    "feedback": "helpful"  # helpful|confusing|too_easy|too_hard
}
```

**Returns:**
```python
{
    "status": "success",
    "feedback_recorded": True,
    "impact_on_recommendations": "Updated"
}
```

## Configuration

### Initialization

```python
from socratic_agents import LearningAgent

# Basic initialization
learner = LearningAgent()

# With LLM client
from socrates_nexus import LLMClient
llm = LLMClient(provider="anthropic")
learner = LearningAgent(llm_client=llm)
```

### Configuration Options

| Option | Type | Default | Purpose |
|--------|------|---------|---------|
| `llm_client` | LLMClient | None | LLM for recommendations |
| `tracking_enabled` | bool | True | Enable interaction tracking |
| `analytics_enabled` | bool | True | Enable analytics |
| `personalization_enabled` | bool | True | Enable personalization |
| `recommendation_threshold` | float | 0.6 | Confidence threshold for recommendations |

## Learning Levels

### Difficulty Levels
- **Beginner** - Foundation concepts, simple examples
- **Intermediate** - Applied concepts, moderate complexity
- **Advanced** - Complex applications, optimization
- **Expert** - Advanced techniques, edge cases

### Mastery Levels
| Level | Range | Description |
|-------|-------|-------------|
| Novice | 0-25% | Learning basics |
| Developing | 25-50% | Building competence |
| Proficient | 50-75% | Solid understanding |
| Advanced | 75-90% | High proficiency |
| Expert | 90-100% | Mastery |

### Learning Styles
- **Visual** - Diagrams, flowcharts, visual examples
- **Auditory** - Explanations, discussions, verbal
- **Reading/Writing** - Text, documentation, notes
- **Kinesthetic** - Hands-on, code exercises, practice
- **Practical** - Real-world applications, projects

## Metrics & Tracking

### Interaction Types
- `question_answered` - User answered a question
- `lesson_completed` - User finished a lesson
- `exercise_solved` - User solved a coding exercise
- `concept_mastered` - User demonstrated mastery
- `skill_applied` - User applied a learned skill

### Performance Metrics
- **Success Rate** - Percentage of correct attempts
- **Retention** - Knowledge retention over time
- **Engagement** - Time spent and participation
- **Velocity** - Speed of learning new concepts
- **Consistency** - Regular participation pattern

## Best Practices

### 1. **Track Regularly**
```python
# Track every learning interaction
def on_question_answered(user_id, question_id, success, time_spent):
    learner.process({
        "action": "track_interaction",
        "user_id": user_id,
        "interaction_type": "question_answered",
        "topic": get_question_topic(question_id),
        "success": success,
        "time_spent": time_spent
    })
```

### 2. **Personalize Learning Paths**
```python
# Get personalized recommendations
recommendations = learner.process({
    "action": "personalize_learning",
    "user_id": user_id,
    "next_topics": upcoming_topics
})

# Present in recommended order
for topic in recommendations["learning_path"]:
    present_topic(topic)
```

### 3. **Adjust Difficulty Dynamically**
```python
# Monitor performance and adjust
profile = learner.process({
    "action": "get_profile",
    "user_id": user_id
})

if profile["success_rate"] > 85:
    difficulty = "increase"
elif profile["success_rate"] < 60:
    difficulty = "decrease"
else:
    difficulty = "maintain"

next_question = generate_question(difficulty)
```

### 4. **Analyze Patterns**
```python
# Regular pattern analysis
patterns = learner.process({
    "action": "detect_patterns",
    "user_id": user_id
})

# Address knowledge gaps
for gap in patterns["knowledge_gaps"]:
    create_remedial_content(gap)
```

## Integration Examples

### With SocraticCounselor
```python
from socratic_agents import SocraticCounselor, LearningAgent

counselor = SocraticCounselor()
learner = LearningAgent()

# Generate question
q_result = counselor.guide(topic)

# Track interaction
learner.process({
    "action": "track_interaction",
    "user_id": user_id,
    "interaction_type": "question_answered",
    "topic": topic,
    "success": was_correct
})

# Get personalized next topic
recommendations = learner.process({
    "action": "personalize_learning",
    "user_id": user_id
})

next_topic = recommendations["learning_path"][0]
```

### With QualityController
```python
from socratic_agents import LearningAgent, QualityController

learner = LearningAgent()
quality = QualityController()

# Get user profile
profile = learner.process({
    "action": "get_profile",
    "user_id": user_id
})

# Assess readiness for advanced content
maturity = quality.process({
    "action": "assess_maturity",
    "maturity_data": {
        "current_phase": "implementation",
        "completion_percent": profile["overall_progress"] * 100
    }
})
```

### With SkillGeneratorAgent
```python
from socratic_agents import LearningAgent, SkillGeneratorAgent

learner = LearningAgent()
skill_gen = SkillGeneratorAgent()

# Detect learning gaps
patterns = learner.process({
    "action": "detect_patterns",
    "user_id": user_id
})

# Generate skills for gaps
for gap in patterns["knowledge_gaps"]:
    skill = skill_gen.process({
        "action": "generate",
        "topic": gap["topic"]
    })

# Track skill application
learner.process({
    "action": "track_feedback",
    "user_id": user_id,
    "skill_id": skill["skill_id"],
    "feedback": "helpful"
})
```

## Common Patterns

### Pattern 1: Adaptive Learning
```python
def adaptive_question_difficulty(user_id, topic):
    profile = learner.process({
        "action": "get_profile",
        "user_id": user_id
    })

    topic_progress = profile["progress"]["topic_progress"].get(topic, 0)

    if topic_progress < 0.5:
        difficulty = "beginner"
    elif topic_progress < 0.75:
        difficulty = "intermediate"
    else:
        difficulty = "advanced"

    return generate_question(topic, difficulty)
```

### Pattern 2: Learning Analytics
```python
def get_learning_summary(user_id):
    profile = learner.process({
        "action": "get_profile",
        "user_id": user_id
    })

    patterns = learner.process({
        "action": "detect_patterns",
        "user_id": user_id
    })

    return {
        "progress": profile["progress"]["overall_progress"],
        "success_rate": profile["profile"]["success_rate"],
        "patterns": patterns["patterns"],
        "gaps": patterns["knowledge_gaps"]
    }
```

### Pattern 3: Personalized Recommendations
```python
def get_next_learning_step(user_id, available_topics):
    recommendations = learner.process({
        "action": "personalize_learning",
        "user_id": user_id,
        "next_topics": available_topics
    })

    return recommendations["learning_path"][0]
```

## Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| Track interaction | <100ms | Async tracking |
| Get profile | 1-2s | Aggregates data |
| Detect patterns | 2-5s | Analysis |
| Get recommendations | 2-4s | May use LLM |
| Measure effectiveness | <500ms | Calculation |

## Troubleshooting

### Inaccurate Profile
- Ensure interactions are being tracked
- Verify user_id is consistent
- Check interaction data is complete
- Allow time for pattern detection

### Poor Recommendations
- Check user has sufficient history
- Verify learning preferences are set
- Review feedback tracking
- May need more interaction data

### Performance Issues
- Use async tracking
- Cache profile data
- Batch analytics calculations
- Consider data cleanup

---

**Related Agents:** SocraticCounselor, QualityController, SkillGeneratorAgent

**Next:** [ProjectManager](./project_manager.md)
