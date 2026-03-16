# Socratic Agents - Integration Guide

## Socrates Nexus Integration

All agents use Socrates Nexus for LLM calls:

```python
from socratic_agents import CodeGenerator
from socrates_nexus import LLMClient

llm = LLMClient(provider="anthropic", model="claude-opus")
generator = CodeGenerator(llm_client=llm)
```

## Openclaw Integration

```python
from socratic_agents.integrations.openclaw import SocraticAgentsSkill

skill = SocraticAgentsSkill()
result = skill.generate_code("Create a function")
```

## LangChain Integration

```python
from socratic_agents.integrations.langchain import SocraticAgentsTool

tool = SocraticAgentsTool()
# Use in LangChain agent
```

## Multi-Agent Workflows

```python
from socratic_agents import AgentOrchestrator

orchestrator = AgentOrchestrator(llm_client=llm)
result = orchestrator.execute_workflow(
    task="Complex task",
    agents=["agent1", "agent2", "agent3"]
)
```
