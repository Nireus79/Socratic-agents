# Socratic Agents

[![PyPI](https://img.shields.io/pypi/v/socratic-agents.svg)](https://pypi.org/project/socratic-agents/)
[![Downloads](https://img.shields.io/pypi/dm/socratic-agents.svg)](https://pypi.org/project/socratic-agents/)
[![GitHub](https://img.shields.io/github/stars/Nireus79/Socratic-agents.svg?style=social)](https://github.com/Nireus79/Socratic-agents)
[![License](https://img.shields.io/github/license/Nireus79/Socratic-agents.svg)](LICENSE)


**Socratic Agents** - Independent multi-agent framework designed for standalone use with optional Constitutional AI governance integration.

---

## Overview

**Socratic Agents** is a collection of 19+ specialized agents that handle complex tasks like Socratic questioning, code generation, project management, quality control, learning, and conflict resolution.

The library uses **service-based architecture with dependency injection** - agents are decoupled from any monolithic system, enabling flexible use in diverse deployment scenarios.

**Key Features**:
- Service-based architecture with dependency injection
- Multi-agent orchestration with event-driven messaging via AgentBus
- Optional Constitutional AI governance (socratic-morality integration)
- Comprehensive agent implementations ready to use
- REST API for external access
- Clean service interfaces for custom implementations

## Requirements

- **Python 3.10+** (recommended 3.11 or 3.12)
- **pydantic>=2.0** - Data validation and modeling

### Optional Dependencies

- **FastAPI** - For REST API support (`pip install socratic-agents[api]`)
- **socratic-morality** - For Constitutional AI governance features (governance module)
- **Anthropic SDK** - For Claude LLM integration

---

## Installation

### Via PyPI (Recommended)

Install the latest version from PyPI:

```bash
pip install socratic-agents
```

For REST API support, install with the api extra:

```bash
pip install socratic-agents[api]
```

For governance features, install with the governance extra:

```bash
pip install socratic-agents[governance]
```

### Development Installation

For development or local testing:

```bash
cd Socratic-agents
pip install -e ".[dev]"  # Includes all dev dependencies
```

---

## The 19+ Agents

### Core Dialogue Agents
- **SocraticCounselorAgent** - Guides users through Socratic questioning with full dialogue orchestration
- **QuestionQueueAgent** - Manages and prioritizes question queues

### Project & Workflow Agents
- **ProjectManagerAgent** - Manages project lifecycle (creation, loading, collaboration)
- **QualityControllerAgent** - Orchestrates maturity tracking and quality assurance
- **WorkflowOptimizationAgent** - Optimizes workflow paths and decision strategies

### Code & Technical Agents
- **CodeGeneratorAgent** - Generates code based on project context
- **CodeValidationAgent** - Validates and tests code
- **DocumentProcessorAgent** - Processes and imports project documents
- **GitHubSyncHandler** - Handles GitHub repository synchronization

### Learning & Knowledge Agents
- **UserLearningAgent** - Tracks user behavior and learning patterns
- **KnowledgeManagerAgent** - Manages knowledge base enrichment
- **KnowledgeAnalysisAgent** - Analyzes and extracts knowledge insights
- **ConflictDetectorAgent** - Detects and resolves conflicts in specifications

### User & System Agents
- **UserManagerAgent** - Manages user accounts and preferences
- **SystemMonitorAgent** - Monitors system health and token usage
- **ContextAnalyzerAgent** - Analyzes and manages project context
- **MultiLLMAgent** - Coordinates multiple LLM providers

### Note & Data Agents
- **NoteManagerAgent** - Manages project notes and documentation
- **DocumentContextAnalyzer** - Analyzes semantic content of documents

---

## Architecture

### Architecture

Agents are organized by function and work together through the AgentOrchestrator:

```
┌─────────────────────────────────────┐
│  AgentOrchestrator                  │
│  ├─ Event System                    │
│  ├─ LLM Client (Multi-provider)     │
│  └─ Message Routing (AgentBus)      │
├─────────────────────────────────────┤
│  Socratic Agents (19+)              │
│  ├─ Dialogue Agents                 │
│  ├─ Project Agents                  │
│  ├─ Code Agents                     │
│  ├─ Learning Agents                 │
│  └─ System Agents                   │
├─────────────────────────────────────┤
│  Constitutional AI Governance       │
│  └─ Via socratic-morality library   │
└─────────────────────────────────────┘
```

### Key Features

- **Agent Orchestration** - Coordinated agent workflows through AgentOrchestrator
- **Async Support** - Full async/await support for non-blocking operations
- **Event System** - Real-time event emission for status tracking
- **Database Integration** - Direct access to Socrates database
- **Vector DB Access** - Knowledge and context retrieval
- **Multi-Provider LLM** - Via Socratic Nexus integration
- **Type Hints** - Full Python type annotations
- **Comprehensive Logging** - Detailed operation logging

### Phase 3 Features - Constitutional AI & Governance

- **GovernedAgent** - Wraps agents with constitutional governance checks
- **Agent Bus** - Inter-agent message routing with history tracking (1000 message buffer)
- **Governance Integration** - Uses socratic-morality for ethical decision making
- **REST API** - FastAPI endpoints for governance, agents, and precedent lookup
- **YAML Configuration** - Constitutional governance rules and agent configuration

---

## Quick Reference

### Initialize Agents Within Socrates

```python
from socratic_agents import AgentOrchestrator, SocraticCounselorAgent

# Create orchestrator (within Socrates context)
orchestrator = AgentOrchestrator(
    database=socrates_db,
    vector_db=socrates_vector_db,
    claude_client=socrates_llm_client
)

# Create and use specific agent
counselor = SocraticCounselorAgent(orchestrator)
result = counselor.process({
    "action": "generate_question",
    "project": project_context,
    "current_user": user_id
})
```

### Available Actions Vary by Agent

Each agent has specific actions. See individual agent documentation for details.

---

## Testing

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run all tests
pytest tests/ -v --cov=src/socratic_agents

# Run with coverage report
pytest tests/ --cov=src/socratic_agents --cov-report=html

# Run specific test category
pytest -m unit
pytest -m integration
```

### Test Coverage

Current test coverage: 81%+ across all agent implementations.

---

## Future: Post-Architecture Redesign

After the Socrates architecture is redesigned and optimized, the following changes are planned:

1. **Independent Agents** - Some agents will be refactored as independent packages
2. **Decoupled Dependencies** - Reduced reliance on Socrates internals
3. **Modular Publishing** - Agent libraries published separately to PyPI
4. **Standalone Mode** - Core agents usable without full Socrates installation

Current independent Socratic libraries:
- **socratic-analyzer** - Code analysis (standalone)
- **socratic-learning** - Learning algorithms (standalone)
- **Socratic-workflow** - Workflow definitions (standalone)
- **Socratic-maturity** - Maturity tracking (standalone)
- And 4+ others...

---

## Architecture Documentation

**Status**: Currently in integration phase within Socrates monolith.

For detailed agent documentation, see the `docs/` directory (available after Socrates publication).

---

## Contributing

This library is maintained as part of the Socrates monolith. Contributions should follow Socrates contribution guidelines.

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

**This library is part of the Socrates AI platform**

Made by [@Nireus79](https://github.com/Nireus79)


---

## Part of Socrates AI Ecosystem

This package is a component of [**Socrates AI**](https://github.com/Nireus79/Socrates), a production-ready platform for building intelligent multi-agent systems with constitutional governance.

### Use This Package Standalone:
```bash
pip install socratic-agents
```

### Or As Part of Socrates Platform:
```bash
pip install socrates-ai  # Includes 37+ modules + all 11 packages
```

### Integration Example:

See the [**Socrates ECOSYSTEM.md**](https://github.com/Nireus79/Socrates/blob/main/ECOSYSTEM.md#layer-2-specialized-libraries) for detailed integration examples showing how to use socratic-agents with other Socratic packages.

**Related packages you might use together:**
- See [Complete Package Map](https://github.com/Nireus79/Socrates/blob/main/ECOSYSTEM.md)

### More Information:
- 📖 [Full Socrates Documentation](https://github.com/Nireus79/Socrates/tree/main/docs)
- 🏗️ [Complete Architecture Guide](https://github.com/Nireus79/Socrates/blob/main/ECOSYSTEM.md)
- 💬 [Socrates Discussions](https://github.com/Nireus79/Socrates/discussions)

---
