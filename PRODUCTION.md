# Production Deployment Guide - Socratic Agents

A production-ready multi-agent framework with 19+ specialized agents and service-based architecture.

## Production Readiness

### Framework Architecture
- [x] Service-based architecture (agents are independent services)
- [x] Dependency injection pattern (loose coupling)
- [x] Event-driven messaging (AgentBus)
- [x] Constitutional AI governance support
- [x] Full async/await support
- [x] Type-safe agent definitions

### Deployment Checklist

#### Agent Configuration
```python
from socratic_agents import (
    SocraticCounselor, ProjectManager, CodeGenerator,
    KnowledgeManager, ConflictDetector, ContextAnalyzer
)
from socratic_morality import Governor

# Initialize agents with governance
governor = Governor(constitution='default')
counselor = SocraticCounselor(governor=governor)
manager = ProjectManager(governor=governor)
code_gen = CodeGenerator(governor=governor)
```

#### Service Registration
```python
# Register agents in service registry
from socratic_agents import AgentRegistry

registry = AgentRegistry()
registry.register('counselor', counselor)
registry.register('manager', manager)
registry.register('generator', code_gen)

# Discover agents dynamically
agent = registry.get_agent('counselor')
```

#### Event-Driven Communication
```python
from socratic_agents import AgentBus

# Create agent bus for inter-agent messaging
bus = AgentBus()
bus.register_handler('project.created', handle_project_creation)
bus.register_handler('conflict.detected', handle_conflict)

# Publish events
bus.publish('project.created', {'project_id': '123', 'owner': 'user1'})

# Agents react to events asynchronously
```

### Scaling Strategies

#### Single-Node Deployment
```python
# All agents in same process
from socratic_agents import AgentOrchestrator

orchestrator = AgentOrchestrator()
# Agents share memory and event bus
```

#### Distributed Deployment
```python
# Agents as microservices
# Each agent runs independently with:
# - Separate process/container
# - Message-based communication via Redis/RabbitMQ
# - Shared event bus (distributed)
# - Centralized database for state

# Agent 1: Socratic Counselor (port 8001)
# Agent 2: Code Generator (port 8002)
# Agent 3: Project Manager (port 8003)
# Central: Event Bus + Database
```

### Monitoring & Observability

#### Agent Metrics
```python
# Track agent activities
metrics = {
    'agent.messages_received': 0,
    'agent.messages_processed': 0,
    'agent.errors': 0,
    'agent.response_time_ms': 0,
}

# Record per agent type
logger.info("agent.activity", extra={
    'agent': 'socratic_counselor',
    'action': 'question_generated',
    'duration_ms': 250,
    'project_id': '123',
})
```

#### Health Checks
```python
# Agent health endpoint
async def agent_health():
    return {
        'agents': {
            'counselor': counselor.is_healthy(),
            'manager': manager.is_healthy(),
            'generator': code_gen.is_healthy(),
        },
        'bus': bus.is_connected(),
        'database': db.is_connected(),
    }
```

#### Error Handling
```python
# Implement agent-level circuit breaker
from socratic_agents import CircuitBreaker

breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=60,
)

try:
    result = await breaker.call(agent.process, data)
except CircuitBreakerOpen:
    logger.warning("Agent overloaded, using fallback")
    result = fallback_result()
```

### Integration Patterns

#### With Socratic Nexus (LLM Client)
```python
from socratic_nexus import ClaudeClient
from socratic_agents import CodeGenerator

# Agents use universal LLM client
llm_client = ClaudeClient(api_key=api_key)
code_gen = CodeGenerator(llm_client=llm_client)

# Can switch providers without changing agents
```

#### With Socratic Knowledge (Knowledge Base)
```python
from socratic_knowledge import KnowledgeManager as KMBase
from socratic_agents import KnowledgeAgent

# Agents access centralized knowledge
knowledge = KMBase(tenant_id='org1')
agent = KnowledgeAgent(knowledge_base=knowledge)
```

#### With Socratic Conflict (Conflict Resolution)
```python
from socratic_conflict import ConflictResolver
from socratic_agents import ConflictDetector

# Detect and resolve multi-agent conflicts
detector = ConflictDetector()
resolver = ConflictResolver()

conflict = await detector.detect()
if conflict:
    resolution = await resolver.resolve(conflict)
```

### Performance Tuning

```python
# Tune for your workload
config = {
    'max_concurrent_agents': 5,
    'queue_size': 1000,
    'timeout_seconds': 30,
    'retry_attempts': 3,
    'batch_size': 50,
}

orchestrator = AgentOrchestrator(**config)
```

### Security & Governance

```python
# Use constitutional AI for safety
from socratic_morality import Governor

# Define organizational values
constitution = {
    'truthfulness': 'All outputs must be factual and honest',
    'harmlessness': 'Never assist with harmful activities',
    'helpfulness': 'Provide maximum value to users',
}

governor = Governor(constitution=constitution)

# Agents respect constraints
agent = CounsElector(governor=governor)
response = await agent.question(project, user)
# Response is evaluated against constitution
```

### Runbook: Common Operations

**Scale agents for high load:**
```bash
# Deploy additional agent replicas
docker-compose scale counselor=3 generator=5 manager=2
```

**Monitor agent queue depth:**
```python
queue_depth = await bus.get_queue_depth()
if queue_depth > 5000:
    logger.warning("High message queue, scale agents up")
```

**Reset failed agent:**
```python
agent.reset()  # Clear internal state
agent.healthcheck()  # Verify recovery
```

