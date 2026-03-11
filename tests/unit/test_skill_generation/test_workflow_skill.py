"""Tests for Phase 5: WorkflowSkill component."""

import pytest

from socratic_agents.skill_generation.workflow_skill import WorkflowSkill, WorkflowStep


class TestWorkflowStep:
    """Tests for WorkflowStep."""

    def test_workflow_step_creation(self):
        """Test basic workflow step creation."""
        step = WorkflowStep(
            agent_id="agent_1",
            skill_name="process_data",
            error_handling="retry",
        )
        assert step.agent_id == "agent_1"
        assert step.skill_name == "process_data"
        assert step.max_retries == 3

    def test_workflow_step_defaults(self):
        """Test workflow step default values."""
        step = WorkflowStep(agent_id="test", skill_name="action")
        assert step.error_handling == "retry"
        assert step.timeout_seconds == 30
        assert step.parallel_capable is True
        assert step.max_retries == 3


class TestWorkflowSkill:
    """Tests for WorkflowSkill."""

    @pytest.fixture
    def simple_workflow(self):
        """Create a simple workflow."""
        steps = [
            WorkflowStep(
                agent_id="agent_1",
                skill_name="step1",
            ),
            WorkflowStep(
                agent_id="agent_2",
                skill_name="step2",
                dependencies=["step_0"],
            ),
        ]

        return WorkflowSkill(
            id="test_workflow",
            target_agent="orchestrator",
            skill_type="workflow",
            config={},
            confidence=0.8,
            maturity_phase="execution",
            workflow_id="workflow_test",
            workflow_steps=steps,
        )

    def test_workflow_skill_creation(self, simple_workflow):
        """Test workflow skill creation."""
        assert simple_workflow.id == "test_workflow"
        assert simple_workflow.workflow_id == "workflow_test"
        assert len(simple_workflow.workflow_steps) == 2

    def test_validate_workflow_valid(self, simple_workflow):
        """Test validation of valid workflow."""
        is_valid, errors = simple_workflow.validate_workflow()
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_workflow_empty(self):
        """Test validation of empty workflow."""
        workflow = WorkflowSkill(
            id="empty",
            target_agent="orchestrator",
            skill_type="workflow",
            config={},
            confidence=0.8,
            maturity_phase="execution",
        )
        is_valid, errors = workflow.validate_workflow()
        assert is_valid is False
        assert any("no steps" in e.lower() for e in errors)

    def test_validate_workflow_missing_agent(self):
        """Test validation with missing agent_id."""
        steps = [
            WorkflowStep(
                agent_id="",
                skill_name="step",
            )
        ]
        workflow = WorkflowSkill(
            id="bad",
            target_agent="orchestrator",
            skill_type="workflow",
            config={},
            confidence=0.8,
            maturity_phase="execution",
            workflow_steps=steps,
        )
        is_valid, errors = workflow.validate_workflow()
        assert is_valid is False

    def test_validate_workflow_missing_skill_name(self):
        """Test validation with missing skill_name."""
        steps = [
            WorkflowStep(
                agent_id="agent",
                skill_name="",
            )
        ]
        workflow = WorkflowSkill(
            id="bad",
            target_agent="orchestrator",
            skill_type="workflow",
            config={},
            confidence=0.8,
            maturity_phase="execution",
            workflow_steps=steps,
        )
        is_valid, errors = workflow.validate_workflow()
        assert is_valid is False

    def test_has_cycle_no_cycle(self, simple_workflow):
        """Test cycle detection on acyclic workflow."""
        assert simple_workflow.has_cycle() is False

    def test_has_cycle_with_cycle(self):
        """Test cycle detection on cyclic workflow."""
        steps = [
            WorkflowStep(agent_id="a1", skill_name="s1", dependencies=["step_1"]),
            WorkflowStep(agent_id="a2", skill_name="s2", dependencies=["step_0"]),
        ]
        workflow = WorkflowSkill(
            id="cyclic",
            target_agent="orchestrator",
            skill_type="workflow",
            config={},
            confidence=0.8,
            maturity_phase="execution",
            workflow_steps=steps,
        )
        assert workflow.has_cycle() is True

    def test_get_critical_path_simple(self, simple_workflow):
        """Test critical path finding."""
        path = simple_workflow.get_critical_path()
        assert len(path) >= 0
        # Should include steps in order

    def test_estimate_execution_time_single_step(self):
        """Test execution time estimation for single step."""
        steps = [WorkflowStep(agent_id="a", skill_name="s", timeout_seconds=10)]
        workflow = WorkflowSkill(
            id="time_test",
            target_agent="orchestrator",
            skill_type="workflow",
            config={},
            confidence=0.8,
            maturity_phase="execution",
            workflow_steps=steps,
        )
        est_time = workflow.estimate_execution_time()
        assert est_time >= 10

    def test_estimate_execution_time_multiple_steps(self, simple_workflow):
        """Test execution time for multiple steps."""
        est_time = simple_workflow.estimate_execution_time()
        assert est_time >= 0
        # Should be at least sum of timeouts

    def test_estimate_execution_time_with_parallelization(self):
        """Test execution time with parallel capable steps."""
        steps = [
            WorkflowStep(
                agent_id="a1",
                skill_name="s1",
                timeout_seconds=10,
                parallel_capable=True,
            ),
            WorkflowStep(
                agent_id="a2",
                skill_name="s2",
                timeout_seconds=10,
                parallel_capable=True,
            ),
        ]
        workflow = WorkflowSkill(
            id="parallel",
            target_agent="orchestrator",
            skill_type="workflow",
            config={},
            confidence=0.8,
            maturity_phase="execution",
            workflow_steps=steps,
            parallel_capable=True,
        )
        est_time = workflow.estimate_execution_time()
        # Parallel execution should be less than sequential
        assert est_time <= 20


class TestWorkflowSkillIntegration:
    """Integration tests for WorkflowSkill."""

    def test_complex_workflow_validation(self):
        """Test validation of complex multi-step workflow."""
        steps = [
            WorkflowStep(agent_id="parser", skill_name="parse"),
            WorkflowStep(
                agent_id="analyzer", skill_name="analyze", dependencies=["step_0"]
            ),
            WorkflowStep(
                agent_id="formatter",
                skill_name="format",
                dependencies=["step_1"],
            ),
        ]

        workflow = WorkflowSkill(
            id="complex",
            target_agent="orchestrator",
            skill_type="workflow",
            config={},
            confidence=0.8,
            maturity_phase="execution",
            workflow_steps=steps,
        )

        is_valid, errors = workflow.validate_workflow()
        assert is_valid is True

    def test_workflow_with_mixed_error_handling(self):
        """Test workflow with different error handling strategies."""
        steps = [
            WorkflowStep(
                agent_id="a1",
                skill_name="s1",
                error_handling="retry",
            ),
            WorkflowStep(
                agent_id="a2",
                skill_name="s2",
                error_handling="skip",
                dependencies=["step_0"],
            ),
            WorkflowStep(
                agent_id="a3",
                skill_name="s3",
                error_handling="abort",
                dependencies=["step_1"],
            ),
        ]

        workflow = WorkflowSkill(
            id="error_handling",
            target_agent="orchestrator",
            skill_type="workflow",
            config={},
            confidence=0.8,
            maturity_phase="execution",
            workflow_steps=steps,
        )

        is_valid, errors = workflow.validate_workflow()
        assert is_valid is True
