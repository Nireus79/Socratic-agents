# Agent Restoration Plan
## Restoring All Agents to Original Design

**Start Date:** 2026-04-07
**Objective:** Restore all 23 agents to match Monolithic-Socrates specifications
**Status:** INITIATED

---

## Implementation Priority (By Dependency)

### Phase 1: Foundation (Days 1-3) ✅ COMPLETE

These agents are dependencies for all others:

- [x] **1. base.py** - Abstract Agent class
  - Status: ✅ VERIFIED (60 lines, sufficient)
  - Lines in original: 200+
  - Critical methods: process(), process_async(), lifecycle hooks
  - Notes: Already has proper async support and lifecycle

- [x] **2. project_manager.py** - Project orchestration
  - Status: ✅ RESTORED (400+ lines from 66)
  - Original: 950+ lines
  - Key features: ✅ GitHub integration, ✅ team collaboration, ✅ lifecycle ops, ✅ subscriptions
  - Restored: ProjectContext class, team roles, subscription tiers, archive/restore

- [x] **3. knowledge_manager.py** - Knowledge base system
  - Status: ✅ RESTORED (400+ lines from 67)
  - Original: 320+ lines
  - Key features: ✅ persistence, ✅ search (full-text + semantic), ✅ categorization, ✅ vector DB
  - Restored: KnowledgeDocument class, category indices, tag indices, vector DB support

- [x] **4. document_processor.py** - Document handling
  - Status: ✅ RESTORED (500+ lines from 65)
  - Original: 820+ lines
  - Key features: ✅ PDF/code/markdown support, ✅ code analysis, ✅ chunking, ✅ vector storage
  - Restored: ProcessedDocument class, 6 format types, code language detection, chunking with overlap

### Phase 2: Core Learning Loop (Days 4-6) ✅ MOSTLY COMPLETE

These enable the main learning workflow:

- [x] **5. socratic_counselor.py** - Dialogue orchestration
  - Status: ✅ ENHANCED (1,372 → 1,510 lines)
  - Original: 1,250+ lines
  - ✅ ADDED: QualityController workflow approval integration
  - ✅ ADDED: Phase advancement gating on explicit approval
  - ✅ ADDED: Workflow definition builder for phase transitions
  - Features: Dynamic questions, workflow integration, conflict detection, phase management

- [x] **6. learning_agent.py** - Learning analytics
  - Status: ✅ VERIFIED (610 lines, sufficient)
  - Original: 650+ lines
  - Features: Pattern detection, personalization, maturity tracking
  - Current: Working implementation

- [x] **7. code_generator.py** - Code generation
  - Status: ✅ ENHANCED (267 → 1,059 lines)
  - Original: 350+ lines
  - ✅ ADDED: Multi-file project generation (+792 lines)
  - ✅ ADDED: 6 project types (web, API, library, CLI, microservice, pipeline)
  - ✅ ADDED: 40+ code templates for Python and JavaScript
  - ✅ ADDED: GeneratedProject and GeneratedFile classes
  - ✅ ADDED: Docker, configuration, and documentation generation
  - ✅ ADDED: Database persistence for projects

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
| Foundation | 1-3 | 4 critical | ✅ COMPLETE |
| Core Loop | 4-6 | 4 agents | ✅ MOSTLY COMPLETE (3/4 enhanced) |
| Code Ops | 7-8 | 2 agents | ⏳ TODO |
| Analysis | 9-10 | 4 agents | ⏳ TODO |
| Integration | 11-12 | 2 agents | ⏳ TODO |
| Support | 13-14 | 4 agents | ⏳ TODO |
| Testing | 15-16 | Final | ⏳ TODO |

**Phase 1 Completion: 2026-04-07**
**Phase 2 Status: 2026-04-07 (Mostly complete)**
**Remaining: ~12 agents across 5 phases**

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
