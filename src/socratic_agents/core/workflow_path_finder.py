"""WorkflowPathFinder - Enumerates all valid execution paths through workflow graph."""

from typing import Any, Dict, List, Optional, Set


class WorkflowPath:
    """Represents a valid execution path through the workflow."""

    def __init__(
        self,
        nodes: List[str],
        edges: Optional[List[str]] = None,
        covered_categories: Optional[List[str]] = None,
    ):
        """
        Initialize a workflow path.

        Args:
            nodes: List of node IDs in execution order
            edges: List of edge IDs connecting the nodes
            covered_categories: Categories covered by this path
        """
        self.nodes = nodes
        self.edges = edges or []
        self.covered_categories = covered_categories or []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "nodes": self.nodes,
            "edges": self.edges,
            "covered_categories": self.covered_categories,
            "step_count": len(self.nodes),
        }


class WorkflowPathFinder:
    """
    Finds all valid execution paths through a workflow graph using DFS.

    Enumerates all possible routes from start nodes to end nodes,
    avoiding infinite loops by tracking visited nodes per path branch.
    """

    def __init__(self, workflow_definition: Dict[str, Any]):
        """
        Initialize the path finder.

        Args:
            workflow_definition: Workflow graph with nodes, edges, and configuration
        """
        self.workflow = workflow_definition
        self.nodes = workflow_definition.get("nodes", {})
        self.edges = workflow_definition.get("edges", [])
        self.start_nodes = workflow_definition.get("start_nodes", [])
        self.end_nodes = workflow_definition.get("end_nodes", [])
        self.adjacency_list = self._build_adjacency_list()

    def find_all_paths(self) -> List[WorkflowPath]:
        """
        Find all valid paths from start nodes to end nodes.

        Returns:
            List of WorkflowPath objects representing all possible routes
        """
        all_paths = []

        for start in self.start_nodes:
            for end in self.end_nodes:
                paths = self._dfs_paths(start, end)
                for node_sequence, edge_sequence in paths:
                    categories = self._extract_covered_categories(node_sequence)
                    path = WorkflowPath(
                        nodes=node_sequence, edges=edge_sequence, covered_categories=categories
                    )
                    all_paths.append(path)

        return all_paths

    def _build_adjacency_list(self) -> Dict[str, List[tuple]]:
        """
        Build adjacency list representation of workflow graph.

        Returns:
            Dictionary mapping node IDs to list of (target_node_id, edge_id) tuples
        """
        adjacency = {}

        for node_id in self.nodes:
            adjacency[node_id] = []

        for edge in self.edges:
            source = edge.get("source")
            target = edge.get("target")
            edge_id = edge.get("id")

            if source and target:
                adjacency[source].append((target, edge_id))

        return adjacency

    def _dfs_paths(self, start: str, end: str) -> List[tuple]:
        """
        Use depth-first search to find all paths from start to end.

        Prevents infinite loops by tracking visited nodes per branch,
        while allowing nodes to be revisited across different branches.

        Args:
            start: Start node ID
            end: End node ID

        Returns:
            List of (node_sequence, edge_sequence) tuples
        """
        paths = []

        def dfs(current: str, target: str, visited: Set[str], nodes: List[str], edges: List[str]):
            """Recursive DFS helper."""
            if current == target:
                paths.append((nodes.copy(), edges.copy()))
                return

            # Mark as visited for this branch
            visited.add(current)

            # Explore neighbors
            for neighbor, edge_id in self.adjacency_list.get(current, []):
                if neighbor not in visited:
                    nodes.append(neighbor)
                    edges.append(edge_id)

                    dfs(neighbor, target, visited.copy(), nodes, edges)

                    nodes.pop()
                    edges.pop()

        dfs(start, end, set(), [start], [])
        return paths

    def _extract_covered_categories(self, node_sequence: List[str]) -> List[str]:
        """
        Extract covered categories from a node sequence.

        Different node types cover different categories:
        - Question nodes: cover goals, requirements, audience
        - Analysis nodes: cover analysis, tech_stack, constraints
        - Validation nodes: cover validation, testing

        Args:
            node_sequence: List of node IDs in the path

        Returns:
            List of covered category names
        """
        covered = set()

        for node_id in node_sequence:
            node = self.nodes.get(node_id, {})
            node_type = node.get("type", "")
            node_categories = node.get("covers_categories", [])

            # Add explicitly defined categories
            covered.update(node_categories)

            # Add implicit categories based on node type
            if "question" in node_type.lower():
                covered.update(["goals", "requirements", "audience"])
            elif "analysis" in node_type.lower():
                covered.update(["analysis", "tech_stack", "constraints"])
            elif "validation" in node_type.lower():
                covered.update(["validation", "testing"])
            elif "design" in node_type.lower():
                covered.update(["architecture", "design"])

        return list(covered)
