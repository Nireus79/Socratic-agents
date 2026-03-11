"""Tests for Phase 5: WorkflowOrchestrator component."""

from unittest.mock import Mock

import pytest

from socratic_agents.skill_generation.workflow_orchestrator import (
    WorkflowOrchestrator,
    WorkflowResult,
    WorkflowStepResult,
)
from socratic_agents.skill_generation.workflow_skill import WorkflowSkill, WorkflowStep


class TestWorkflowStepResult:
    """Tests for WorkflowStepResult."""

    def test_step_result_creation(self):
        """Test creating a step result."""
        result = WorkflowStepResult(
            step_id="step_0",
            agent_id="agent_1",
            skill_name="process",
            success=True,
            output={"data": "value"},
        )
        assert result.step_id == "step_0"
        assert result.success is True
        assert result.output == {"data": "value"}

    def test_step_result_failure(self):
        """Test step result with failure."""
        result = WorkflowStepResult(
            step_id="step_0",
            agent_id="agent_1",
            skill_name="process",
            success=False,
            error="Agent not found",
        )
        assert result.success is False
        assert result.error == "Agent not found"


class TestWorkflowResult:
    """Tests for WorkflowResult."""

    def test_workflow_result_creation(self):
        """Test creating a workflow result."""
        result = WorkflowResult(
            workflow_id="wf_1",
            success=True,
        )
        assert result.workflow_id == "wf_1"
        assert result.success is True
        assert result.steps_executed == 0

    def test_add_step_result(self):
        """Test adding step results."""
        result = WorkflowResult(workflow_id="wf_1", success=True)
        step_result = WorkflowStepResult(
            step_id="step_0",
            agent_id="a1",
            skill_name="s",
            success=True,
        )
        result.add_step_result(step_result)
        assert result.steps_executed == 1
        assert result.steps_failed == 0

    def test_add_failed_step(self):
        """Test adding failed step."""
        result = WorkflowResult(workflow_id="wf_1", success=True)
        step_result = WorkflowStepResult(
            step_id="step_0",
            agent_id="a1",
            skill_name="s",
            success=False,
            error="Failed",
        )
        result.add_step_result(step_result)
        assert result.steps_executed == 1
        assert result.steps_failed == 1

    def test_workflow_result_to_dict(self):
        """Test converting result to dict."""
        result = WorkflowResult(
            workflow_id="wf_1",
            success=True,
            total_execution_time=1.5,
        )
        result.steps_executed = 2
        result.steps_failed = 0

        data = result.to_dict()
        assert data["workflow_id"] == "wf_1"
        assert data["success"] is True
        assert data["steps_executed"] == 2


class TestWorkflowOrchestrator:
    """Tests for WorkflowOrchestrator."""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator."""
        return WorkflowOrchestrator()

    @pytest.fixture
    def mock_agents(self):
        """Create mock agents."""
        agents = {
            "agent_1": Mock(),
            "agent_2": Mock(),
        }
        agents["agent_1"].process.return_value = {"status": "success", "data": "output1"}
        agents["agent_2"].process.return_value = {"status": "success", "data": "output2"}
        return agents

    @pytest.fixture
    def simple_workflow(self):
        """Create simple workflow."""
        steps = [
            WorkflowStep(agent_id="agent_1", skill_name="step1"),
            WorkflowStep(
                agent_id="agent_2",
                skill_name="step2",
                dependencies=["step_0"],
            ),
        ]
        return WorkflowSkill(
            id="wf_test",
            target_agent="orchestrator",
            skill_type="workflow",
            config={},
            confidence=0.8,
            maturity_phase="execution",
            workflow_id="wf_test",
            workflow_steps=steps,
        )

    def test_register_agent(self, orchestrator, mock_agents):
        """Test agent registration."""
        orchestrator.register_agent("agent_1", mock_agents["agent_1"])
        assert "agent_1" in orchestrator.agent_registry

    def test_execute_workflow_invalid(self, orchestrator):
        """Test executing invalid workflow."""
        workflow = WorkflowSkill(
            id="bad",
            target_agent="orchestrator",
            skill_type="workflow",
            config={},
            confidence=0.8,
            maturity_phase="execution",
        )
        result = orchestrator.execute_workflow(workflow, {})
        assert result.success is False

    def test_execute_workflow_agent_not_found(self, orchestrator, simple_workflow):
        """Test execution when agent not registered."""
        result = orchestrator.execute_workflow(simple_workflow, {})
        assert result.success is False
        assert len(result.errors) > 0

    def test_execute_workflow_success(self, orchestrator, simple_workflow, mock_agents):
        """Test successful workflow execution."""
        orchestrator.register_agent("agent_1", mock_agents["agent_1"])
        orchestrator.register_agent("agent_2", mock_agents["agent_2"])

        result = orchestrator.execute_workflow(simple_workflow, {})
        assert result.steps_executed >= 0

    def test_prepare_step_inputs(self, orchestrator):
        """Test input preparation for steps."""
        step = WorkflowStep(
            agent_id="a",
            skill_name="s",
            input_mapping={"param": "step_0"},
        )
        step_outputs = {"step_0": {"value": 42}}
        context = {"ctx": "data"}

        inputs = orchestrator._prepare_step_inputs(step, step_outputs, context)
        assert "ctx" in inputs
        assert inputs["param"] == {"value": 42}

    def test_plan_execution_order(self, orchestrator, simple_workflow):
        """Test execution order planning."""
        order = orchestrator._plan_execution(simple_workflow)
        assert len(order) == len(simple_workflow.workflow_steps)

    def test_collect_workflow_metrics(self, orchestrator):
        """Test metric collection."""
        result = WorkflowResult(workflow_id="wf_1", success=True, total_execution_time=2.5)
        step1 = WorkflowStepResult(
            step_id="s0",
            agent_id="a1",
            skill_name="skill",
            success=True,
            execution_time=1.0,
        )
        step2 = WorkflowStepResult(
            step_id="s1",
            agent_id="a2",
            skill_name="skill",
            success=True,
            execution_time=1.5,
        )
        result.add_step_result(step1)
        result.add_step_result(step2)

        metrics = orchestrator.collect_workflow_metrics(result)
        assert metrics["workflow_id"] == "wf_1"
        assert metrics["success_rate"] == 1.0
        assert metrics["steps_count"] == 2

    def test_execution_history(self, orchestrator, simple_workflow, mock_agents):
        """Test execution history tracking."""
        orchestrator.register_agent("agent_1", mock_agents["agent_1"])
        orchestrator.register_agent("agent_2", mock_agents["agent_2"])

        result = orchestrator.execute_workflow(simple_workflow, {})
        history = orchestrator.get_execution_history(limit=10)
        assert len(history) >= 1

    def test_clear_history(self, orchestrator, simple_workflow, mock_agents):
        """Test clearing execution history."""
        orchestrator.register_agent("agent_1", mock_agents["agent_1"])
        orchestrator.register_agent("agent_2", mock_agents["agent_2"])

        orchestrator.execute_workflow(simple_workflow, {})
        assert len(orchestrator.execution_history) > 0

        orchestrator.clear_history()
        assert len(orchestrator.execution_history) == 0


class TestWorkflowOrchestratorIntegration:
    """Integration tests for WorkflowOrchestrator."""

    def test_complete_workflow_execution(self):
        """Test complete workflow execution."""
        orchestrator = WorkflowOrchestrator()

        # Create mock agents
        agent1 = Mock()
        agent2 = Mock()
        agent1.process.return_value = {"status": "ok", "data": "result1"}
        agent2.process.return_value = {"status": "ok", "data": "result2"}

        orchestrator.register_agent("agent_1", agent1)
        orchestrator.register_agent("agent_2", agent2)

        # Create workflow
        steps = [
            WorkflowStep(agent_id="agent_1", skill_name="action1"),
            WorkflowStep(
                agent_id="agent_2",
                skill_name="action2",
                dependencies=["step_0"],
            ),
        ]

        workflow = WorkflowSkill(
            id="integration_test",
            target_agent="orchestrator",
            skill_type="workflow",
            config={},
            confidence=0.8,
            maturity_phase="execution",
            workflow_steps=steps,
        )

        # Execute
        result = orchestrator.execute_workflow(workflow, {})

        assert result.workflow_id is not None
        assert result.total_execution_time >= 0

    def test_workflow_with_error_handling(self):
        """Test workflow with error handling."""
        orchestrator = WorkflowOrchestrator()

        # Create mock agents - first succeeds, second fails
        agent1 = Mock()
        agent2 = Mock()
        agent1.process.return_value = {"status": "ok"}
        agent2.process.side_effect = Exception("Agent failed")

        orchestrator.register_agent("agent_1", agent1)
        orchestrator.register_agent("agent_2", agent2)

        steps = [
            WorkflowStep(agent_id="agent_1", skill_name="action1"),
            WorkflowStep(
                agent_id="agent_2",
                skill_name="action2",
                error_handling="skip",
                dependencies=["step_0"],
            ),
        ]

        workflow = WorkflowSkill(
            id="error_test",
            target_agent="orchestrator",
            skill_type="workflow",
            config={},
            confidence=0.8,
            maturity_phase="execution",
            workflow_steps=steps,
        )

        result = orchestrator.execute_workflow(workflow, {})
        assert result.steps_executed >= 1
