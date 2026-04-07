"""WorkflowRiskCalculator - Evaluates risk for workflow paths."""

from typing import Any, Dict, List


class WorkflowRiskCalculator:
    """
    Calculates risk metrics for workflow paths.

    Evaluates three risk dimensions:
    1. Incompleteness Risk (40%) - Coverage gaps
    2. Complexity Risk (30%) - Technical difficulty
    3. Rework Probability (30%) - Likelihood of rework needed
    """

    # Required categories for complete project
    REQUIRED_CATEGORIES = {
        "goals",
        "requirements",
        "audience",
        "constraints",
        "tech_stack",
        "architecture",
        "design",
        "testing",
    }

    # Token costs for complexity assessment
    NODE_TYPE_WEIGHTS = {
        "question": 20,  # Question sets are lightweight
        "analysis": 30,  # Analysis nodes are medium complexity
        "validation": 15,  # Validation nodes have low complexity
        "design": 35,  # Design nodes are complex
        "implementation": 40,  # Implementation is most complex
    }

    # Risk weights for overall calculation
    RISK_WEIGHTS = {
        "incompleteness": 0.40,
        "complexity": 0.30,
        "rework": 0.30,
    }

    def __init__(self, required_categories: List[str] = None):
        """
        Initialize risk calculator.

        Args:
            required_categories: Categories that must be covered (defaults to REQUIRED_CATEGORIES)
        """
        self.required_categories = set(required_categories or self.REQUIRED_CATEGORIES)

    def calculate_risk(
        self, covered_categories: List[str], nodes: List[str], node_definitions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate overall risk score for a workflow path.

        Args:
            covered_categories: Categories covered by the path
            nodes: Node IDs in the path
            node_definitions: Node configuration dictionary

        Returns:
            Dictionary with risk metrics and overall score
        """
        covered_set = set(covered_categories)

        # Calculate individual risk components
        incompleteness_risk = self._calculate_incompleteness_risk(covered_set)
        complexity_risk = self._calculate_complexity_risk(nodes, node_definitions)
        rework_probability = self._calculate_rework_probability(
            covered_set, len(nodes), incompleteness_risk
        )

        # Calculate overall risk (weighted combination)
        overall_risk = (
            (incompleteness_risk * self.RISK_WEIGHTS["incompleteness"])
            + (complexity_risk * self.RISK_WEIGHTS["complexity"])
            + (rework_probability * self.RISK_WEIGHTS["rework"])
        )

        # Identify missing categories
        missing_categories = list(self.required_categories - covered_set)

        return {
            "overall_risk_score": round(overall_risk, 3),
            "incompleteness_risk": round(incompleteness_risk, 3),
            "complexity_risk": round(complexity_risk, 3),
            "rework_probability": round(rework_probability, 3),
            "missing_categories": missing_categories,
            "missing_category_count": len(missing_categories),
            "coverage_percentage": round(
                (len(covered_set) / len(self.required_categories)) * 100, 1
            ),
        }

    def _calculate_incompleteness_risk(self, covered_categories: set) -> float:
        """
        Calculate incompleteness risk (40% weight in overall risk).

        Risk increases with percentage of missing categories.
        If 3 of 8 categories covered, incompleteness_risk = 0.625 (5/8)

        Args:
            covered_categories: Set of covered category names

        Returns:
            Incompleteness risk score (0.0-1.0)
        """
        missing_count = len(self.required_categories - covered_categories)
        total_required = len(self.required_categories)

        if total_required == 0:
            return 0.0

        incompleteness = missing_count / total_required
        return min(1.0, incompleteness)

    def _calculate_complexity_risk(
        self, nodes: List[str], node_definitions: Dict[str, Any]
    ) -> float:
        """
        Calculate complexity risk (30% weight in overall risk).

        Based on node types in the path. More complex nodes increase risk.
        Each node type contributes weighted points, capped at 100.

        Args:
            nodes: List of node IDs
            node_definitions: Node configuration dictionary

        Returns:
            Complexity risk score (0.0-1.0)
        """
        complexity_points = 0

        for node_id in nodes:
            node = node_definitions.get(node_id, {})
            node_type = node.get("type", "").lower()

            # Map node type to complexity weight
            for type_key, weight in self.NODE_TYPE_WEIGHTS.items():
                if type_key in node_type:
                    complexity_points += weight
                    break

        # Normalize to 0-1 range (cap at 100 points = 1.0)
        complexity_risk = min(1.0, complexity_points / 100.0)
        return complexity_risk

    def _calculate_rework_probability(
        self, covered_categories: set, path_length: int, incompleteness_risk: float
    ) -> float:
        """
        Calculate rework probability (30% weight in overall risk).

        Combines multiple factors:
        - Base incompleteness (80% weight)
        - Path length (2 points per node, max 20%)
        - Missing categories (5 points each, max 50%)

        Args:
            covered_categories: Set of covered categories
            path_length: Number of nodes in the path
            incompleteness_risk: Incompleteness risk score already calculated

        Returns:
            Rework probability score (0.0-1.0)
        """
        # Base component: 80% of incompleteness risk
        base_rework = incompleteness_risk * 0.80

        # Path length component: 2 points per node (max 20%)
        length_risk = min(0.20, (path_length * 0.02))

        # Missing categories component
        missing_count = len(self.required_categories - covered_categories)
        category_risk = min(0.50, missing_count * 0.05)

        # Combine components
        rework_prob = min(1.0, base_rework + length_risk + category_risk)

        return rework_prob

    def get_risk_details(
        self, covered_categories: List[str], nodes: List[str], node_definitions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get comprehensive risk analysis.

        Args:
            covered_categories: Categories covered by path
            nodes: Node IDs in path
            node_definitions: Node configurations

        Returns:
            Detailed risk analysis dictionary
        """
        risk_result = self.calculate_risk(covered_categories, nodes, node_definitions)

        return {
            "summary": {
                "overall_risk_score": risk_result["overall_risk_score"],
                "risk_level": self._get_risk_level(risk_result["overall_risk_score"]),
                "coverage_percentage": risk_result["coverage_percentage"],
            },
            "components": {
                "incompleteness_risk": risk_result["incompleteness_risk"],
                "complexity_risk": risk_result["complexity_risk"],
                "rework_probability": risk_result["rework_probability"],
            },
            "details": {
                "missing_categories": risk_result["missing_categories"],
                "path_length": len(nodes),
                "covered_categories": covered_categories,
            },
        }

    def _get_risk_level(self, risk_score: float) -> str:
        """
        Categorize risk score into qualitative level.

        Args:
            risk_score: Risk score (0.0-1.0)

        Returns:
            Risk level (low, medium, high, critical)
        """
        if risk_score < 0.25:
            return "low"
        elif risk_score < 0.50:
            return "medium"
        elif risk_score < 0.75:
            return "high"
        else:
            return "critical"
