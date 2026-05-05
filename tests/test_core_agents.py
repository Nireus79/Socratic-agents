"""Comprehensive tests for core Socratic Agents."""

from socratic_agents import (
    Agent,
    AgentOrchestrator,
    EventEmitter,
    EventType,
    LLMProviderConfig,
    LLMUsageRecord,
    ProviderMetadata,
    get_provider_metadata,
    list_available_providers,
)
from socratic_agents.code_generator import CodeGeneratorAgent
from socratic_agents.code_validation_agent import CodeValidationAgent
from socratic_agents.knowledge_manager import KnowledgeManagerAgent
from socratic_agents.learning_agent import UserLearningAgent
from socratic_agents.multi_llm_agent import MultiLLMAgent
from socratic_agents.quality_controller import QualityControllerAgent
from socratic_agents.socratic_counselor import SocraticCounselorAgent


# ===== EventEmitter Tests =====
class TestEventEmitter:
    """Test event emission system."""

    def test_event_emitter_creation(self):
        """Test creating an event emitter."""
        emitter = EventEmitter()
        assert emitter is not None
        assert hasattr(emitter, "on")
        assert hasattr(emitter, "emit")
        assert hasattr(emitter, "off")

    def test_event_listener_registration(self):
        """Test registering event listeners."""
        emitter = EventEmitter()
        callback_called = []

        def callback(data):
            callback_called.append(data)

        emitter.on(EventType.CODE_GENERATED, callback)
        emitter.emit(EventType.CODE_GENERATED, {"code": "test"})

        assert len(callback_called) == 1
        assert callback_called[0]["code"] == "test"

    def test_multiple_listeners(self):
        """Test multiple listeners for same event."""
        emitter = EventEmitter()
        results = []

        def callback1(data):
            results.append(("cb1", data))

        def callback2(data):
            results.append(("cb2", data))

        emitter.on(EventType.CODE_GENERATED, callback1)
        emitter.on(EventType.CODE_GENERATED, callback2)
        emitter.emit(EventType.CODE_GENERATED, {"test": True})

        assert len(results) == 2
        assert results[0][0] == "cb1"
        assert results[1][0] == "cb2"

    def test_event_listener_removal(self):
        """Test removing event listeners."""
        emitter = EventEmitter()
        calls = []

        def callback(data):
            calls.append(data)

        emitter.on(EventType.LOG_INFO, callback)
        emitter.emit(EventType.LOG_INFO, {"msg": "first"})
        assert len(calls) == 1

        emitter.off(EventType.LOG_INFO, callback)
        emitter.emit(EventType.LOG_INFO, {"msg": "second"})
        assert len(calls) == 1  # Should not increase


# ===== AgentOrchestrator Tests =====
class TestAgentOrchestrator:
    """Test agent orchestration system."""

    def test_orchestrator_creation(self):
        """Test creating an orchestrator."""
        orchestrator = AgentOrchestrator()
        assert orchestrator is not None
        assert orchestrator.event_emitter is not None
        assert isinstance(orchestrator.event_emitter, EventEmitter)

    def test_agent_registration(self):
        """Test registering agents."""
        orchestrator = AgentOrchestrator()

        class DummyAgent(Agent):
            def process(self, request):
                return {"status": "success"}

        agent = DummyAgent("test_agent", orchestrator)
        orchestrator.register_agent("test", agent)

        assert orchestrator.get_agent("test") == agent

    def test_list_agents(self):
        """Test listing registered agents."""
        orchestrator = AgentOrchestrator()

        class DummyAgent(Agent):
            def process(self, request):
                return {"status": "success"}

        agent1 = DummyAgent("agent1", orchestrator)
        agent2 = DummyAgent("agent2", orchestrator)

        orchestrator.register_agent("agent1", agent1)
        orchestrator.register_agent("agent2", agent2)

        agents = orchestrator.list_agents()
        assert len(agents) == 2
        assert "agent1" in agents
        assert "agent2" in agents

    def test_shared_state(self):
        """Test shared state management."""
        orchestrator = AgentOrchestrator()

        orchestrator.set_state("key1", "value1")
        assert orchestrator.get_state("key1") == "value1"

        orchestrator.set_state("key2", {"nested": "data"})
        assert orchestrator.get_state("key2") == {"nested": "data"}

        assert orchestrator.get_state("nonexistent", "default") == "default"

    def test_clear_state(self):
        """Test clearing shared state."""
        orchestrator = AgentOrchestrator()
        orchestrator.set_state("key", "value")
        assert orchestrator.get_state("key") == "value"

        orchestrator.clear_state()
        assert orchestrator.get_state("key") is None


# ===== Agent Base Class Tests =====
class TestAgentBase:
    """Test base agent functionality."""

    def test_agent_initialization(self):
        """Test initializing an agent."""
        orchestrator = AgentOrchestrator()

        class TestAgent(Agent):
            def process(self, request):
                return {"status": "ok"}

        agent = TestAgent("Test Agent", orchestrator)
        assert agent.name == "Test Agent"
        assert agent.orchestrator == orchestrator

    def test_agent_process_sync(self):
        """Test synchronous process method."""
        orchestrator = AgentOrchestrator()

        class TestAgent(Agent):
            def process(self, request):
                return {"status": "success", "input": request.get("input")}

        agent = TestAgent("Test", orchestrator)
        result = agent.process({"input": "test_value"})

        assert result["status"] == "success"
        assert result["input"] == "test_value"

    def test_agent_emit_event(self):
        """Test agent event emission."""
        orchestrator = AgentOrchestrator()
        events = []

        def capture_event(data):
            events.append(data)

        orchestrator.event_emitter.on(EventType.CODE_GENERATED, capture_event)

        class TestAgent(Agent):
            def process(self, request):
                self.emit_event(EventType.CODE_GENERATED, {"code": "test_code"})
                return {"status": "ok"}

        agent = TestAgent("Test", orchestrator)
        agent.process({})

        assert len(events) == 1
        assert events[0]["code"] == "test_code"
        assert events[0]["agent"] == "Test"


# ===== Models Tests =====
class TestLLMModels:
    """Test LLM provider models."""

    def test_llm_provider_config_creation(self):
        """Test creating provider config."""
        config = LLMProviderConfig(
            id="config-1",
            provider="claude",
            user_id="user-1",
            is_default=True,
        )

        assert config.provider == "claude"
        assert config.id == "config-1"
        assert config.user_id == "user-1"
        assert config.is_default is True

    def test_llm_provider_config_validation(self):
        """Test provider config requires id and user_id."""
        # Valid config with required fields
        config = LLMProviderConfig(id="config-1", provider="claude", user_id="user-1")
        assert config.id == "config-1"
        assert config.user_id == "user-1"

        # Config with settings
        config_with_settings = LLMProviderConfig(
            id="config-2",
            provider="openai",
            user_id="user-2",
            settings={"model": "gpt-4", "temperature": 0.5},
        )
        assert config_with_settings.settings["model"] == "gpt-4"
        assert config_with_settings.settings["temperature"] == 0.5

    def test_llm_usage_record(self):
        """Test creating usage records."""
        record = LLMUsageRecord(
            id="record-1",
            user_id="user-1",
            provider="claude",
            model="claude-3-5-sonnet-20241022",
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
            cost=0.015,
        )

        assert record.provider == "claude"
        assert record.total_tokens == 150
        assert record.cost == 0.015

    def test_get_provider_metadata(self):
        """Test getting provider metadata."""
        claude_metadata = get_provider_metadata("claude")
        assert claude_metadata.provider == "claude"
        assert isinstance(claude_metadata, ProviderMetadata)
        assert len(claude_metadata.models) > 0
        assert claude_metadata.supports_vision is True

        openai_metadata = get_provider_metadata("openai")
        assert openai_metadata.provider == "openai"

    def test_list_available_providers(self):
        """Test listing available providers."""
        providers = list_available_providers()
        assert isinstance(providers, list)
        assert "claude" in providers
        assert "openai" in providers
        assert "gemini" in providers
        assert "ollama" in providers

    def test_get_invalid_provider(self):
        """Test getting metadata for invalid provider."""
        invalid_metadata = get_provider_metadata("invalid_provider")
        assert invalid_metadata is None


# ===== Concrete Agent Tests =====
class TestConcreteAgents:
    """Test concrete agent implementations."""

    def test_code_generator_agent_init(self):
        """Test CodeGeneratorAgent initialization."""
        orchestrator = AgentOrchestrator()
        agent = CodeGeneratorAgent(orchestrator)
        assert agent.name == "CodeGenerator"
        assert agent.orchestrator == orchestrator

    def test_code_validation_agent_init(self):
        """Test CodeValidationAgent initialization."""
        orchestrator = AgentOrchestrator()
        agent = CodeValidationAgent(orchestrator)
        assert agent.name == "CodeValidation"

    def test_knowledge_manager_agent_init(self):
        """Test KnowledgeManagerAgent initialization."""
        orchestrator = AgentOrchestrator()
        agent = KnowledgeManagerAgent("Knowledge Manager", orchestrator)
        assert agent.name == "Knowledge Manager"

    def test_multi_llm_agent_init(self):
        """Test MultiLLMAgent initialization."""
        orchestrator = AgentOrchestrator()
        agent = MultiLLMAgent(orchestrator)
        assert agent.name == "Multi-LLM Manager"

    def test_learning_agent_init(self):
        """Test UserLearningAgent initialization."""
        orchestrator = AgentOrchestrator()
        agent = UserLearningAgent(orchestrator)
        assert agent.name == "User Learning"

    def test_quality_controller_agent_init(self):
        """Test QualityControllerAgent initialization."""
        orchestrator = AgentOrchestrator()
        agent = QualityControllerAgent(orchestrator)
        assert agent.name == "QualityController"

    def test_socratic_counselor_agent_init(self):
        """Test SocraticCounselorAgent initialization."""
        orchestrator = AgentOrchestrator()
        agent = SocraticCounselorAgent(orchestrator)
        assert agent.name == "SocraticCounselor"


# ===== EventType Tests =====
class TestEventTypes:
    """Test EventType enum."""

    def test_event_type_values(self):
        """Test EventType enum has all expected values."""
        # Logging events
        assert hasattr(EventType, "LOG_DEBUG")
        assert hasattr(EventType, "LOG_INFO")
        assert hasattr(EventType, "LOG_WARNING")
        assert hasattr(EventType, "LOG_ERROR")

        # Code events
        assert hasattr(EventType, "CODE_GENERATED")
        assert hasattr(EventType, "CODE_ANALYSIS_COMPLETE")

        # Knowledge events
        assert hasattr(EventType, "KNOWLEDGE_SUGGESTION")
        assert hasattr(EventType, "DOCUMENT_IMPORTED")
        assert hasattr(EventType, "QUESTIONS_REGENERATED")

        # Workflow events
        assert hasattr(EventType, "WORKFLOW_APPROVAL_REQUESTED")
        assert hasattr(EventType, "WORKFLOW_APPROVED")
        assert hasattr(EventType, "WORKFLOW_REJECTED")

        # Quality/Maturity events
        assert hasattr(EventType, "QUALITY_CHECK_PASSED")
        assert hasattr(EventType, "PHASE_READY_TO_ADVANCE")


# ===== Integration Tests =====
class TestAgentIntegration:
    """Integration tests with multiple agents."""

    def test_orchestrator_with_multiple_agents(self):
        """Test orchestrator coordinating multiple agents."""
        orchestrator = AgentOrchestrator()

        class Agent1(Agent):
            def process(self, request):
                self.emit_event(EventType.CODE_GENERATED, {"step": 1})
                return {"step": 1, "result": "agent1"}

        class Agent2(Agent):
            def process(self, request):
                self.emit_event(EventType.CODE_ANALYSIS_COMPLETE, {"step": 2})
                return {"step": 2, "result": "agent2"}

        agent1 = Agent1("Agent1", orchestrator)
        agent2 = Agent2("Agent2", orchestrator)

        orchestrator.register_agent("agent1", agent1)
        orchestrator.register_agent("agent2", agent2)

        result1 = orchestrator.process("agent1", {})
        result2 = orchestrator.process("agent2", {})

        assert result1["step"] == 1
        assert result2["step"] == 2

    def test_event_propagation_between_agents(self):
        """Test events propagating between agents."""
        orchestrator = AgentOrchestrator()
        event_log = []

        def log_event(data):
            event_log.append(data["event_type"])

        orchestrator.event_emitter.on(EventType.CODE_GENERATED, log_event)
        orchestrator.event_emitter.on(EventType.CODE_ANALYSIS_COMPLETE, log_event)

        class GeneratorAgent(Agent):
            def process(self, request):
                self.emit_event(EventType.CODE_GENERATED, {"code": "test"})
                return {"status": "generated"}

        class AnalyzerAgent(Agent):
            def process(self, request):
                self.emit_event(EventType.CODE_ANALYSIS_COMPLETE, {"analysis": "ok"})
                return {"status": "analyzed"}

        gen_agent = GeneratorAgent("Generator", orchestrator)
        ana_agent = AnalyzerAgent("Analyzer", orchestrator)

        orchestrator.register_agent("generator", gen_agent)
        orchestrator.register_agent("analyzer", ana_agent)

        orchestrator.process("generator", {})
        orchestrator.process("analyzer", {})

        assert len(event_log) == 2
        assert "code_generated" in event_log
        assert "code_analysis_complete" in event_log


# Phase 3 Governance Tests
class TestPhase3Governance:
    """Tests for Phase 3 governance integration."""

    def test_governed_agent_import(self):
        """Test that GovernedAgent can be imported."""
        from socratic_agents.governance import GovernedAgent

        assert GovernedAgent is not None

    def test_governance_adapter_import(self):
        """Test that GovernanceAdapter can be imported."""
        from socratic_agents.governance import GovernanceAdapter

        assert GovernanceAdapter is not None

    def test_agent_bus_import(self):
        """Test that AgentBus can be imported."""
        from socratic_agents.agent_bus import AgentBus, AgentMessage, MessageType

        assert AgentBus is not None
        assert AgentMessage is not None
        assert MessageType is not None

    def test_orchestrator_has_core_support(self):
        """Test that orchestrator has core features."""
        orchestrator = AgentOrchestrator()

        assert hasattr(orchestrator, "event_emitter")
        assert hasattr(orchestrator, "register_agent")
        assert hasattr(orchestrator, "get_agent")
        assert hasattr(orchestrator, "process")
        assert hasattr(orchestrator, "set_state")

    def test_orchestrator_state_management(self):
        """Test state management in orchestrator."""
        orchestrator = AgentOrchestrator()

        orchestrator.set_state("test_key", "test_value")
        assert orchestrator.get_state("test_key") == "test_value"

        orchestrator.clear_state()
        assert orchestrator.get_state("test_key") is None

    def test_orchestrator_agent_registration(self):
        """Test agent registration and retrieval."""
        orchestrator = AgentOrchestrator()

        class TestAgent:
            def __init__(self):
                self.name = "TestAgent"

        agent = TestAgent()
        orchestrator.register_agent("test_agent", agent)

        retrieved = orchestrator.get_agent("test_agent")
        assert retrieved is not None
        assert retrieved.name == "TestAgent"

    def test_orchestrator_list_agents(self):
        """Test listing registered agents."""
        orchestrator = AgentOrchestrator()

        class DummyAgent:
            def __init__(self, name):
                self.name = name

        orchestrator.register_agent("agent1", DummyAgent("agent1"))
        orchestrator.register_agent("agent2", DummyAgent("agent2"))

        agents = orchestrator.list_agents()
        assert len(agents) == 2
        assert "agent1" in agents
        assert "agent2" in agents

    def test_orchestrator_process_request(self):
        """Test processing request through agent."""
        orchestrator = AgentOrchestrator()

        class EchoAgent:
            def process(self, request):
                return {"echo": request.get("message")}

        orchestrator.register_agent("echo", EchoAgent())

        result = orchestrator.process("echo", {"message": "hello"})
        assert result["echo"] == "hello"
