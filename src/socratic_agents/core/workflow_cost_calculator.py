"""WorkflowCostCalculator - Calculates token and USD costs for workflow paths."""

from typing import Any, Dict, List


class WorkflowCostCalculator:
    """
    Calculates API token consumption and USD costs for workflow paths.

    Uses operation-specific token estimates and pricing models from actual LLM APIs.
    """

    # Token cost per operation type
    TOKEN_COSTS = {
        "question_generation": 500,  # Generate Socratic questions
        "response_analysis": 1000,  # Analyze user responses
        "code_validation": 800,  # Validate code
        "maturity_calculation": 300,  # Calculate maturity metrics
        "skill_generation": 600,  # Generate adaptive skills
        "default": 400,  # Default for unknown operations
    }

    # USD pricing per token (from LLM provider APIs)
    PRICING_MODELS = {
        "input": 0.000015,  # $0.000015 per input token
        "output": 0.000075,  # $0.000075 per output token
        "balanced": 0.000045,  # Balanced average (~$0.045 per 1k tokens)
    }

    def __init__(self, pricing_model: str = "balanced"):
        """
        Initialize cost calculator.

        Args:
            pricing_model: Which pricing model to use (input, output, balanced)
        """
        self.pricing_model = pricing_model
        self.rate_per_token = self.PRICING_MODELS.get(pricing_model, 0.000045)

    def calculate_path_cost(self, nodes: List[str], node_definitions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate total cost for a workflow path.

        Args:
            nodes: List of node IDs in the path
            node_definitions: Dictionary of node configurations

        Returns:
            Dictionary with token_cost, usd_cost, and breakdown
        """
        total_tokens = 0
        cost_breakdown = []

        for node_id in nodes:
            node = node_definitions.get(node_id, {})
            node_type = node.get("type", "")

            # Get token cost for this node type
            tokens = self._estimate_tokens_for_node(node_type, node)
            total_tokens += tokens

            cost_breakdown.append({"node_id": node_id, "node_type": node_type, "tokens": tokens})

        # Convert to USD
        usd_cost = total_tokens * self.rate_per_token

        return {
            "total_tokens": total_tokens,
            "usd_cost": round(usd_cost, 6),
            "pricing_model": self.pricing_model,
            "breakdown": cost_breakdown,
        }

    def _estimate_tokens_for_node(self, node_type: str, node_config: Dict[str, Any]) -> int:
        """
        Estimate tokens for a specific node type.

        Args:
            node_type: Type of node (question, analysis, validation, etc.)
            node_config: Node configuration with optional token overrides

        Returns:
            Estimated token count
        """
        # Check for explicit token count
        if "tokens" in node_config:
            return node_config["tokens"]

        # Map node type to token cost
        node_type_lower = node_type.lower()

        if "question" in node_type_lower:
            return self.TOKEN_COSTS["question_generation"]
        elif "response" in node_type_lower or "answer" in node_type_lower:
            return self.TOKEN_COSTS["response_analysis"]
        elif "validation" in node_type_lower or "validator" in node_type_lower:
            return self.TOKEN_COSTS["code_validation"]
        elif "maturity" in node_type_lower:
            return self.TOKEN_COSTS["maturity_calculation"]
        elif "skill" in node_type_lower:
            return self.TOKEN_COSTS["skill_generation"]
        else:
            return self.TOKEN_COSTS["default"]

    def estimate_cost_per_node_type(self, node_type: str) -> Dict[str, float]:
        """
        Get cost estimate for a node type in different pricing models.

        Args:
            node_type: Type of node

        Returns:
            Dictionary with costs in different pricing models
        """
        tokens = self._estimate_tokens_for_node(node_type, {})

        return {
            "tokens": tokens,
            "input_cost": round(tokens * self.PRICING_MODELS["input"], 6),
            "output_cost": round(tokens * self.PRICING_MODELS["output"], 6),
            "balanced_cost": round(tokens * self.PRICING_MODELS["balanced"], 6),
        }

    def get_cost_breakdown(
        self, nodes: List[str], node_definitions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get detailed cost breakdown for a path.

        Args:
            nodes: List of node IDs
            node_definitions: Node configuration dictionary

        Returns:
            Detailed cost analysis across pricing models
        """
        cost_result = self.calculate_path_cost(nodes, node_definitions)
        tokens = cost_result["total_tokens"]

        return {
            "total_tokens": tokens,
            "input_tokens_cost": round(tokens * self.PRICING_MODELS["input"], 6),
            "output_tokens_cost": round(tokens * self.PRICING_MODELS["output"], 6),
            "balanced_cost": round(tokens * self.PRICING_MODELS["balanced"], 6),
            "breakdown": cost_result["breakdown"],
        }
