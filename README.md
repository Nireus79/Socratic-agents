# Socratic Agents

⚠️ **SOCRATES-ONLY LIBRARY** - This library is designed exclusively for use within the Socrates monolith and is NOT suitable for standalone use.

---

## Overview

**Socratic Agents** is a collection of 19+ specialized agents that power the Socrates AI platform. These agents handle complex tasks like Socratic questioning, code generation, project management, quality control, learning, and conflict resolution.

**Key Point**: All agents in this library require the Socrates monolith to be installed locally. They depend on `socratic_system` internals and cannot function independently.

## Requirements

- **Socrates Monolith** - Must be installed locally
- **socratic_system** - Must be available in Python path
- **Python 3.9+**

### Why Socrates-Only?

The agents in this library are tightly integrated with Socrates internals:
- Access to centralized database
- Vector database integration
- Unified LLM client orchestration
- Shared user and project context
- Maturity tracking and workflow optimization

**After the Socrates architecture redesign**, many of these agents will be refactored for independence.

---

## Installation

### Via PyPI (Recommended)

Socratic-agents v0.3.1 is published to PyPI for use with Socrates v2.0.0+:

```bash
pip install socratic-agents==0.3.1
```

This requires Socrates v2.0.0+ to be installed, as the library depends on the Socrates monolith.

### Within Socrates Monolith (Development)

For development work within the Socrates monolith:

```bash
cd Socratic-agents
pip install -e .
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

### Socrates-Integrated Design

All agents are designed to work within the Socrates orchestration framework:

```
┌─────────────────────────────────────┐
│     Socrates Monolith               │
├─────────────────────────────────────┤
│  AgentOrchestrator                  │
│  ├─ Database Connection             │
│  ├─ Vector Database                 │
│  ├─ LLM Client (Multi-provider)     │
│  └─ Event System                    │
├─────────────────────────────────────┤
│  Socratic Agents (19+)              │
│  ├─ Dialogue Agents                 │
│  ├─ Project Agents                  │
│  ├─ Code Agents                     │
│  ├─ Learning Agents                 │
│  └─ System Agents                   │
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
cd Socratic-agents

# Run all tests (requires Socrates environment)
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/socratic_agents --cov-report=html

# Run specific test category
pytest -m unit
pytest -m integration
```

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
