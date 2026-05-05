# Socratic Agents - Quick Start Guide

This guide shows how to use `socratic-agents` as a standalone library in your projects.

## Installation

```bash
pip install socratic-agents
```

## Basic Usage

### Initialize the System

```python
from socratic_agents import SocraticAgentsSystem

# Create system with default services
system = SocraticAgentsSystem(
    api_key="sk-...",  # Your Anthropic API key
    data_dir="./data"
)

# List available agents
agents = system.list_agents()
print(agents)
# Output: {
#     "project_manager": "ProjectManagerAgent",
#     "socratic_counselor": "SocraticCounselorAgent",
#     "code_generator": "CodeGeneratorAgent",
#     ...
# }
```

### Process Requests Synchronously

```python
# Invoke an agent
response = system.process_request(
    "project_manager",
    {
        "action": "create_project",
        "name": "My Project",
        "description": "A sample project"
    }
)

# Response format:
# {
#     "status": "success",
#     "data": { ... },
#     "message": "Project created successfully"
# }

if response["status"] == "success":
    print(f"Success: {response['message']}")
    print(f"Data: {response['data']}")
else:
    print(f"Error: {response['message']}")
    print(f"Error code: {response.get('error_code')}")
```

### Process Requests Asynchronously

```python
import asyncio

async def main():
    response = await system.process_request_async(
        "code_generator",
        {
            "action": "generate_code",
            "language": "python",
            "context": "Create a web scraper"
        }
    )
    print(response)

asyncio.run(main())
```

## Customizing Services

### Using Custom Services

```python
from socratic_agents import SocraticAgentsSystem
from my_project.services import MyDatabaseService, MyLLMService

system = SocraticAgentsSystem(
    database=MyDatabaseService(),
    llm=MyLLMService(api_key="sk-..."),
    data_dir="./data"
)
```

### Replacing Services After Initialization

```python
system.set_service("database", my_custom_database)
system.set_service("llm", my_custom_llm)
system.set_service("event_emitter", my_custom_emitter)
```

## Registering Custom Agents

```python
from socratic_agents import SocraticAgentsSystem
from my_project.agents import MyCustomAgent

system = SocraticAgentsSystem(api_key="sk-...")

# Register your custom agent
system.register_agent("my_agent", MyCustomAgent)

# Use it
response = system.process_request(
    "my_agent",
    {"action": "my_action", "param": "value"}
)
```

## Service Interfaces

To implement custom services, inherit from these abstract base classes:

```python
from socratic_agents.services import (
    DatabaseService,
    LLMService,
    VectorDatabaseService,
    ConfigService,
    EventEmitterService,
)

class MyDatabase(DatabaseService):
    def load_user(self, user_id: str):
        # Implement your logic
        pass

    def save_user(self, user):
        # Implement your logic
        pass

    # ... implement other required methods

class MyLLM(LLMService):
    def generate_response(self, prompt: str, context: str = None, **kwargs) -> str:
        # Implement your logic
        pass

    # ... implement other required methods
```

## Available Agents

The system comes with 19+ agents out of the box:

**Core Agents:**
- `project_manager` - Manages project lifecycle
- `socratic_counselor` - Guides through Socratic questioning
- `quality_controller` - Orchestrates quality tracking
- `code_generator` - Generates code and documentation
- `user_learning` - Tracks user behavior and learning

**Analysis Agents:**
- `context_analyzer` - Analyzes project context
- `conflict_detector` - Identifies and resolves conflicts
- `document_processor` - Processes and analyzes documents
- `knowledge_analysis` - Analyzes knowledge and patterns

**Management Agents:**
- `user_manager` - Manages user accounts
- `note_manager` - Manages project notes
- `knowledge_manager` - Manages knowledge base

**Specialized Agents:**
- `code_validation` - Validates code quality
- `system_monitor` - Monitors system health
- `multi_llm` - Coordinates multiple LLM providers
- `question_queue` - Manages question queuing

... and more. Use `system.list_agents()` to see all available agents.

## Request Format

All requests follow a standard format:

```python
request = {
    "action": "string",  # Required: The action to perform
    # ... additional fields specific to the agent
}
```

## Response Format

All responses follow a standard format:

```python
response = {
    "status": "success" | "error",  # Required
    "data": { ... },                 # Response data (empty dict if error)
    "message": "string",             # Human-readable message
    "error_code": "string"           # (Optional) Error code for errors
}
```

## Example: Complete Project Setup

```python
from socratic_agents import SocraticAgentsSystem

# Initialize
system = SocraticAgentsSystem(
    api_key="sk-...",
    data_dir="./project_data"
)

# Create a project
create_response = system.process_request(
    "project_manager",
    {
        "action": "create_project",
        "name": "AI Learning System",
        "description": "A system for learning with AI guidance"
    }
)

if create_response["status"] == "success":
    project_id = create_response["data"].get("project_id")

    # Ask a question
    question_response = system.process_request(
        "socratic_counselor",
        {
            "action": "ask_question",
            "project_id": project_id,
            "topic": "machine learning"
        }
    )

    print("Question:", question_response["data"].get("question"))

    # Generate code
    code_response = system.process_request(
        "code_generator",
        {
            "action": "generate_artifact",
            "type": "code",
            "context": "Linear regression implementation"
        }
    )

    print("Generated code:", code_response["data"].get("artifact"))
```

## Error Handling

```python
response = system.process_request(agent_name, request)

if response["status"] == "error":
    error_code = response.get("error_code")

    if error_code == "AGENT_NOT_FOUND":
        print("Agent not found. Available agents:", system.list_agents())
    elif error_code == "REQUEST_ERROR":
        print("Request processing error:", response["message"])
    elif error_code == "SYSTEM_ERROR":
        print("System error:", response["message"])
    else:
        print(f"Unknown error ({error_code}): {response['message']}")
```

## Lifecycle Management

```python
# When done, clean up
system.shutdown()
```

## Architecture

```
SocraticAgentsSystem
├── AgentRegistry
│   ├── Manages agent registration and discovery
│   └── Creates agent instances with dependency injection
├── Services
│   ├── DatabaseService
│   ├── LLMService
│   ├── VectorDatabaseService
│   ├── ConfigService
│   └── EventEmitterService
├── RequestHandler
│   ├── Validates requests
│   ├── Routes to agents
│   └── Normalizes responses
└── AgentOrchestrator
    └── Coordinates agent interactions
```

## More Information

For detailed documentation on:
- Creating custom agents
- Advanced service configuration
- Agent communication patterns
- REST API integration

See the project documentation and examples in the repository.
