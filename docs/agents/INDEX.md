# Socratic Agents Documentation

Complete guide to all agents in the Socratic Agents framework. Each agent is a specialized component designed to handle specific tasks in educational and development workflows.

## Quick Overview

The Socratic Agents framework includes 23 specialized agents organized into functional categories:

### Core Dialogue & Learning
- **[SocraticCounselor](./socratic_counselor.md)** - Complete Socratic dialogue orchestration
- **[LearningAgent](./learning_agent.md)** - Continuous learning analytics and personalization
- **[QuestionQueueAgent](./question_queue_agent.md)** - Manages question queues and delivery

### Code & Quality
- **[CodeGenerator](./code_generator.py.md)** - LLM-powered code generation
- **[CodeValidator](./code_validator.md)** - Code validation and quality checking
- **[QualityController](./quality_controller.md)** - Quality assurance and testing
- **[SkillGeneratorAgent](./skill_generator_agent.md)** - AI-powered skill generation

### Knowledge & Context
- **[KnowledgeManager](./knowledge_manager.md)** - Knowledge base management
- **[KnowledgeAnalysis](./knowledge_analysis.md)** - Knowledge analysis and insights
- **[ContextAnalyzer](./context_analyzer.md)** - Context extraction and analysis
- **[DocumentContextAnalyzer](./document_context_analyzer.md)** - Document-specific context

### Project & Document Management
- **[ProjectManager](./project_manager.md)** - Project planning and task management
- **[DocumentProcessor](./document_processor.md)** - Document processing and analysis
- **[ProjectFileLoader](./project_file_loader.md)** - File loading and parsing
- **[NoteManager](./note_manager.md)** - Note organization and retrieval

### Integration & Infrastructure
- **[MultiLlmAgent](./multi_llm_agent.md)** - Multi-LLM orchestration
- **[ConflictDetector](./conflict_detector.md)** - Conflict detection and resolution
- **[GithubSyncHandler](./github_sync_handler.md)** - GitHub integration
- **[SystemMonitor](./system_monitor.md)** - System health monitoring
- **[UserManager](./user_manager.md)** - User management and profiles

### Advanced Features
- **[SkillGeneratorAgentV2](./skill_generator_agent_v2.md)** - Advanced skill generation

---

## Common Usage Patterns

### Pattern 1: Get Learning Guidance
```python
from socratic_agents import SocraticCounselor

counselor = SocraticCounselor()
result = counselor.guide("Python recursion", level="beginner")
```

**Uses:** SocraticCounselor, LearningAgent

### Pattern 2: Generate and Validate Code
```python
from socratic_agents import CodeGenerator, CodeValidator

generator = CodeGenerator()
validator = CodeValidator()

code = generator.process({"prompt": "factorial function"})
validation = validator.process({"code": code["code"]})
```

**Uses:** CodeGenerator, CodeValidator, QualityController

### Pattern 3: Track Learning Progress
```python
from socratic_agents import LearningAgent

learner = LearningAgent()
learner.process({"action": "track_interaction", "user_id": "user_1"})
profile = learner.process({"action": "get_profile"})
```

**Uses:** LearningAgent, UserManager

### Pattern 4: Manage Project
```python
from socratic_agents import ProjectManager

pm = ProjectManager()
project = pm.process({"action": "create", "project_name": "MyApp"})
task = pm.process({"action": "add_task", "project_id": project["id"]})
```

**Uses:** ProjectManager, DocumentProcessor

---

## Agent Architecture

### Base Agent
All agents inherit from `BaseAgent` which provides:
- `process()` - Main request handler
- `process_async()` - Async request handler
- Logging and error handling
- State management
- Lifecycle hooks

### Agent Interface

Every agent implements:
```python
def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process incoming requests with an action parameter.

    Args:
        request: {"action": "...", ...other params...}

    Returns:
        {"status": "success"|"error", ...results...}
    """
```

---

## Agent Categories by Purpose

### Educational & Learning
- **SocraticCounselor** - Interactive learning through Socratic questions
- **LearningAgent** - Personalized learning paths and analytics
- **QuestionQueueAgent** - Question management and delivery

### Development & Code
- **CodeGenerator** - Generate code from descriptions
- **CodeValidator** - Validate code quality and correctness
- **QualityController** - Quality metrics and testing
- **SkillGeneratorAgent** - Create reusable code skills

### Knowledge & Information
- **KnowledgeManager** - Store and retrieve knowledge
- **KnowledgeAnalysis** - Analyze patterns in knowledge
- **ContextAnalyzer** - Extract relevant context
- **DocumentProcessor** - Process and analyze documents

### Project Management
- **ProjectManager** - Manage projects and tasks
- **NoteManager** - Organize notes and documentation
- **ProjectFileLoader** - Load and parse project files

### System & Infrastructure
- **MultiLlmAgent** - Coordinate multiple LLM providers
- **ConflictDetector** - Detect and resolve conflicts
- **GithubSyncHandler** - GitHub integration
- **SystemMonitor** - Monitor system health
- **UserManager** - Manage user profiles

---

## Configuration & Dependencies

### Required
- Python 3.9+
- Core agent implementations in `src/socratic_agents/agents/`

### Optional Dependencies
- `socratic-learning` - Enhanced learning analytics (LearningAgent)
- `socratic-conflict` - Conflict detection (ConflictDetector)
- `socrates-maturity` - Maturity assessment (QualityController)
- `socrates-nexus` - LLM client (all agents)

---

## Best Practices

### 1. Error Handling
```python
result = agent.process(request)
if result["status"] == "error":
    error_message = result.get("message")
    # Handle error appropriately
```

### 2. Async Operations
```python
import asyncio

async def main():
    result = await agent.process_async(request)
    return result

asyncio.run(main())
```

### 3. Chaining Agents
```python
# Use output from one agent as input to another
code_result = generator.process(generator_request)
validation_result = validator.process({
    "code": code_result["code"]
})
```

### 4. Logging & Monitoring
```python
import logging

logger = logging.getLogger("socratic_agents")
logger.setLevel(logging.DEBUG)  # See agent operations

result = agent.process(request)
# Agent logs will show detailed execution trace
```

---

## Integration Points

### With Skill System
Many agents support the skill system:
- **SkillGeneratorAgent** creates skills from code
- **CodeGenerator** uses skills for code generation
- **QualityController** applies skills for improvement

### With Learning System
- **LearningAgent** tracks interaction history
- **SocraticCounselor** personalizes questions based on learning profile
- **QuestionQueueAgent** delivers questions at optimal times

### With Knowledge System
- **KnowledgeManager** stores context and information
- **ContextAnalyzer** extracts relevant knowledge
- **DocumentProcessor** indexes knowledge from documents

---

## Troubleshooting

### Agent Returns Error Status
1. Check request format - ensure `action` parameter is valid
2. Verify required parameters are present
3. Check agent logs for detailed error messages
4. See agent-specific documentation for action details

### Missing Dependencies
- Install optional dependencies if agent requires them
- Check agent documentation for dependency requirements

### Performance Issues
- Use async operations for long-running tasks
- Consider using `SystemMonitor` to track performance
- Check `QualityController` for optimization recommendations

---

## Next Steps

1. **Start with [SocraticCounselor](./socratic_counselor.md)** - Core dialogue engine
2. **Explore [CodeGenerator](./code_generator.py.md)** - Code generation capabilities
3. **Learn [LearningAgent](./learning_agent.md)** - Personalization features
4. **Review integration guides** - See how agents work together

---

## Quick Reference

| Agent | Purpose | Key Action | Status |
|-------|---------|-----------|--------|
| SocraticCounselor | Dialogue orchestration | `generate_question` | ✅ Stable |
| CodeGenerator | Code generation | `generate` | ✅ Stable |
| QualityController | Quality assurance | `check` | ✅ Stable |
| LearningAgent | Learning analytics | `track_interaction` | ✅ Stable |
| ProjectManager | Project management | `create` | ✅ Stable |
| KnowledgeManager | Knowledge base | `store` | ✅ Stable |
| ConflictDetector | Conflict resolution | `detect` | ✅ Stable |
| CodeValidator | Code validation | `validate` | ✅ Stable |
| ContextAnalyzer | Context extraction | `analyze` | ✅ Stable |
| DocumentProcessor | Document analysis | `process` | ✅ Stable |

---

*For detailed information on each agent, see the individual documentation files in this directory.*
