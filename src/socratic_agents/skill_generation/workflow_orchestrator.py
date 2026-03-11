"""Workflow Orchestrator for Phase 5: Multi-Agent Coordination."""

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from .workflow_skill import WorkflowSkill, WorkflowStep


@dataclass
class WorkflowStepResult:
    """Result of executing a single workflow step."""

    step_id: str
    agent_id: str
    skill_name: str
    success: bool
    output: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    retry_count: int = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class WorkflowResult:
    """Result of executing entire workflow."""

    workflow_id: str
    success: bool
    total_execution_time: float = 0.0
    steps_executed: int = 0
    steps_failed: int = 0
    step_results: List[WorkflowStepResult] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    def add_step_result(self, result: WorkflowStepResult) -> None:
        """Add a step result."""
        self.step_results.append(result)
        self.steps_executed += 1
        if not result.success:
            self.steps_failed += 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "workflow_id": self.workflow_id,
            "success": self.success,
            "total_execution_time": self.total_execution_time,
            "steps_executed": self.steps_executed,
            "steps_failed": self.steps_failed,
            "step_count": len(self.step_results),
            "errors": self.errors,
        }


class WorkflowOrchestrator:
    """Orchestrates execution of workflow skills."""

    def __init__(self):
        """Initialize the workflow orchestrator."""
        self.logger = logging.getLogger(f"socratic_agents.{self.__class__.__name__}")
        self.agent_registry: Dict[str, Any] = {}
        self.execution_history: List[WorkflowResult] = []

    def register_agent(self, agent_id: str, agent: Any) -> None:
        """
        Register an agent for workflow execution.

        Args:
            agent_id: Unique identifier for the agent
            agent: Agent instance with process() method
        """
        self.agent_registry[agent_id] = agent
        self.logger.info(f"Registered agent: {agent_id}")

    def execute_workflow(self, skill: WorkflowSkill, context: Dict[str, Any]) -> WorkflowResult:
        """
        Execute a workflow skill.

        Args:
            skill: WorkflowSkill to execute
            context: Shared context data for workflow

        Returns:
            WorkflowResult with execution details
        """
        # Validate workflow
        is_valid, errors = skill.validate_workflow()
        if not is_valid:
            return WorkflowResult(
                workflow_id=skill.workflow_id,
                success=False,
                errors=errors,
            )

        result = WorkflowResult(
            workflow_id=skill.workflow_id,
            success=True,
        )

        start_time = time.time()
        step_outputs: Dict[str, Any] = {}

        try:
            # Determine execution order
            execution_order = self._plan_execution(skill)

            # Execute steps
            for step_idx in execution_order:
                step = skill.workflow_steps[step_idx]
                step_id = f"step_{step_idx}"

                # Check if agent is registered
                if step.agent_id not in self.agent_registry:
                    error_msg = f"Agent not registered: {step.agent_id}"
                    result.errors.append(error_msg)
                    step_result = WorkflowStepResult(
                        step_id=step_id,
                        agent_id=step.agent_id,
                        skill_name=step.skill_name,
                        success=False,
                        error=error_msg,
                    )
                    result.add_step_result(step_result)
                    if step.error_handling == "skip":
                        continue
                    result.success = False
                    if step.error_handling == "abort":
                        break
                    continue

                # Prepare inputs
                step_inputs = self._prepare_step_inputs(step, step_outputs, context)

                # Execute step with retries
                step_result = self._execute_step_with_retry(step, step_id, step_inputs)

                result.add_step_result(step_result)
                if step_result.success:
                    step_outputs[step_id] = step_result.output
                else:
                    if step.error_handling == "abort":
                        result.success = False
                        break

        except Exception as e:
            self.logger.error(f"Workflow execution error: {str(e)}")
            result.success = False
            result.errors.append(str(e))

        # Finalize result
        result.total_execution_time = time.time() - start_time
        result.completed_at = datetime.utcnow()
        self.execution_history.append(result)

        return result

    def _plan_execution(self, skill: WorkflowSkill) -> List[int]:
        """
        Plan execution order considering dependencies.

        Returns:
            List of step indices in execution order
        """
        # Simple topological sort
        executed: set[int] = set()
        order: List[int] = []

        while len(executed) < len(skill.workflow_steps):
            # Find steps with no unexecuted dependencies
            ready_steps = []
            for i, step in enumerate(skill.workflow_steps):
                if i in executed:
                    continue

                # Parse dependencies
                all_deps_ready = True
                for dep_str in step.dependencies:
                    if dep_str.startswith("step_"):
                        dep_idx = int(dep_str.split("_")[1])
                        if dep_idx not in executed:
                            all_deps_ready = False
                            break

                if all_deps_ready:
                    ready_steps.append(i)

            if not ready_steps:
                # No progress - circular dependency or error
                self.logger.warning("No executable steps found")
                break

            # Execute ready steps (could be in parallel)
            for step_idx in ready_steps:
                order.append(step_idx)
                executed.add(step_idx)

        return order

    def _prepare_step_inputs(
        self,
        step: WorkflowStep,
        step_outputs: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Prepare inputs for a workflow step.

        Maps outputs from previous steps to inputs.
        """
        inputs = {}

        # Add context
        inputs.update(context)

        # Map previous outputs
        for input_name, mapping_source in step.input_mapping.items():
            if isinstance(mapping_source, str):
                if mapping_source in step_outputs:
                    inputs[input_name] = step_outputs[mapping_source]
                elif mapping_source in context:
                    inputs[input_name] = context[mapping_source]

        return inputs

    def _execute_step_with_retry(
        self,
        step: WorkflowStep,
        step_id: str,
        inputs: Dict[str, Any],
    ) -> WorkflowStepResult:
        """
        Execute a single step with retry logic.

        Returns:
            WorkflowStepResult with execution details
        """
        agent = self.agent_registry.get(step.agent_id)
        start_time = time.time()

        if agent is None:
            execution_time = time.time() - start_time
            return WorkflowStepResult(
                step_id=step_id,
                agent_id=step.agent_id,
                skill_name=step.skill_name,
                success=False,
                error="Agent not available",
                execution_time=execution_time,
            )

        retry_count = 0
        last_error = None

        while retry_count <= step.max_retries:
            try:
                # Execute step
                if hasattr(agent, "process"):
                    output = agent.process(
                        {
                            "action": step.skill_name,
                            **inputs,
                        }
                    )
                else:
                    output = getattr(agent, step.skill_name)(inputs)

                execution_time = time.time() - start_time
                return WorkflowStepResult(
                    step_id=step_id,
                    agent_id=step.agent_id,
                    skill_name=step.skill_name,
                    success=True,
                    output=output,
                    execution_time=execution_time,
                    retry_count=retry_count,
                )

            except Exception as e:
                last_error = str(e)
                retry_count += 1

                if retry_count <= step.max_retries:
                    self.logger.warning(
                        f"Step {step_id} failed, retrying ({retry_count}/{step.max_retries})"
                    )
                    time.sleep(0.5)  # Brief delay before retry

        # All retries exhausted
        execution_time = time.time() - start_time
        return WorkflowStepResult(
            step_id=step_id,
            agent_id=step.agent_id,
            skill_name=step.skill_name,
            success=False,
            error=last_error or "Unknown error",
            execution_time=execution_time,
            retry_count=retry_count,
        )

    def execute_parallel(self, steps: List[WorkflowStep]) -> Dict[str, Any]:
        """
        Execute multiple steps in parallel.

        Args:
            steps: List of WorkflowSteps to execute

        Returns:
            Dictionary with results from all steps
        """
        results = {}

        for i, step in enumerate(steps):
            step_id = f"parallel_step_{i}"
            result = self._execute_step_with_retry(step, step_id, {})
            results[step_id] = {
                "success": result.success,
                "output": result.output,
                "error": result.error,
            }

        return results

    def collect_workflow_metrics(self, result: WorkflowResult) -> Dict[str, Any]:
        """
        Collect metrics from workflow execution.

        Args:
            result: WorkflowResult to analyze

        Returns:
            Dictionary with workflow metrics
        """
        if not result.step_results:
            return {}

        execution_times = [s.execution_time for s in result.step_results]
        retry_counts = [s.retry_count for s in result.step_results]

        return {
            "workflow_id": result.workflow_id,
            "total_time": result.total_execution_time,
            "steps_count": result.steps_executed,
            "success_count": result.steps_executed - result.steps_failed,
            "failure_count": result.steps_failed,
            "success_rate": (
                (result.steps_executed - result.steps_failed) / result.steps_executed
                if result.steps_executed > 0
                else 0.0
            ),
            "avg_step_time": (
                sum(execution_times) / len(execution_times) if execution_times else 0.0
            ),
            "max_step_time": max(execution_times) if execution_times else 0.0,
            "min_step_time": min(execution_times) if execution_times else 0.0,
            "total_retries": sum(retry_counts),
            "avg_retries_per_step": sum(retry_counts) / len(retry_counts) if retry_counts else 0.0,
        }

    def get_execution_history(self, limit: int = 10) -> List[WorkflowResult]:
        """Get recent workflow execution history."""
        return self.execution_history[-limit:]

    def clear_history(self) -> None:
        """Clear execution history."""
        self.execution_history.clear()
