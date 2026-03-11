"""Skill Composition for Phase 5: Combining Skills into Workflows."""

import logging
from typing import Any, Dict, List, Optional, Tuple

from .workflow_skill import WorkflowSkill, WorkflowStep


class SkillComposition:
    """Compose multiple skills into cohesive workflows."""

    def __init__(self):
        """Initialize skill composition engine."""
        self.logger = logging.getLogger(f"socratic_agents.{self.__class__.__name__}")
        self.skill_library: Dict[str, Dict[str, Any]] = {}
        self.composition_history: List[Dict[str, Any]] = []

    def register_skill(self, skill_id: str, skill_info: Dict[str, Any]) -> None:
        """
        Register a skill for composition.

        Args:
            skill_id: Unique skill identifier
            skill_info: Dict with 'agent_id', 'skill_name', 'output_type', etc.
        """
        self.skill_library[skill_id] = skill_info
        self.logger.debug(f"Registered skill: {skill_id}")

    def compose_skills(
        self, skills: List[str], goal: str, context: Optional[Dict[str, Any]] = None
    ) -> Optional[WorkflowSkill]:
        """
        Compose multiple skills into a workflow.

        Args:
            skills: List of skill IDs to compose
            goal: High-level goal for the workflow
            context: Optional context information

        Returns:
            WorkflowSkill or None if composition fails
        """
        if not skills:
            self.logger.warning("No skills provided for composition")
            return None

        # Determine optimal order
        ordered_skills = self._determine_skill_order(skills, goal)

        # Create workflow steps
        steps: List[WorkflowStep] = []
        for i, skill_id in enumerate(ordered_skills):
            if skill_id not in self.skill_library:
                self.logger.warning(f"Skill not found: {skill_id}")
                continue

            skill_info = self.skill_library[skill_id]

            step = WorkflowStep(
                agent_id=skill_info.get("agent_id", "unknown"),
                skill_name=skill_info.get("skill_name", skill_id),
                input_mapping=self._create_input_mapping(i, ordered_skills),
                error_handling="skip" if i < len(ordered_skills) - 1 else "abort",
                parallel_capable=skill_info.get("parallel_capable", False),
            )
            steps.append(step)

        # Create workflow skill
        workflow = WorkflowSkill(
            id=f"workflow_{goal.replace(' ', '_')}",
            target_agent="orchestrator",
            skill_type="workflow",
            config={"goal": goal, "skills": ordered_skills},
            confidence=self._estimate_workflow_confidence(ordered_skills),
            maturity_phase="execution",
            workflow_id=f"workflow_{goal.replace(' ', '_')}",
            workflow_steps=steps,
            parallel_capable=self._can_parallelize(steps),
        )

        # Track composition
        self.composition_history.append(
            {
                "goal": goal,
                "skills": skills,
                "ordered_skills": ordered_skills,
                "steps_count": len(steps),
            }
        )

        return workflow

    def find_skill_chain(self, start_skill: str, goal: str) -> List[str]:
        """
        Find a chain of skills from start to goal.

        Uses graph search to find optimal skill path.

        Args:
            start_skill: Starting skill ID
            goal: Goal description

        Returns:
            List of skill IDs forming a chain
        """
        if start_skill not in self.skill_library:
            return []

        visited: set[str] = set()
        chain: List[str] = [start_skill]

        current_skill = start_skill
        for _ in range(10):  # Limit search depth
            visited.add(current_skill)

            # Find next skill that gets closer to goal
            current_info = self.skill_library.get(current_skill, {})
            current_output = current_info.get("output_type", "unknown")

            next_skill = self._find_next_skill(current_output, goal, visited)

            if not next_skill:
                break

            chain.append(next_skill)
            current_skill = next_skill

            # Check if we reached goal
            if self._matches_goal(current_skill, goal):
                break

        return chain

    def optimize_skill_order(self, skills: List[str]) -> List[str]:
        """
        Optimize the execution order of skills.

        Considers dependencies and parallelization.

        Args:
            skills: List of skill IDs

        Returns:
            Optimized list of skill IDs
        """
        if len(skills) <= 1:
            return skills

        # Build dependency graph
        dependencies: Dict[str, List[str]] = {}
        for skill_id in skills:
            if skill_id in self.skill_library:
                deps = self.skill_library[skill_id].get("depends_on", [])
                dependencies[skill_id] = [d for d in deps if d in skills]

        # Topological sort
        sorted_skills: List[str] = []
        visited: set[str] = set()

        def visit(skill_id: str) -> None:
            if skill_id in visited:
                return
            visited.add(skill_id)

            for dep in dependencies.get(skill_id, []):
                visit(dep)

            sorted_skills.append(skill_id)

        for skill_id in skills:
            visit(skill_id)

        return sorted_skills

    def detect_skill_conflicts(self, skills: List[str]) -> List[Tuple[str, str, str]]:
        """
        Detect conflicts between skills.

        Returns:
            List of (skill1, skill2, conflict_description)
        """
        conflicts: List[Tuple[str, str, str]] = []

        for i, skill_a in enumerate(skills):
            for skill_b in skills[i + 1 :]:
                if skill_a not in self.skill_library or skill_b not in self.skill_library:
                    continue

                info_a = self.skill_library[skill_a]
                info_b = self.skill_library[skill_b]

                # Check for conflicting requirements
                if info_a.get("target_agent") == info_b.get("target_agent"):
                    if not info_a.get("can_run_together", True):
                        conflicts.append(
                            (
                                skill_a,
                                skill_b,
                                "Cannot run on same agent",
                            )
                        )

                # Check for input/output incompatibilities
                output_a = info_a.get("output_type", "any")
                input_b = info_b.get("input_type", "any")

                if output_a != "any" and input_b != "any" and output_a != input_b:
                    conflicts.append(
                        (
                            skill_a,
                            skill_b,
                            f"Output {output_a} incompatible with input {input_b}",
                        )
                    )

        return conflicts

    def _determine_skill_order(self, skills: List[str], goal: str) -> List[str]:
        """Determine optimal skill execution order."""
        # First, optimize based on dependencies
        ordered = self.optimize_skill_order(skills)

        # Then, reorder to match goal progression
        skill_scores = {}
        for skill_id in ordered:
            if skill_id in self.skill_library:
                skill_info = self.skill_library[skill_id]
                relevance = self._calculate_relevance(skill_info, goal)
                skill_scores[skill_id] = relevance

        # Sort by relevance (descending) while maintaining dependency order
        return sorted(ordered, key=lambda s: skill_scores.get(s, 0), reverse=True)

    def _create_input_mapping(self, step_index: int, skills: List[str]) -> Dict[str, Any]:
        """Create input mapping for a step based on previous step outputs."""
        mapping = {}

        if step_index > 0:
            prev_skill_id = skills[step_index - 1]
            if prev_skill_id in self.skill_library:
                # Map previous output
                mapping[f"input_{step_index}"] = f"step_{step_index - 1}"

        return mapping

    def _estimate_workflow_confidence(self, skills: List[str]) -> float:
        """Estimate confidence of composed workflow."""
        if not skills:
            return 0.5

        confidences = []
        for skill_id in skills:
            if skill_id in self.skill_library:
                skill_info = self.skill_library[skill_id]
                confidences.append(skill_info.get("confidence", 0.7))

        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.7

        # Reduce confidence for each step (accumulated error)
        reduction_factor = 0.95 ** len(skills)

        return min(1.0, avg_confidence * reduction_factor)

    def _can_parallelize(self, steps: List[WorkflowStep]) -> bool:
        """Check if workflow steps can be parallelized."""
        # Can parallelize if most steps have no dependencies
        parallel_capable = sum(1 for s in steps if s.parallel_capable)
        return parallel_capable > len(steps) * 0.5

    def _find_next_skill(self, current_output: str, goal: str, visited: set[str]) -> Optional[str]:
        """Find next skill in chain based on output type."""
        best_skill = None
        best_score = -1.0

        for skill_id, skill_info in self.skill_library.items():
            if skill_id in visited:
                continue

            # Check input compatibility
            input_type = skill_info.get("input_type", "any")
            if input_type != "any" and current_output != "any" and input_type != current_output:
                continue

            # Score based on relevance to goal
            relevance = self._calculate_relevance(skill_info, goal)
            if relevance > best_score:
                best_score = relevance
                best_skill = skill_id

        return best_skill

    def _matches_goal(self, skill_id: str, goal: str) -> bool:
        """Check if skill matches or completes goal."""
        if skill_id not in self.skill_library:
            return False

        skill_info = self.skill_library[skill_id]
        skill_goal = skill_info.get("goal", "").lower()
        goal_lower = goal.lower()

        # Simple keyword matching
        keywords = skill_goal.split()
        return any(keyword in goal_lower for keyword in keywords)

    def _calculate_relevance(self, skill_info: Dict[str, Any], goal: str) -> float:
        """Calculate relevance of a skill to a goal."""
        goal_lower = goal.lower()
        skill_goal = skill_info.get("goal", "").lower()

        # Keyword matching
        goal_words = set(goal_lower.split())
        skill_words = set(skill_goal.split())

        common_words = goal_words.intersection(skill_words)
        if not goal_words:
            return 0.0

        relevance = len(common_words) / len(goal_words)

        # Boost for description match
        description = skill_info.get("description", "").lower()
        if any(word in description for word in goal_words):
            relevance += 0.2

        return min(1.0, relevance)
