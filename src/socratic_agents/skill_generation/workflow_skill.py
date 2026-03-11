"""Workflow Skill model for Phase 5: Multi-Agent Orchestration."""

from dataclasses import dataclass, field
from typing import Any, Dict, List

from ..models.skill_models import AgentSkill


@dataclass
class WorkflowStep:
    """A single step in a workflow."""

    agent_id: str
    """Agent to execute this step."""

    skill_name: str
    """Skill or action for the agent to perform."""

    input_mapping: Dict[str, Any] = field(default_factory=dict)
    """Map outputs from previous steps to inputs for this step."""

    error_handling: str = "retry"
    """How to handle errors: 'retry', 'skip', or 'abort'."""

    max_retries: int = 3
    """Maximum retries for this step."""

    timeout_seconds: int = 30
    """Maximum time allowed for this step."""

    dependencies: List[str] = field(default_factory=list)
    """IDs of steps that must complete before this one."""

    parallel_capable: bool = True
    """Whether this step can run in parallel with others."""


@dataclass
class WorkflowSkill(AgentSkill):
    """
    Skill that orchestrates multiple agents.

    Extends AgentSkill to define complex multi-agent workflows with
    dependencies, error handling, and parallelization support.
    """

    workflow_id: str = ""
    """Unique identifier for the workflow."""

    workflow_steps: List[WorkflowStep] = field(default_factory=list)
    """Steps to execute in sequence or parallel."""

    agent_dependencies: Dict[str, List[str]] = field(default_factory=dict)
    """Mapping of agent_id to list of agents it depends on."""

    parallel_capable: bool = False
    """Whether the entire workflow can be parallelized."""

    max_parallel_steps: int = 4
    """Maximum steps to run in parallel."""

    workflow_timeout_seconds: int = 300
    """Total timeout for entire workflow."""

    def __post_init__(self) -> None:
        """Validate workflow after initialization."""
        if not self.workflow_id and self.id:
            self.workflow_id = f"workflow_{self.id}"

    def validate_workflow(self) -> tuple[bool, List[str]]:
        """
        Validate workflow structure and dependencies.

        Returns:
            (is_valid, error_messages)
        """
        errors: List[str] = []

        # Check for empty workflow
        if not self.workflow_steps:
            errors.append("Workflow has no steps")
            return False, errors

        # Track available step IDs
        available_steps = set()

        # Validate each step
        for i, step in enumerate(self.workflow_steps):
            step_id = f"step_{i}"
            available_steps.add(step_id)

            if not step.agent_id:
                errors.append(f"Step {step_id}: Missing agent_id")

            if not step.skill_name:
                errors.append(f"Step {step_id}: Missing skill_name")

            if step.timeout_seconds <= 0:
                errors.append(f"Step {step_id}: Invalid timeout")

            if step.error_handling not in ["retry", "skip", "abort"]:
                errors.append(f"Step {step_id}: Invalid error_handling")

            # Check dependencies exist
            for dep in step.dependencies:
                if dep not in available_steps and dep != "":
                    errors.append(f"Step {step_id}: Dependency '{dep}' not found")

        # Check for circular dependencies
        if self._has_circular_dependency():
            errors.append("Workflow has circular dependencies")

        return len(errors) == 0, errors

    def has_cycle(self) -> bool:
        """Detect circular dependencies in workflow."""
        return self._has_circular_dependency()

    def _has_circular_dependency(self) -> bool:
        """Check for circular dependencies using DFS."""
        visited: set[int] = set()
        rec_stack: set[int] = set()

        def has_cycle_util(step_idx: int) -> bool:
            visited.add(step_idx)
            rec_stack.add(step_idx)

            if step_idx < len(self.workflow_steps):
                step = self.workflow_steps[step_idx]
                for dep_str in step.dependencies:
                    # Convert dependency string to index
                    if dep_str.startswith("step_"):
                        dep_idx = int(dep_str.split("_")[1])
                        if dep_idx not in visited:
                            if has_cycle_util(dep_idx):
                                return True
                        elif dep_idx in rec_stack:
                            return True

            rec_stack.remove(step_idx)
            return False

        for i in range(len(self.workflow_steps)):
            if i not in visited:
                if has_cycle_util(i):
                    return True

        return False

    def get_critical_path(self) -> List[str]:
        """
        Get the critical path (longest dependency chain).

        Returns:
            List of step IDs representing critical path
        """
        if not self.workflow_steps:
            return []

        # Calculate depth for each step
        depths: Dict[int, int] = {}

        for i in range(len(self.workflow_steps)):
            depths[i] = self._calculate_depth(i, depths)

        # Find step with max depth
        max_depth_idx = max(depths, key=lambda k: depths[k]) if depths else 0

        # Trace back through dependencies
        path: List[str] = []
        current_idx = max_depth_idx

        visited_in_path: set[int] = set()
        while current_idx not in visited_in_path:
            visited_in_path.add(current_idx)
            path.insert(0, f"step_{current_idx}")

            # Find parent step with max depth
            if current_idx < len(self.workflow_steps):
                step = self.workflow_steps[current_idx]
                if step.dependencies:
                    # Get first dependency
                    dep_str = step.dependencies[0]
                    if dep_str.startswith("step_"):
                        current_idx = int(dep_str.split("_")[1])
                    else:
                        break
                else:
                    break
            else:
                break

        return path

    def _calculate_depth(self, step_idx: int, depths: Dict[int, int]) -> int:
        """Calculate dependency depth for a step."""
        if step_idx in depths:
            return depths[step_idx]

        if step_idx >= len(self.workflow_steps):
            return 0

        step = self.workflow_steps[step_idx]
        if not step.dependencies:
            return 1

        max_dep_depth = 0
        for dep_str in step.dependencies:
            if dep_str.startswith("step_"):
                dep_idx = int(dep_str.split("_")[1])
                if dep_idx < len(self.workflow_steps):
                    dep_depth = self._calculate_depth(dep_idx, depths)
                    max_dep_depth = max(max_dep_depth, dep_depth)

        return max_dep_depth + 1

    def estimate_execution_time(self) -> float:
        """
        Estimate total execution time in seconds.

        Assumes all steps run sequentially by default.
        Reduces time for steps that can run in parallel.

        Returns:
            Estimated time in seconds
        """
        if not self.workflow_steps:
            return 0.0

        # Simple sequential estimate
        total_time: float = sum(step.timeout_seconds for step in self.workflow_steps)

        # Reduce for parallelizable steps
        parallel_steps = [s for s in self.workflow_steps if s.parallel_capable]
        if len(parallel_steps) > 1 and self.parallel_capable:
            # Estimate: run every N steps in parallel
            parallel_groups = (
                len(parallel_steps) + self.max_parallel_steps - 1
            ) // self.max_parallel_steps
            avg_step_time = sum(s.timeout_seconds for s in parallel_steps) / len(parallel_steps)
            estimated_parallel_time = parallel_groups * avg_step_time
            total_time -= sum(s.timeout_seconds for s in parallel_steps) - estimated_parallel_time

        return total_time
