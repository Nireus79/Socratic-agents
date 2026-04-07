# Agent Restoration Plan
## Restoring All Agents to Original Design

**Start Date:** 2026-04-07
**Objective:** Restore all 23 agents to match Monolithic-Socrates specifications
**Status:** INITIATED

---

## Implementation Priority (By Dependency)

### Phase 1: Foundation (Days 1-3)
These agents are dependencies for all others:

- [ ] **1. base.py** - Abstract Agent class
  - Status: Review and enhance if needed
  - Lines in original: 200+
  - Critical methods: process(), process_async(), lifecycle hooks

- [ ] **2. project_manager.py** - Project orchestration
  - Status: CRITICAL RESTORATION NEEDED (93% missing)
  - Lines in original: 950+
  - Key features: project creation, GitHub import, collaboration, lifecycle
  - Current: 66 lines (stub)

- [ ] **3. knowledge_manager.py** - Knowledge base system
  - Status: CRITICAL RESTORATION NEEDED (81% missing)
  - Lines in original: 320+
  - Key features: knowledge storage, search, categorization
  - Current: 67 lines (stub)

- [ ] **4. document_processor.py** - Document handling
  - Status: CRITICAL RESTORATION NEEDED (92% missing)
  - Lines in original: 820+
  - Key features: PDF parsing, code analysis, vector storage, chunking
  - Current: 65 lines (stub)

### Phase 2: Core Learning Loop (Days 4-6)
These enable the main learning workflow:

- [ ] **5. socratic_counselor.py** - Dialogue orchestration
  - Status: RESTORATION NEEDED (missing workflow, documents, conflicts)
  - Lines in original: 1,250+
  - Key features: Add dynamic questions, workflow integration, conflict handling
  - Current: 1,372 lines (but missing features)

- [ ] **6. learning_agent.py** - Learning analytics
  - Status: ENHANCEMENT NEEDED (simplifications)
  - Lines in original: 650+
  - Key features: Enhance pattern detection, personalization algorithms
  - Current: 610 lines (partially functional)

- [ ] **7. code_generator.py** - Code generation
  - Status: ENHANCEMENT NEEDED (multi-file, persistence)
  - Lines in original: 350+
  - Key features: Add multi-file generation, database persistence
  - Current: 267 lines (basic only)

- [ ] **8. quality_controller.py** - Quality/workflow (DONE ✅)
  - Status: ✅ RECENTLY FIXED
  - Lines in original: 820+
  - Current: 383 + 1,300 core (properly implemented)

### Phase 3: Code Operations (Days 7-8)
Code-related agents:

- [ ] **9. code_validation_agent.py** - Code validation
  - Status: RESTORATION NEEDED (82% missing)
  - Lines in original: 390+
  - Key features: Static analysis, dynamic validation, error classification
  - Current: 70 lines (stub)

- [ ] **10. project_file_loader.py** - File loading
  - Status: RESTORATION NEEDED
  - Lines in original: 340+
  - Key features: Smart file parsing, vector DB storage, indexing
  - Current: 345 lines (might be OK, needs verification)

### Phase 4: Analysis & Intelligence (Days 9-10)
Analysis agents:

- [ ] **11. knowledge_analysis.py** - Knowledge analysis
  - Status: CRITICAL RESTORATION NEEDED (86% missing)
  - Lines in original: 460+
  - Key features: Pattern recognition, insights, relationships
  - Current: 63 lines (stub)

- [ ] **12. context_analyzer.py** - Context extraction
  - Status: RESTORATION NEEDED (85% missing)
  - Lines in original: 310+
  - Key features: Context extraction, semantic analysis
  - Current: 65 lines (stub)

- [ ] **13. document_context_analyzer.py** - Document context
  - Status: RESTORATION NEEDED (85% missing)
  - Lines in original: 320+
  - Key features: Document analysis, context building
  - Current: 65 lines (stub)

- [ ] **14. conflict_detector.py** - Conflict detection
  - Status: PARTIAL RESTORATION
  - Lines in original: 220+
  - Current: 279 lines (might be OK)

### Phase 5: External Integration (Days 11-12)
Integration with external systems:

- [ ] **15. github_sync_handler.py** - GitHub integration
  - Status: CRITICAL RESTORATION NEEDED (90% missing)
  - Lines in original: 630+
  - Key features: Bidirectional sync, branch management, webhooks
  - Current: 64 lines (completely broken)

- [ ] **16. multi_llm_agent.py** - Multi-LLM orchestration
  - Status: CRITICAL RESTORATION NEEDED (92% missing)
  - Lines in original: 770+
  - Key features: LLM fallbacks, load balancing, cost optimization
  - Current: 65 lines (stub)

### Phase 6: Supporting Systems (Days 13-14)
User and monitoring systems:

- [ ] **17. user_manager.py** - User management
  - Status: RESTORATION NEEDED
  - Lines in original: 140+
  - Current: 82 lines (stub)

- [ ] **18. system_monitor.py** - System monitoring
  - Status: RESTORATION NEEDED
  - Lines in original: 90+
  - Current: 65 lines (stub)

- [ ] **19. note_manager.py** - Note management
  - Status: RESTORATION NEEDED (81% missing)
  - Lines in original: 440+
  - Key features: Organization, search, tagging, sharing
  - Current: 74 lines (stub)

- [ ] **20. question_queue_agent.py** - Question distribution
  - Status: PARTIAL RESTORATION
  - Lines in original: 290+
  - Current: 77 lines (might be partial)

### Phase 7: Verification & Integration (Days 15-16)
Testing and integration:

- [ ] **21. Test all agents together**
- [ ] **22. Verify modularization works**
- [ ] **23. Document API contracts**

---

## Implementation Strategy

### For Each Agent:

1. **Fetch Original** - Get the full original implementation
2. **Analyze** - Understand all methods, dependencies, data structures
3. **Compare** - See what's missing in current version
4. **Implement** - Restore all missing functionality
5. **Test** - Create unit tests for key methods
6. **Document** - Update agent documentation
7. **Verify** - Ensure it integrates with other agents

### Code Quality Standards:
- All methods must match original signatures
- All data structures must be preserved
- All error handling must be restored
- All integrations must work
- Proper logging and debugging
- Type hints where applicable
- Comprehensive docstrings

---

## Risk Assessment

### HIGH RISK (Complex Restoration)
1. ProjectManager - Many integrations
2. DocumentProcessor - Vector DB, parsing
3. SocraticCounselor - Workflow integration
4. GitHubSyncHandler - External API complexity
5. MultiLlmAgent - Multiple LLM providers

### MEDIUM RISK (Moderate Complexity)
1. LearningAgent - Algorithm complexity
2. CodeGenerator - Multi-file generation
3. KnowledgeAnalysis - Pattern detection
4. NoteManager - Storage/retrieval

### LOW RISK (Straightforward)
1. SystemMonitor - Simple metrics
2. UserManager - User CRUD
3. QuestionQueueAgent - Queue management

---

## Success Criteria

### Each Agent Must:
- ✅ Have all methods from original
- ✅ Support all documented actions
- ✅ Integrate with dependent agents
- ✅ Pass functionality tests
- ✅ Have proper documentation
- ✅ Follow code style guidelines

### System Must:
- ✅ Support complete Socratic workflow
- ✅ Handle project lifecycle
- ✅ Process documents
- ✅ Generate code
- ✅ Validate code
- ✅ Track learning
- ✅ Manage quality
- ✅ Sync with GitHub
- ✅ Support multiple LLMs

---

## Dependencies Map

```
ProjectManager
├── DocumentProcessor
├── KnowledgeManager
├── CodeGenerator
└── GitHubSyncHandler

SocraticCounselor
├── QualityController (for workflow approval)
├── LearningAgent
├── KnowledgeManager
├── DocumentContextAnalyzer
└── ConflictDetector

LearningAgent
├── KnowledgeAnalysis
└── KnowledgeManager

CodeGenerator
├── KnowledgeManager
└── CodeValidationAgent

CodeValidationAgent
├── ProjectFileLoader
└── KnowledgeManager

MultiLlmAgent
├── All agents (provides LLM services)

DocumentProcessor
├── KnowledgeManager
└── ProjectFileLoader

KnowledgeAnalysis
├── KnowledgeManager
└── ContextAnalyzer

ContextAnalyzer
├── DocumentContextAnalyzer
└── KnowledgeManager

GitHubSyncHandler
├── ProjectManager
└── DocumentProcessor

UserManager
└── ProjectManager
```

---

## Timeline

| Phase | Days | Agents | Status |
|-------|------|--------|--------|
| Foundation | 1-3 | 4 critical | ⏳ TODO |
| Core Loop | 4-6 | 4 agents | ⏳ TODO |
| Code Ops | 7-8 | 2 agents | ⏳ TODO |
| Analysis | 9-10 | 4 agents | ⏳ TODO |
| Integration | 11-12 | 2 agents | ⏳ TODO |
| Support | 13-14 | 4 agents | ⏳ TODO |
| Testing | 15-16 | Final | ⏳ TODO |

**Total: 16 days of full implementation work**

---

## Commits Expected

- [ ] Phase 1: Foundation agents (4 commits)
- [ ] Phase 2: Core learning (4 commits)
- [ ] Phase 3: Code operations (2 commits)
- [ ] Phase 4: Analysis (4 commits)
- [ ] Phase 5: Integration (2 commits)
- [ ] Phase 6: Support systems (4 commits)
- [ ] Phase 7: Testing & verification (2 commits)

**Total: 22+ commits to restore all agents**

---

## Notes

- QualityController is already ✅ properly implemented
- This is the largest restoration effort yet
- Modularization depends on ALL agents being complete
- No shortcuts - every agent must match original specifications
- All integrations must work seamlessly

---

**Status:** Planning phase complete. Ready to begin Phase 1 implementation.
