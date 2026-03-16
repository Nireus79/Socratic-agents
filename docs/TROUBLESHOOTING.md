# Socratic Agents - Troubleshooting

## Agent Issues

### Agent not producing output

Cause: LLM client not configured

Solution: Pass LLM client
```python
from socrates_nexus import LLMClient

llm = LLMClient(provider="anthropic")
agent = CodeGenerator(llm_client=llm)
```

### Slow agent execution

Cause: Slow LLM provider

Solution: Use faster model
```python
llm = LLMClient(provider="openai", model="gpt-3.5-turbo")
```

## Orchestration Issues

### Agents not communicating

Cause: Context not passed between agents

Solution: Use AgentOrchestrator
```python
from socratic_agents import AgentOrchestrator

orch = AgentOrchestrator(llm_client=llm)
result = orch.execute_workflow(task, agents)
```

### Dependency resolution failing

Cause: Invalid agent dependencies

Solution: Check agent list and dependencies
