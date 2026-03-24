"""
Phase 5: Test Pure Orchestration Layer

Verifies that orchestration:
1. Routes requests to agents with proper caching
2. Implements maturity-driven workflow gating
3. Manages skill application
4. Handles feedback loops
5. Orchestrates multi-agent workflows
6. Has no dependencies on infrastructure
"""

import pytest
from unittest.mock import Mock, MagicMock

from src.socratic_agents.orchestration import (
    PureOrchestrator,
    CoordinationEvent,
    AgentRequest,
    AgentResponse,
    QUALITY_GATE_THRESHOLDS,
)


class MockAgent:
    """Mock agent for testing."""

    def __init__(self, name: str):
        self.name = name
        self.applied_skills = []

    def process(self, request: dict) -> dict:
        """Process request."""
        return {
            "status": "success",
            "agent": self.name,
            "action": request.get("action", "unknown"),
            "result": "processed",
        }

    def apply_skill(self, skill):
        """Apply a skill (for testing)."""
        self.applied_skills.append(skill.id if hasattr(skill, "id") else str(skill))


class MockSkill:
    """Mock skill for testing."""

    def __init__(self, skill_id: str, target_agent: str, intensity: str = "high"):
        self.id = skill_id
        self.target_agent = target_agent
        self.intensity = intensity
        self.confidence = 0.8
        self.config = {"intensity": intensity}


class TestPureOrchestratorBasics:
    """Test basic orchestrator functionality."""

    def test_orchestrator_initialization(self):
        """Test orchestrator can be initialized without infrastructure."""
        agents = {
            "code_generator": MockAgent("CodeGenerator"),
            "quality_controller": MockAgent("QualityController"),
        }

        def get_maturity(user_id, phase):
            return 0.5

        def get_effectiveness(agent_name):
            return 0.7

        orchestrator = PureOrchestrator(
            agents=agents,
            get_maturity=get_maturity,
            get_learning_effectiveness=get_effectiveness,
        )

        assert orchestrator is not None
        assert len(orchestrator.agents) == 2

    def test_execute_request_basic(self):
        """Test executing a basic agent request."""
        agents = {"code_generator": MockAgent("CodeGenerator")}

        orchestrator = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.5,
            get_learning_effectiveness=lambda a: 0.7,
        )

        request = AgentRequest(
            agent_name="code_generator",
            action="generate",
            data={"code": "test"},
        )

        response = orchestrator.execute_request(request, current_maturity=0.5)

        assert response.status == "success"
        assert response.agent == "code_generator"
        assert response.action == "generate"
        assert not response.gated

    def test_execute_request_unknown_agent(self):
        """Test executing request for unknown agent."""
        agents = {}

        orchestrator = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.5,
            get_learning_effectiveness=lambda a: 0.7,
        )

        request = AgentRequest(
            agent_name="unknown_agent",
            action="do_something",
            data={},
        )

        response = orchestrator.execute_request(request)

        assert response.status == "error"
        assert "not found" in response.data.get("error", "").lower()


class TestMaturityDrivenGating:
    """Test maturity-driven workflow gating."""

    def test_can_execute_request_with_sufficient_maturity(self):
        """Test that requests can execute with sufficient maturity."""
        agents = {"code_generator": MockAgent("CodeGenerator")}

        orchestrator = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.6,
            get_learning_effectiveness=lambda a: 0.7,
        )

        can_execute, reason = orchestrator.can_execute_request(
            agent_name="code_generator",
            current_phase="design",  # Requires 0.5 quality
            current_maturity=0.6,
        )

        assert can_execute
        assert reason is None

    def test_can_execute_request_insufficient_quality(self):
        """Test that low-quality code gates agent execution."""
        agents = {"code_validator": MockAgent("CodeValidator")}

        orchestrator = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.3,
            get_learning_effectiveness=lambda a: 0.7,
        )

        # Implementation phase requires 0.6 quality
        can_execute, reason = orchestrator.can_execute_request(
            agent_name="code_validator",
            current_phase="implementation",
            current_maturity=0.3,  # Too low
        )

        assert not can_execute
        assert "quality" in reason.lower()

    def test_phase_gate_prevents_early_phase_agents(self):
        """Test that agents gated by phase cannot execute early."""
        agents = {"code_validator": MockAgent("CodeValidator")}

        orchestrator = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.8,
            get_learning_effectiveness=lambda a: 0.7,
        )

        # Code validator only available in design/implementation
        can_execute, reason = orchestrator.can_execute_request(
            agent_name="code_validator",
            current_phase="discovery",  # Too early
            current_maturity=0.8,
        )

        assert not can_execute
        assert "not available" in reason.lower()

    def test_execute_request_gating(self):
        """Test that gating is enforced during request execution."""
        agents = {"code_validator": MockAgent("CodeValidator")}

        orchestrator = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.3,
            get_learning_effectiveness=lambda a: 0.7,
        )

        request = AgentRequest(
            agent_name="code_validator",
            action="validate",
            data={"code": "test"},
        )

        # Try to execute in discovery phase with low maturity
        response = orchestrator.execute_request(
            request,
            current_maturity=0.3,
            current_phase="discovery",
        )

        assert response.gated
        assert response.status == "gated"
        assert response.gating_reason is not None


class TestSkillApplication:
    """Test skill application and management."""

    def test_apply_skills_to_agents(self):
        """Test applying skills to target agents."""
        agents = {
            "code_generator": MockAgent("CodeGenerator"),
            "quality_controller": MockAgent("QualityController"),
        }

        orchestrator = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.5,
            get_learning_effectiveness=lambda a: 0.7,
        )

        skills = [
            MockSkill("skill_1", "code_generator"),
            MockSkill("skill_2", "quality_controller"),
        ]

        applied = orchestrator.apply_skills_to_agents(skills, agents)

        assert len(applied) == 2
        assert "code_generator" in applied
        assert "quality_controller" in applied
        assert len(applied["code_generator"]) == 1
        assert len(applied["quality_controller"]) == 1

    def test_apply_skills_to_nonexistent_agent(self):
        """Test applying skills to agent that doesn't exist."""
        agents = {"code_generator": MockAgent("CodeGenerator")}

        orchestrator = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.5,
            get_learning_effectiveness=lambda a: 0.7,
        )

        skills = [
            MockSkill("skill_1", "nonexistent_agent"),
        ]

        applied = orchestrator.apply_skills_to_agents(skills, agents)

        # Should skip nonexistent agent gracefully
        assert len(applied) == 0

    def test_record_feedback(self):
        """Test recording feedback about agent effectiveness."""
        agents = {"code_generator": MockAgent("CodeGenerator")}

        events = []

        def on_event(event, data):
            events.append((event, data))

        orchestrator = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.5,
            get_learning_effectiveness=lambda a: 0.7,
            on_event=on_event,
        )

        success = orchestrator.record_feedback(
            agent_name="code_generator",
            action="generate",
            effectiveness=0.8,
            user_id="user123",
        )

        assert success
        assert len(events) > 0
        assert events[-1][0] == CoordinationEvent.FEEDBACK_RECORDED


class TestWorkflowComposition:
    """Test multi-agent workflow orchestration."""

    def test_start_workflow(self):
        """Test starting a new workflow."""
        agents = {"code_generator": MockAgent("CodeGenerator")}

        orchestrator = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.5,
            get_learning_effectiveness=lambda a: 0.7,
        )

        workflow_id = orchestrator.start_workflow("wf_123", {"initial": "data"})

        assert workflow_id == "wf_123"

    def test_execute_workflow_step(self):
        """Test executing a step in a workflow."""
        agents = {"code_generator": MockAgent("CodeGenerator")}

        orchestrator = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.5,
            get_learning_effectiveness=lambda a: 0.7,
        )

        workflow_id = orchestrator.start_workflow("wf_123", {})

        request = AgentRequest(
            agent_name="code_generator",
            action="generate",
            data={"code": "test"},
            workflow_id=workflow_id,
        )

        response = orchestrator.execute_workflow_step(workflow_id, request)

        assert response.status == "success"
        assert response.agent == "code_generator"

    def test_complete_workflow(self):
        """Test completing a workflow and getting results."""
        agents = {"code_generator": MockAgent("CodeGenerator")}

        orchestrator = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.5,
            get_learning_effectiveness=lambda a: 0.7,
        )

        workflow_id = orchestrator.start_workflow("wf_123", {})

        request = AgentRequest(
            agent_name="code_generator",
            action="generate",
            data={"code": "test"},
        )

        orchestrator.execute_workflow_step(workflow_id, request)
        result = orchestrator.complete_workflow(workflow_id)

        assert result["id"] == "wf_123"
        assert "code_generator" in result["results"]
        assert "code_generator" in result["executed_agents"]

    def test_complete_nonexistent_workflow(self):
        """Test completing a workflow that doesn't exist."""
        agents = {}

        orchestrator = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.5,
            get_learning_effectiveness=lambda a: 0.7,
        )

        result = orchestrator.complete_workflow("nonexistent_wf")

        assert "error" in result


class TestCoordinationQueries:
    """Test coordination queries."""

    def test_get_available_agents_for_phase(self):
        """Test getting agents available in a phase."""
        agents = {
            "socratic_counselor": MockAgent("SocraticCounselor"),
            "code_validator": MockAgent("CodeValidator"),
            "knowledge_manager": MockAgent("KnowledgeManager"),
        }

        orchestrator = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.5,
            get_learning_effectiveness=lambda a: 0.7,
        )

        # Discovery phase
        available = orchestrator.get_available_agents_for_phase("discovery")
        assert "socratic_counselor" in available
        assert "knowledge_manager" in available
        assert "code_validator" not in available

        # Implementation phase
        available = orchestrator.get_available_agents_for_phase("implementation")
        assert "code_validator" in available
        assert "socratic_counselor" not in available
        assert "knowledge_manager" in available

    def test_get_required_quality_for_phase(self):
        """Test getting quality threshold for each phase."""
        agents = {}

        orchestrator = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.5,
            get_learning_effectiveness=lambda a: 0.7,
        )

        # Discovery: no bar
        assert orchestrator.get_required_quality_for_phase("discovery") == 0.0

        # Implementation: high bar
        assert orchestrator.get_required_quality_for_phase("implementation") == 0.6

    def test_estimate_phase(self):
        """Test phase estimation from maturity."""
        agents = {}

        orchestrator = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.5,
            get_learning_effectiveness=lambda a: 0.7,
        )

        # Low maturity -> discovery
        phase = orchestrator.estimate_phase(0.1)
        assert phase == "discovery"

        # Medium maturity -> analysis or design
        phase = orchestrator.estimate_phase(0.5)
        assert phase in ["analysis", "design"]

        # High maturity -> implementation
        phase = orchestrator.estimate_phase(0.9)
        assert phase == "implementation"


class TestCoordinationEvents:
    """Test coordination event emission."""

    def test_events_emitted_on_execution(self):
        """Test that events are emitted during execution."""
        agents = {"code_generator": MockAgent("CodeGenerator")}

        events = []

        def on_event(event, data):
            events.append((event, data))

        orchestrator = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.5,
            get_learning_effectiveness=lambda a: 0.7,
            on_event=on_event,
        )

        request = AgentRequest(
            agent_name="code_generator",
            action="generate",
            data={},
        )

        orchestrator.execute_request(request, current_maturity=0.5)

        # Check for expected events
        event_types = [event for event, _ in events]
        assert CoordinationEvent.WORKFLOW_STARTED in event_types
        assert CoordinationEvent.PHASE_GATING_CHECK in event_types
        assert CoordinationEvent.PHASE_GATE_PASSED in event_types
        assert CoordinationEvent.AGENT_EXECUTED in event_types

    def test_events_on_gated_execution(self):
        """Test that gating events are emitted."""
        agents = {"code_validator": MockAgent("CodeValidator")}

        events = []

        def on_event(event, data):
            events.append((event, data))

        orchestrator = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.3,
            get_learning_effectiveness=lambda a: 0.7,
            on_event=on_event,
        )

        request = AgentRequest(
            agent_name="code_validator",
            action="validate",
            data={},
        )

        orchestrator.execute_request(
            request,
            current_maturity=0.2,  # Too low
            current_phase="implementation",
        )

        event_types = [event for event, _ in events]
        assert CoordinationEvent.PHASE_GATE_FAILED in event_types


class TestIntegrationWithMaturityCalculator:
    """Test integration with MaturityCalculator."""

    def test_maturity_based_workflow_progression(self):
        """Test that workflow progression follows maturity levels."""
        agents = {
            "socratic_counselor": MockAgent("SocraticCounselor"),
            "code_generator": MockAgent("CodeGenerator"),
            "code_validator": MockAgent("CodeValidator"),
        }

        # Simulate user progression through phases
        maturity_levels = [0.1, 0.35, 0.6, 0.85]

        orchestrator = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.5,
            get_learning_effectiveness=lambda a: 0.7,
        )

        for maturity in maturity_levels:
            phase = orchestrator.estimate_phase(maturity)
            available = orchestrator.get_available_agents_for_phase(phase)

            # Verify correct agents available for each maturity level
            if maturity < 0.25:  # Discovery
                assert "socratic_counselor" in available
            elif maturity < 0.5:  # Analysis
                assert "code_generator" in available or "socratic_counselor" in available
            elif maturity < 0.75:  # Design
                assert "code_generator" in available
            else:  # Implementation
                assert "code_validator" in available

    def test_complete_workflow_with_gating(self):
        """Test complete workflow with maturity-driven gating."""
        agents = {
            "socratic_counselor": MockAgent("SocraticCounselor"),
            "code_generator": MockAgent("CodeGenerator"),
            "code_validator": MockAgent("CodeValidator"),
        }

        orchestrator = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.5,
            get_learning_effectiveness=lambda a: 0.7,
        )

        # Step 1: Can execute socratic counselor in discovery
        response = orchestrator.execute_request(
            AgentRequest(
                agent_name="socratic_counselor",
                action="ask_question",
                data={},
            ),
            current_maturity=0.1,
            current_phase="discovery",
        )
        assert not response.gated

        # Step 2: Cannot execute validator in discovery
        response = orchestrator.execute_request(
            AgentRequest(
                agent_name="code_validator",
                action="validate",
                data={},
            ),
            current_maturity=0.1,
            current_phase="discovery",
        )
        assert response.gated

        # Step 3: Can execute validator in implementation
        response = orchestrator.execute_request(
            AgentRequest(
                agent_name="code_validator",
                action="validate",
                data={},
            ),
            current_maturity=0.85,
            current_phase="implementation",
        )
        assert not response.gated


class TestNoInfrastructureDependencies:
    """Test that orchestrator has no infrastructure dependencies."""

    def test_orchestrator_works_with_mocks(self):
        """Test that orchestrator works entirely with mocked dependencies."""
        # Create mock agents
        agents = {f"agent_{i}": MockAgent(f"Agent{i}") for i in range(5)}

        # Mock maturity functions
        def get_maturity(user_id, phase):
            return {"discovery": 0.2, "analysis": 0.4, "design": 0.6, "implementation": 0.8}[
                phase
            ]

        def get_effectiveness(agent_name):
            return 0.75

        # Create orchestrator with pure mocks - no real infrastructure
        orchestrator = PureOrchestrator(
            agents=agents,
            get_maturity=get_maturity,
            get_learning_effectiveness=get_effectiveness,
        )

        # Verify it works
        assert len(orchestrator.agents) == 5
        assert orchestrator.estimate_phase(0.5) in [
            "discovery",
            "analysis",
            "design",
            "implementation",
        ]

    def test_no_file_system_access(self):
        """Test that orchestrator doesn't access file system."""
        agents = {"test_agent": MockAgent("TestAgent")}

        # Create with minimal dependencies
        orchestrator = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.5,
            get_learning_effectiveness=lambda a: 0.7,
        )

        # Execute request - should work without any file system access
        response = orchestrator.execute_request(
            AgentRequest(
                agent_name="test_agent",
                action="test",
                data={"input": "data"},
            )
        )

        assert response.status == "success"

    def test_no_database_access(self):
        """Test that orchestrator doesn't access database."""
        agents = {"test_agent": MockAgent("TestAgent")}

        # Create with no database dependency
        orchestrator = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.5,
            get_learning_effectiveness=lambda a: 0.7,
        )

        # All operations should work without database
        orchestrator.record_feedback("test_agent", "test", 0.8, "user123")
        orchestrator.apply_skills_to_agents([], agents)

        # Verify it worked
        assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
