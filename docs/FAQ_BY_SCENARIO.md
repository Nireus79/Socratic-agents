# Socratic Agents - FAQ by Scenario

## Using Socratic Counselor

How do I use the counselor for learning?

```python
from socratic_agents import SocraticCounselor
from socrates_nexus import LLMClient

llm = LLMClient(provider="anthropic", model="claude-opus")
counselor = SocraticCounselor(llm_client=llm)

result = counselor.process({
    "action": "guide",
    "topic": "machine learning",
    "level": "beginner"
})

print(result["questions"])
```

## Using Code Generator

How do I generate code?

```python
from socratic_agents import CodeGenerator

generator = CodeGenerator(llm_client=llm)
result = generator.process({
    "prompt": "Create a sorting algorithm",
    "language": "python"
})

print(result["code"])
```

## Orchestrating Agents

How do I run multiple agents together?

```python
from socratic_agents import AgentOrchestrator

orchestrator = AgentOrchestrator(
    llm_client=llm,
    agents=["counselor", "code_generator", "validator"]
)

result = orchestrator.execute_workflow(
    task="Generate and test a function",
    agents=["code_generator", "validator"]
)
```

## Adaptive Skill Generation

How do I generate skills?

```python
from socratic_agents import SkillGeneratorAgent

skill_gen = SkillGeneratorAgent()
result = skill_gen.process({
    "action": "generate",
    "maturity_data": {...},
    "learning_data": {...}
})
```
