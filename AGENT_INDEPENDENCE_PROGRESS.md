# Agent Independence Refactoring Progress

**Status**: PHASE 1 IN PROGRESS
**Date Started**: May 4, 2026
**Goal**: Make socratic-agents completely independent of socratic_system

---

## Strategy

Make agents **completely independent** with **clean API boundaries**, then implement **security governance** on top.

**Why This Order**:
- Security is easier on clean boundaries (REST API)
- Capability tokens make sense with explicit dependencies
- Zero trust is natural with service interfaces
- Won't have to refactor security later

---

## Phase 1: Service Interfaces & Dependency Injection

### Status: IN PROGRESS

**Completed**:
- ✅ Created `socratic_agents/interfaces/` module
- ✅ Defined `DatabaseService` (ABC)
- ✅ Defined `LLMService` (ABC)
- ✅ Defined `VectorDatabaseService` (ABC)
- ✅ Started refactoring `CodeGeneratorAgent`
- ✅ Removed direct socratic_system imports from CodeGeneratorAgent

**In Progress**:
- 🔄 Finish CodeGeneratorAgent refactoring
- 🔄 Refactor remaining 18 agents

**Next Steps**:
1. Complete CodeGeneratorAgent with all methods using injected services
2. Refactor ProjectManagerAgent
3. Refactor SocraticCounselorAgent (most complex, uses many services)
4. Refactor remaining agents in priority order

---

## Agent Refactoring Priority Order

Agents to refactor (19 total):

### Priority 1: Core Agents (5 agents)
- [ ] **CodeGeneratorAgent** - In progress
- [ ] **ProjectManagerAgent** - Uses database, LLM, file system
- [ ] **SocraticCounselorAgent** - Uses database, LLM, vector DB, multiple other agents
- [ ] **QualityControllerAgent** - Uses database, maturity calculations
- [ ] **ConflictDetectorAgent** - Uses LLM for conflict analysis

### Priority 2: Knowledge Agents (3 agents)
- [ ] **KnowledgeManagerAgent** - Uses vector DB, database
- [ ] **KnowledgeAnalysisAgent** - Uses vector DB, LLM
- [ ] **DocumentProcessorAgent** - Uses LLM, file system

### Priority 3: Utility Agents (4 agents)
- [ ] **CodeValidationAgent** - Uses GitHub API (external service)
- [ ] **UserLearningAgent** - Uses database
- [ ] **ContextAnalyzerAgent** - Uses vector DB
- [ ] **MultiLLMAgent** - Uses LLM

### Priority 4: Management Agents (4 agents)
- [ ] **UserManagerAgent** - Uses database
- [ ] **NoteManagerAgent** - Uses database
- [ ] **SystemMonitorAgent** - Uses database
- [ ] **QuestionQueueAgent** - Uses database

### Priority 5: Helpers (3 agents)
- [ ] **GitHubSyncHandler** - External service
- [ ] **ProjectFileLoader** - Uses database, file system
- [ ] **DocumentContextAnalyzer** - Uses vector DB, LLM

---

## Service Interfaces Required

### Completed ✅
- DatabaseService
- LLMService
- VectorDatabaseService

### Still Needed 🔄
- **FileSystemService** - Abstract file I/O
  - save_file(), load_file(), delete_file()
  - create_directory(), list_files()

- **GitHubService** - Abstract GitHub integration
  - create_repo(), push_code(), create_pr()
  - get_repo_info()

- **ExternalAPIService** - Abstract external services
  - call_api(), get_credentials()

- **AuthService** - Abstract authentication
  - get_user(), verify_credentials()
  - get_user_auth_method()

- **EventEmitterService** - Abstract event system
  - emit(), on(), off()
  - emit_async() for async contexts

---

## Code Pattern: From Coupled to Independent

### BEFORE (Coupled to orchestrator):
```python
class CodeGeneratorAgent(Agent):
    def __init__(self, orchestrator):
        super().__init__("CodeGenerator", orchestrator)
        self.orchestrator = orchestrator

    def _generate_artifact(self, request):
        project = request.get("project")
        artifact = self.orchestrator.claude_client.generate_artifact(...)  # ❌ Direct coupling
        self.orchestrator.database.save_file(...)  # ❌ Direct coupling
        return artifact
```

### AFTER (Independent with DI):
```python
class CodeGeneratorAgent(Agent):
    def __init__(
        self,
        name: str = "CodeGenerator",
        llm_service: Optional[LLMService] = None,
        database_service: Optional[DatabaseService] = None,
        file_service: Optional[FileSystemService] = None,
    ):
        super().__init__(name)
        self.llm_service = llm_service
        self.database_service = database_service
        self.file_service = file_service

    async def _generate_artifact(self, request):
        project = request.get("project")
        artifact = await self.llm_service.generate_code(...)  # ✅ Injected service
        await self.file_service.save_file(...)  # ✅ Injected service
        return artifact
```

---

## Integration Points

After agents are independent, they'll be created like:

```python
# Create service implementations
llm_service = ClaudeService(api_key=key)
database_service = SocratesDatabase(db_path=path)
vector_db_service = ChromaDBService(collection_name="socrates")
file_service = LocalFileSystem(base_dir=data_dir)

# Create agents with injected services
code_gen = CodeGeneratorAgent(
    llm_service=llm_service,
    database_service=database_service,
    file_service=file_service,
)

project_manager = ProjectManagerAgent(
    llm_service=llm_service,
    database_service=database_service,
    file_service=file_service,
)

# Agents talk via REST API or AgentBus
agent_bus = AgentBus()
agent_bus.register(code_gen)
agent_bus.register(project_manager)
```

---

## Current Blockers / Considerations

1. **Async/Await Consistency**
   - Some agents use sync code, some use async
   - Need to make all service methods async
   - Will need `asyncio.to_thread()` for sync operations

2. **Agent-to-Agent Communication**
   - Currently: `orchestrator.process_request("other_agent", data)`
   - After: Use `agent_bus.send_request("other_agent", data)`
   - Already implemented in socratic_agents library

3. **Configuration**
   - Currently: `self.orchestrator.config.data_dir`
   - After: Pass config to services via constructor
   - Need to define Config interface

4. **Testing**
   - After refactoring, can mock services easily
   - No need for full Socrates environment
   - Can test agents in isolation

---

## Benefits After Refactoring

### Immediate
- ✅ Agents don't import from socratic_system
- ✅ Can test agents without Socrates monolith
- ✅ Clear service boundaries for security
- ✅ Easier to reason about dependencies

### Security
- ✅ Capability tokens per service
- ✅ Constitutional Governor validates service calls
- ✅ Zero trust between agents (via REST)
- ✅ Audit logging at service boundaries

### Scalability
- ✅ Agents can run as separate services
- ✅ Horizontal scaling of agent workloads
- ✅ Service instances can be containerized
- ✅ Multi-instance deployments possible

### Maintainability
- ✅ Mocking services is straightforward
- ✅ Changing implementations doesn't affect agents
- ✅ Clear separation of concerns
- ✅ Easier debugging and testing

---

## Estimated Timeline

- **Phase 1 (Service Interfaces)**: 1 week - IN PROGRESS
  - Define all interfaces ✅ (started)
  - Create implementations stubs
  - Refactor agents to use DI

- **Phase 2 (Agent Bus Integration)**: 1 week
  - Replace orchestrator calls with agent bus
  - Implement message routing
  - Add request/response patterns

- **Phase 3 (Security Integration)**: 2 weeks
  - Add capability tokens
  - Constitutional Governor validation
  - Audit logging

- **Phase 4 (Testing & Hardening)**: 1-2 weeks
  - Unit tests for each agent
  - Integration tests for service interactions
  - Security testing

**Total**: 5-7 weeks to full independence

---

## Documentation References

- **ARCHITECTURE_ANALYSIS_LIBRARY_EXPORT.md** - Overall strategy
- **SECURITY.md** - Security architecture (Phase 3)
- **TWO_LIBRARY_ARCHITECTURE.md** - Library structure

---

**Next Update**: After CodeGeneratorAgent completion
