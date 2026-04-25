"""Advanced comprehensive tests for Socratic Agents."""

from socratic_agents import (
    Agent,
    AgentOrchestrator,
    EventEmitter,
    EventType,
    LLMProviderConfig,
    LLMUsageRecord,
    get_provider_metadata,
    list_available_providers,
)
from socratic_agents.knowledge_manager import KnowledgeManagerAgent
from socratic_agents.learning_agent import UserLearningAgent
from socratic_agents.multi_llm_agent import MultiLLMAgent


# ===== Advanced EventEmitter Tests =====
class TestAdvancedEventEmitter:
    """Advanced event emission and handling tests."""

    def test_event_with_multiple_data_types(self):
        """Test event emission with various data types."""
        emitter = EventEmitter()
        results = []

        def callback(data):
            results.append(data)

        emitter.on(EventType.LOG_INFO, callback)
        emitter.emit(EventType.LOG_INFO, {"string": "test", "number": 42, "list": [1, 2, 3]})

        assert len(results) == 1
        assert results[0]["number"] == 42
        assert results[0]["list"] == [1, 2, 3]

    def test_event_listener_called_in_order(self):
        """Test that listeners are called in registration order."""
        emitter = EventEmitter()
        order = []

        def listener1(data):
            order.append(1)

        def listener2(data):
            order.append(2)

        def listener3(data):
            order.append(3)

        emitter.on(EventType.CODE_GENERATED, listener1)
        emitter.on(EventType.CODE_GENERATED, listener2)
        emitter.on(EventType.CODE_GENERATED, listener3)
        emitter.emit(EventType.CODE_GENERATED, {})

        assert order == [1, 2, 3]

    def test_different_event_types_isolated(self):
        """Test that different event types don't interfere."""
        emitter = EventEmitter()
        log_calls = []
        code_calls = []

        emitter.on(EventType.LOG_INFO, lambda d: log_calls.append(d))
        emitter.on(EventType.CODE_GENERATED, lambda d: code_calls.append(d))

        emitter.emit(EventType.LOG_INFO, {"msg": "log"})
        emitter.emit(EventType.CODE_GENERATED, {"code": "gen"})
        emitter.emit(EventType.LOG_INFO, {"msg": "log2"})

        assert len(log_calls) == 2
        assert len(code_calls) == 1


# ===== Advanced AgentOrchestrator Tests =====
class TestAdvancedOrchestration:
    """Advanced orchestration scenarios."""

    def test_orchestrator_with_large_state(self):
        """Test orchestrator with large state objects."""
        orchestrator = AgentOrchestrator()
        large_dict = {f"key_{i}": f"value_{i}" for i in range(100)}

        orchestrator.set_state("large_state", large_dict)
        retrieved = orchestrator.get_state("large_state")

        assert len(retrieved) == 100
        assert retrieved["key_50"] == "value_50"

    def test_multiple_agents_sharing_state(self):
        """Test multiple agents sharing orchestrator state."""
        orchestrator = AgentOrchestrator()

        class ReadAgent(Agent):
            def process(self, request):
                return {"value": self.orchestrator.get_state("shared_key")}

        class WriteAgent(Agent):
            def process(self, request):
                self.orchestrator.set_state("shared_key", request.get("value"))
                return {"status": "written"}

        read_agent = ReadAgent("reader", orchestrator)
        write_agent = WriteAgent("writer", orchestrator)

        orchestrator.register_agent("reader", read_agent)
        orchestrator.register_agent("writer", write_agent)

        write_result = orchestrator.process("writer", {"value": "test_data"})
        assert write_result["status"] == "written"

        read_result = orchestrator.process("reader", {})
        assert read_result["value"] == "test_data"

    def test_state_overwrite(self):
        """Test that state overwrites properly."""
        orchestrator = AgentOrchestrator()

        orchestrator.set_state("key", "value1")
        assert orchestrator.get_state("key") == "value1"

        orchestrator.set_state("key", "value2")
        assert orchestrator.get_state("key") == "value2"

    def test_get_nonexistent_state_with_default(self):
        """Test getting non-existent state with default value."""
        orchestrator = AgentOrchestrator()

        result = orchestrator.get_state("nonexistent", "default_val")
        assert result == "default_val"


# ===== Agent Communication Tests =====
class TestAgentCommunication:
    """Test inter-agent communication and coordination."""

    def test_agent_to_agent_event_coordination(self):
        """Test agents coordinating via events."""
        orchestrator = AgentOrchestrator()
        events_received = []

        def track_events(data):
            events_received.append(data)

        orchestrator.event_emitter.on(EventType.CODE_GENERATED, track_events)
        orchestrator.event_emitter.on(EventType.CODE_ANALYSIS_COMPLETE, track_events)

        class Producer(Agent):
            def process(self, request):
                self.emit_event(EventType.CODE_GENERATED, {"code": "generated"})
                self.emit_event(EventType.CODE_ANALYSIS_COMPLETE, {"analysis": "done"})
                return {"status": "complete"}

        producer = Producer("producer", orchestrator)
        orchestrator.register_agent("producer", producer)
        result = orchestrator.process("producer", {})

        assert result["status"] == "complete"
        assert len(events_received) == 2

    def test_sequential_agent_processing(self):
        """Test sequential processing through multiple agents."""
        orchestrator = AgentOrchestrator()

        class Agent1(Agent):
            def process(self, request):
                value = request.get("value", 0)
                return {"value": value + 10}

        class Agent2(Agent):
            def process(self, request):
                value = request.get("value", 0)
                return {"value": value * 2}

        agent1 = Agent1("agent1", orchestrator)
        agent2 = Agent2("agent2", orchestrator)

        orchestrator.register_agent("agent1", agent1)
        orchestrator.register_agent("agent2", agent2)

        result1 = orchestrator.process("agent1", {"value": 5})
        result2 = orchestrator.process("agent2", result1)

        assert result2["value"] == 30


# ===== Configuration Tests =====
class TestLLMConfiguration:
    """Test LLM provider configuration."""

    def test_all_providers_available(self):
        """Test that all expected providers are available."""
        providers = list_available_providers()

        expected = ["claude", "openai", "gemini", "ollama"]
        for provider in expected:
            assert provider in providers

    def test_provider_metadata_consistency(self):
        """Test that provider metadata is consistent."""
        for provider in list_available_providers():
            metadata = get_provider_metadata(provider)

            assert metadata.name == provider
            assert len(metadata.models) > 0
            assert metadata.default_model is not None
            assert metadata.default_model in metadata.models

    def test_config_with_optional_parameters(self):
        """Test config with various optional parameters."""
        config = LLMProviderConfig(
            provider="claude",
            temperature=0.8,
            max_tokens=1000,
            timeout=60,
        )

        assert config.temperature == 0.8
        assert config.max_tokens == 1000
        assert config.timeout == 60

    def test_usage_record_totals(self):
        """Test usage record token totals."""
        record = LLMUsageRecord(
            provider="claude",
            model="claude-3-5-sonnet-20241022",
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
            cost_usd=0.01,
        )

        assert record.total_tokens == 150
        assert record.input_tokens + record.output_tokens == record.total_tokens


# ===== Multi-Agent Scenarios =====
class TestMultiAgentWorkflows:
    """Test complex multi-agent workflow scenarios."""

    def test_three_agent_workflow(self):
        """Test workflow with three coordinating agents."""
        orchestrator = AgentOrchestrator()
        workflow_steps = []

        class StepAgent(Agent):
            def __init__(self, name, step_number, orchestrator):
                super().__init__(name, orchestrator)
                self.step_number = step_number

            def process(self, request):
                workflow_steps.append(self.step_number)
                return {"step": self.step_number}

        agents = []
        for i in range(1, 4):
            agent = StepAgent(f"step_{i}", i, orchestrator)
            agents.append(agent)
            orchestrator.register_agent(f"step_{i}", agent)

        for i in range(1, 4):
            orchestrator.process(f"step_{i}", {})

        assert workflow_steps == [1, 2, 3]

    def test_agent_pipeline_with_state_passing(self):
        """Test pipeline where agents pass state through orchestrator."""
        orchestrator = AgentOrchestrator()

        class PassthroughAgent(Agent):
            def process(self, request):
                current = self.orchestrator.get_state("pipeline", [])
                current.append(self.name)
                self.orchestrator.set_state("pipeline", current)
                return {"status": "passed"}

        for i in range(3):
            agent = PassthroughAgent(f"agent_{i}", orchestrator)
            orchestrator.register_agent(f"agent_{i}", agent)
            orchestrator.process(f"agent_{i}", {})

        final_state = orchestrator.get_state("pipeline")
        assert len(final_state) == 3
        assert final_state == ["agent_0", "agent_1", "agent_2"]


# ===== Error Handling Tests =====
class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_get_nonexistent_agent(self):
        """Test getting an agent that doesn't exist."""
        orchestrator = AgentOrchestrator()
        agent = orchestrator.get_agent("nonexistent")
        assert agent is None

    def test_event_emission_stress(self):
        """Test emitting many events in sequence."""
        emitter = EventEmitter()
        received = []

        emitter.on(EventType.LOG_INFO, lambda d: received.append(d))

        for i in range(50):
            emitter.emit(EventType.LOG_INFO, {"id": i})

        assert len(received) == 50

    def test_orchestrator_handles_exception_in_agent(self):
        """Test orchestrator continues when agent raises exception."""
        orchestrator = AgentOrchestrator()

        class FailingAgent(Agent):
            def process(self, request):
                raise ValueError("Test error")

        agent = FailingAgent("failing", orchestrator)
        orchestrator.register_agent("failing", agent)

        # Should handle gracefully
        try:
            orchestrator.process("failing", {})
        except ValueError:
            pass  # Expected


# ===== Concrete Agent Tests =====
class TestConcreteAgentBehavior:
    """Test specific agent implementations."""

    def test_knowledge_manager_agent_lifecycle(self):
        """Test knowledge manager agent initialization and operation."""
        orchestrator = AgentOrchestrator()
        agent = KnowledgeManagerAgent("Knowledge Manager", orchestrator)

        assert agent.name == "Knowledge Manager"
        assert agent.orchestrator == orchestrator
        assert hasattr(agent, "process")

    def test_multi_llm_agent_initialization(self):
        """Test multi-LLM agent setup."""
        orchestrator = AgentOrchestrator()
        agent = MultiLLMAgent(orchestrator)

        assert agent.name == "Multi-LLM Manager"
        assert agent.orchestrator == orchestrator

    def test_learning_agent_with_missing_library(self):
        """Test learning agent when socratic-learning might be unavailable."""
        orchestrator = AgentOrchestrator()
        agent = UserLearningAgent(orchestrator)

        assert agent.name == "User Learning"
        assert agent is not None

    def test_agent_process_request_passthrough(self):
        """Test that agents receive and process requests correctly."""
        orchestrator = AgentOrchestrator()

        class EchoAgent(Agent):
            def process(self, request):
                return {"received": request}

        agent = EchoAgent("echo", orchestrator)
        result = agent.process({"test": "data"})

        assert result["received"]["test"] == "data"

    def test_agent_emit_event_with_agent_name(self):
        """Test that emitted events include agent name."""
        orchestrator = AgentOrchestrator()
        emitted_data = []

        orchestrator.event_emitter.on(EventType.LOG_INFO, lambda d: emitted_data.append(d))

        class TestAgent(Agent):
            def process(self, request):
                self.emit_event(EventType.LOG_INFO, {"message": "test"})
                return {}

        agent = TestAgent("TestAgent", orchestrator)
        agent.process({})

        assert len(emitted_data) == 1
        assert emitted_data[0]["agent"] == "TestAgent"
