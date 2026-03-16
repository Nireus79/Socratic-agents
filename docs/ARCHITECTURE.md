# Socratic Agents - Architecture & System Design

## System Overview

Socratic Agents provides 19 pre-built agents for orchestrating complex AI workflows. Each agent specializes in a specific capability and can work independently or be orchestrated together.

## The 19 Agents

**Core Agents** (6):
1. Socratic Counselor - Guided learning
2. Code Generator - Code generation
3. Code Validator - Code testing
4. Knowledge Manager - Knowledge management
5. Learning Agent - Pattern learning
6. Skill Generator - Adaptive skill generation

**Coordination Agents** (4):
7. Multi-LLM Coordinator - Provider switching
8. Project Manager - Project management
9. Quality Controller - QA orchestration
10. Context Analyzer - Context management

**Data Agents** (4):
11. Document Processor - Document parsing
12. GitHub Sync Handler - GitHub integration
13. System Monitor - System monitoring
14. User Manager - User management

**Analysis Agents** (5):
15. Conflict Detector - Conflict detection
16. Knowledge Analyzer - Knowledge analysis
17. Document Context Analyzer - Semantic analysis
18. Note Manager - Notes/memory
19. Question Queue Agent - Question queuing

## Core Components

### 1. BaseAgent
Abstract base class for all agents.

Features:
- LLM integration via Socrates Nexus
- Async/await support
- Error handling
- Logging

### 2. AgentOrchestrator
Coordinates multiple agents.

Features:
- Dependency resolution
- Workflow execution
- Context passing
- Error recovery

### 3. Skill Generator
Generates and optimizes agent skills.

Methods:
- `generate(maturity_data, learning_data)` - Generate recommendations
- `apply_skill(agent, skill)` - Apply skill to agent

## Integration

- Socrates Nexus for LLM calls
- Openclaw skills
- LangChain tools
