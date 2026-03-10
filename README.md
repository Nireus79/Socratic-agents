# Socratic Agents

Production-grade multi-agent orchestration system with 19 specialized agents for AI workflows. Extracted from the Socrates AI platform and optimized for standalone use. Includes adaptive skill generation for intelligent agent optimization.

[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![PyPI Status](https://img.shields.io/badge/PyPI-Coming%20Soon-blue.svg)](https://pypi.org/)

## Overview

Socratic Agents provides a comprehensive agent orchestration framework with 19 pre-built agents designed to handle complex AI workflows. Each agent specializes in a specific capability (code generation, analysis, learning, coordination, skill generation, etc.) and can work independently or be orchestrated together.

### The 19 Agents

**Core Agents**:
1. **Socratic Counselor** - Guided learning and interactive problem-solving
2. **Code Generator** - Intelligent code generation and completion
3. **Code Validator** - Validation and testing of generated code
4. **Knowledge Manager** - Knowledge base management and RAG integration
5. **Learning Agent** - Continuous improvement and pattern learning
6. **Skill Generator** - Adaptive skill generation for agent optimization

**Coordination Agents**:
7. **Multi-LLM Coordinator** - Provider switching and model orchestration
8. **Project Manager** - Project scope and timeline management
9. **Quality Controller** - Quality assurance and testing orchestration
10. **Context Analyzer** - Context understanding and management

**Data Agents**:
11. **Document Processor** - Document parsing and processing
12. **GitHub Sync Handler** - GitHub integration and synchronization
13. **System Monitor** - System health and performance monitoring
14. **User Manager** - User context and preferences management

**Analysis Agents**:
15. **Conflict Detector** - Conflict detection and resolution
16. **Knowledge Analyzer** - Knowledge analysis and insights
17. **Document Context Analyzer** - Document semantic analysis
18. **Note Manager** - Notes and memory management
19. **Question Queue Agent** - Question queuing and prioritization

## Key Features

- **19 Pre-built Agents** - Specialized agents for different tasks including adaptive skill generation
- **Agent Orchestration** - Coordinate multiple agents for complex workflows
- **Async Support** - Full async/await support for non-blocking operations
- **Extensible Design** - Create custom agents by extending BaseAgent
- **Framework Integration** - Openclaw skills and LangChain tools
- **Socrates Nexus Integration** - Multi-provider LLM support
- **Production Ready** - Type hints, comprehensive testing, documentation
- **Part of Socrates Ecosystem** - Works with RAG, Analyzer, and other packages

## Part of the Socrates Ecosystem

**Socratic Agents** is a core component of the [Socrates Ecosystem](https://github.com/Nireus79/Socrates-nexus/blob/main/ECOSYSTEM.md) - a collection of production-grade AI packages that work together.

### How It Uses Socrates Nexus
- LLM calls within agents use Socrates Nexus for multi-provider support
- Works with any Socrates Nexus provider (Claude, GPT-4, Gemini, Ollama)
- Automatic provider switching for cost optimization and reliability

### Related Packages in the Ecosystem
- **[Socrates Nexus](https://github.com/Nireus79/Socrates-nexus)** (Dependency) - Universal LLM client
- **[Socratic RAG](https://github.com/Nireus79/Socratic-rag)** - Knowledge retrieval and management
- **[Socratic Analyzer](https://github.com/Nireus79/Socratic-analyzer)** - Code analysis
- **[Socratic Workflow](https://github.com/Nireus79/Socratic-workflow)** (Coming Q4 2026) - Workflow optimization
- **[Socratic Knowledge](https://github.com/Nireus79/Socratic-knowledge)** (Coming Q1 2027) - Enterprise knowledge

👉 **Full ecosystem guide**: See [Socrates Nexus ECOSYSTEM.md](https://github.com/Nireus79/Socrates-nexus/blob/main/ECOSYSTEM.md)

📊 **Track development**: View the [Socrates Ecosystem Roadmap](https://github.com/users/Nireus79/projects/3) to see progress across all packages

## Installation

```bash
# Basic installation
pip install socratic-agents

# With Openclaw support
pip install socratic-agents[openclaw]

# With LangChain support
pip install socratic-agents[langchain]

# With all features
pip install socratic-agents[all]

# Development
pip install socratic-agents[dev]
```

## Quick Start

### Basic Agent Usage

```python
from socratic_agents import SocraticCounselor, MultiLLMAgent
from socrates_nexus import LLMClient

# Create LLM client
llm_client = LLMClient(provider="anthropic", model="claude-opus")

# Create agents
counselor = SocraticCounselor(llm_client)
coordinator = MultiLLMAgent(llm_client)

# Use agent
response = counselor.guide("Help me understand recursion")
print(response)
```

### Multi-Agent Workflow

```python
from socratic_agents import AgentOrchestrator
from socrates_nexus import LLMClient

# Create orchestrator
orchestrator = AgentOrchestrator(
    llm_client=LLMClient(provider="anthropic"),
    agents=["counselor", "code_generator", "validator"]
)

# Execute workflow
result = orchestrator.execute_workflow(
    task="Generate and test a Python function for fibonacci",
    agents=["code_generator", "validator"]
)

print(result)
```

### Adaptive Skill Generation

Generate and apply adaptive skills to optimize agent behavior based on maturity and learning patterns:

```python
from socratic_agents import SkillGeneratorAgent

# Create skill generator
skill_gen = SkillGeneratorAgent()

# Generate skills based on maturity and learning data
result = skill_gen.process({
    "action": "generate",
    "maturity_data": {
        "current_phase": "discovery",
        "completion_percent": 35,
        "weak_categories": ["problem_definition"],
        "category_scores": {
            "problem_definition": 0.3,
            "scope": 0.8
        }
    },
    "learning_data": {
        "learning_velocity": "medium",
        "engagement_score": 0.75
    }
})

# Get recommended skills
for rec in result["recommendations"]:
    skill = rec["skill"]
    print(f"Skill: {skill['id']}")
    print(f"Priority: {rec['priority']}")
    print(f"Expected Impact: {rec['expected_impact']:.0%}")
```

### Openclaw Integration

```python
from socratic_agents.integrations.openclaw import SocraticAgentsSkill

# Use in Openclaw
skill = SocraticAgentsSkill()
result = skill.generate_code("Create a sorting algorithm")
```

### LangChain Integration

```python
from socratic_agents.integrations.langchain import SocraticAgentsTool
from langchain.agents import AgentType, initialize_agent
from langchain.llms import OpenAI

# Create tool
agents_tool = SocraticAgentsTool()

# Use in agent
tools = [agents_tool]
agent = initialize_agent(
    tools,
    OpenAI(temperature=0),
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)
```

## Architecture

### Core Components

**BaseAgent** - Abstract base class for all agents with:
- LLM integration via Socrates Nexus
- Async support
- Error handling
- Logging and monitoring

**Agent Categories**:
- **Execution Agents** - Execute specific tasks (CodeGenerator, Validator)
- **Coordination Agents** - Orchestrate other agents (MultiLLMCoordinator, ProjectManager)
- **Analysis Agents** - Analyze information (ConflictDetector, KnowledgeAnalyzer)
- **Management Agents** - Manage resources (UserManager, SystemMonitor)
- **Optimization Agents** - Optimize agent behavior (SkillGenerator)

**AgentOrchestrator** - Coordinates multiple agents:
- Dependency resolution
- Workflow execution
- Context passing between agents
- Error handling and recovery

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/socratic_agents

# Run specific test category
pytest -m unit
pytest -m integration

# Run without slow tests
pytest -m "not slow"
```

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - See [LICENSE](LICENSE) for details.

## Support

- GitHub Issues: https://github.com/Nireus79/Socratic-agents/issues
- Documentation: https://github.com/Nireus79/Socratic-agents/tree/main/docs
- Socrates Ecosystem: https://github.com/Nireus79/Socrates-nexus/blob/main/ECOSYSTEM.md

---

**Built with ❤️ as part of the Socrates ecosystem**

Made by [@Nireus79](https://github.com/Nireus79)
