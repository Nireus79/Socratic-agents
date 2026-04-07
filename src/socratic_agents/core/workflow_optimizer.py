"""WorkflowOptimizer - Orchestrates workflow optimization and path selection."""

from enum import Enum
from typing import Any, Dict, List, Optional

from .workflow_cost_calculator import WorkflowCostCalculator
from .workflow_path_finder import WorkflowPath, WorkflowPathFinder
from .workflow_risk_calculator import WorkflowRiskCalculator


class DecisionStrategy(Enum):
    """Workflow optimization strategies."""

    MINIMIZE_COST = "minimize_cost"  # Select lowest token consumption
    MINIMIZE_RISK = "minimize_risk"  # Select lowest risk score
    MAXIMIZE_QUALITY = "maximize_quality"  # Select highest quality score
    BALANCED = "balanced"  # 50% cost, 30% risk, 20% quality
    USER_CHOICE = "user_choice"  # Return all options for manual selection


class WorkflowOptimizer:
    """
    Orchestrates workflow optimization and path selection.

    Four-step process:
    1. Enumerate all valid paths through workflow graph
    2. Calculate cost, risk, and quality metrics for each path
    3. Select optimal path using decision strategy
    4. Generate approval request with recommendations
    """

    def __init__(
        self,
        workflow_definition: Dict[str, Any],
        strategy: DecisionStrategy = DecisionStrategy.BALANCED,
    ):
        """
        Initialize the optimizer.

        Args:
            workflow_definition: Workflow graph definition
            strategy: Decision strategy for path selection
        """
        self.workflow = workflow_definition
        self.strategy = strategy
        self.path_finder = WorkflowPathFinder(workflow_definition)
        self.cost_calculator = WorkflowCostCalculator(pricing_model="balanced")
        self.risk_calculator = WorkflowRiskCalculator()

    def optimize_workflow(self) -> Dict[str, Any]:
        """
        Execute complete workflow optimization.

        Returns:
            Dictionary with analyzed paths, recommendation, and approval request
        """
        # Step 1: Enumerate all paths
        paths = self.path_finder.find_all_paths()

        if not paths:
            return {
                "status": "error",
                "message": "No valid paths found in workflow",
            }

        # Step 2: Calculate metrics for each path
        analyzed_paths = []
        for path in paths:
            metrics = self._calculate_path_metrics(path)
            analyzed_paths.append(
                {
                    "path": path.to_dict(),
                    "metrics": metrics,
                }
            )

        # Step 3: Select optimal path
        selected_path = self._select_optimal_path(analyzed_paths)

        # Step 4: Generate approval request
        approval_request = {
            "paths_analyzed": len(analyzed_paths),
            "selected_path_index": analyzed_paths.index(selected_path),
            "selection_strategy": self.strategy.value,
            "paths": analyzed_paths,
            "recommendation": {
                "reason": self._get_selection_reason(selected_path),
                "selected_metrics": selected_path["metrics"],
            },
        }

        return {
            "status": "success",
            "approval_request": approval_request,
        }

    def _calculate_path_metrics(self, path: WorkflowPath) -> Dict[str, Any]:
        """
        Calculate all metrics for a single path.

        Args:
            path: WorkflowPath object

        Returns:
            Dictionary with cost, risk, quality, and ROI metrics
        """
        nodes = path.nodes
        node_defs = self.workflow.get("nodes", {})

        # Cost metrics
        cost_result = self.cost_calculator.calculate_path_cost(nodes, node_defs)
        tokens = cost_result["total_tokens"]
        usd_cost = cost_result["usd_cost"]

        # Risk metrics
        risk_result = self.risk_calculator.calculate_risk(path.covered_categories, nodes, node_defs)

        # Quality score: coverage + complexity - risk penalty
        coverage_quality = 100 - (risk_result["incompleteness_risk"] * 100)
        complexity_quality = 100 - (risk_result["complexity_risk"] * 50)
        risk_penalty = risk_result["overall_risk_score"] * 30
        quality_score = max(0.0, min(100.0, coverage_quality + complexity_quality - risk_penalty))

        # Expected maturity gain
        maturity_gain = self._calculate_maturity_gain(
            len(path.covered_categories), len(nodes), risk_result["incompleteness_risk"]
        )

        # ROI: maturity points per 1000 tokens
        roi = (maturity_gain / max(tokens, 1)) * 1000 if tokens > 0 else 0

        return {
            "cost": {
                "tokens": tokens,
                "usd": usd_cost,
            },
            "risk": {
                "overall_score": risk_result["overall_risk_score"],
                "incompleteness": risk_result["incompleteness_risk"],
                "complexity": risk_result["complexity_risk"],
                "rework_probability": risk_result["rework_probability"],
            },
            "quality": {
                "score": round(quality_score, 1),
                "coverage_quality": round(coverage_quality, 1),
                "complexity_quality": round(complexity_quality, 1),
            },
            "maturity": {
                "estimated_gain": round(maturity_gain, 1),
                "roi_per_1000_tokens": round(roi, 2),
            },
            "coverage": {
                "categories_covered": len(path.covered_categories),
                "categories": path.covered_categories,
                "missing": risk_result["missing_categories"],
                "coverage_percentage": risk_result["coverage_percentage"],
            },
        }

    def _calculate_maturity_gain(
        self, categories_covered: int, path_length: int, incompleteness_risk: float
    ) -> float:
        """
        Estimate expected maturity gain from the path.

        Combines:
        - Coverage gain (70%) - how many categories covered
        - Complexity depth (30%) - how complex the path is

        Args:
            categories_covered: Number of categories covered
            path_length: Number of nodes in path
            incompleteness_risk: Incompleteness risk score

        Returns:
            Expected maturity gain (0-100)
        """
        # Coverage component: 70% weight
        # Maximum 8 categories, so 8/8 = 100%
        coverage_gain = (categories_covered / 8.0) * 70

        # Complexity component: 30% weight
        # Path length indicates thoroughness
        # Optimal is 3-5 nodes, penalty for too short or too long
        optimal_length = 4
        length_difference = abs(path_length - optimal_length)
        complexity_penalty = min(30, length_difference * 3)
        complexity_gain = 30 - complexity_penalty

        # Total gain, capped at 100
        maturity_gain = min(100.0, coverage_gain + complexity_gain)

        return maturity_gain

    def _select_optimal_path(self, analyzed_paths: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Select optimal path based on decision strategy.

        Args:
            analyzed_paths: List of path analyses

        Returns:
            The selected path analysis dictionary
        """
        if self.strategy == DecisionStrategy.MINIMIZE_COST:
            return min(analyzed_paths, key=lambda p: p["metrics"]["cost"]["tokens"])

        elif self.strategy == DecisionStrategy.MINIMIZE_RISK:
            return min(analyzed_paths, key=lambda p: p["metrics"]["risk"]["overall_score"])

        elif self.strategy == DecisionStrategy.MAXIMIZE_QUALITY:
            return max(analyzed_paths, key=lambda p: p["metrics"]["quality"]["score"])

        elif self.strategy == DecisionStrategy.BALANCED:
            return self._select_balanced_path(analyzed_paths)

        elif self.strategy == DecisionStrategy.USER_CHOICE:
            # Return first path for user to manually review all
            return analyzed_paths[0]

        else:
            return analyzed_paths[0]

    def _select_balanced_path(self, analyzed_paths: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Select path using balanced strategy.

        Weights: 50% cost, 30% risk, 20% quality (inverted where lower is better)

        Args:
            analyzed_paths: List of path analyses

        Returns:
            The selected path
        """
        # Normalize all metrics to 0-1 range
        cost_values = [p["metrics"]["cost"]["tokens"] for p in analyzed_paths]
        risk_values = [p["metrics"]["risk"]["overall_score"] for p in analyzed_paths]
        quality_values = [p["metrics"]["quality"]["score"] for p in analyzed_paths]

        min_cost = min(cost_values)
        max_cost = max(cost_values)
        min_risk = min(risk_values)
        max_risk = max(risk_values)
        min_quality = min(quality_values)
        max_quality = max(quality_values)

        cost_range = max_cost - min_cost if max_cost > min_cost else 1
        risk_range = max_risk - min_risk if max_risk > min_risk else 1
        quality_range = max_quality - min_quality if max_quality > min_quality else 1

        scores = []
        for path in analyzed_paths:
            # Normalize to 0-1 (lower cost is better, so invert)
            cost_norm = 1.0 - ((path["metrics"]["cost"]["tokens"] - min_cost) / cost_range)
            risk_norm = 1.0 - ((path["metrics"]["risk"]["overall_score"] - min_risk) / risk_range)
            quality_norm = (path["metrics"]["quality"]["score"] - min_quality) / quality_range

            # Weighted combination
            balanced_score = (cost_norm * 0.50) + (risk_norm * 0.30) + (quality_norm * 0.20)
            scores.append(balanced_score)

        # Return path with highest balanced score
        best_index = scores.index(max(scores))
        return analyzed_paths[best_index]

    def _get_selection_reason(self, selected_path: Dict[str, Any]) -> str:
        """
        Generate human-readable reason for path selection.

        Args:
            selected_path: The selected path analysis

        Returns:
            Explanation of why this path was selected
        """
        metrics = selected_path["metrics"]
        cost = metrics["cost"]["tokens"]
        risk = metrics["risk"]["overall_score"]
        quality = metrics["quality"]["score"]
        coverage = metrics["coverage"]["coverage_percentage"]

        if self.strategy == DecisionStrategy.MINIMIZE_COST:
            return f"Lowest cost path: {cost} tokens, {quality:.0f}% quality"

        elif self.strategy == DecisionStrategy.MINIMIZE_RISK:
            return f"Lowest risk path: {risk:.1%} risk, {coverage:.0f}% coverage"

        elif self.strategy == DecisionStrategy.MAXIMIZE_QUALITY:
            return f"Highest quality path: {quality:.0f} score, {coverage:.0f}% coverage"

        elif self.strategy == DecisionStrategy.BALANCED:
            return (
                f"Balanced selection: {cost} tokens, {risk:.1%} risk, "
                f"{quality:.0f}% quality, {coverage:.0f}% coverage"
            )

        else:
            return "Path recommended for review"
