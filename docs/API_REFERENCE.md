# Socratic Agents - API Reference

## BaseAgent

Base class for all agents.

```python
class BaseAgent:
    def __init__(self, llm_client=None, name=None)
    def process(self, config: Dict) -> Dict
    async def async_process(self, config: Dict) -> Dict
```

## The 19 Agents

### Core Agents
- SocraticCounselor
- CodeGenerator
- CodeValidator
- KnowledgeManager
- LearningAgent
- SkillGeneratorAgent

### Coordination Agents
- MultiLLMCoordinator
- ProjectManager
- QualityController
- ContextAnalyzer

### Data Agents
- DocumentProcessor
- GitHubSyncHandler
- SystemMonitor
- UserManager

### Analysis Agents
- ConflictDetector
- KnowledgeAnalyzer
- DocumentContextAnalyzer
- NoteManager
- QuestionQueueAgent

## AgentOrchestrator

```python
class AgentOrchestrator:
    def __init__(self, llm_client, agents=None)
    def execute_workflow(self, task, agents) -> Dict
    async def execute_workflow_async(self, task, agents) -> Dict
```

## SkillGeneratorAgent

```python
skill_gen = SkillGeneratorAgent()
result = skill_gen.process({
    "action": "generate",
    "maturity_data": {...},
    "learning_data": {...}
})
```
