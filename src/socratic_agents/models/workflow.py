"""
Workflow optimization models for Quality Controller

Provides data structures for workflow definition, path enumeration,
cost/risk calculation, and approval workflow management.
"""

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class WorkflowNodeType(Enum):
    """Types of nodes in a workflow graph"""

    PHASE_START = "phase_start"
    QUESTION_SET = "question_set"
    ANALYSIS = "analysis"
    DECISION = "decision"
    PHASE_END = "phase_end"
    VALIDATION = "validation"

    @staticmethod
    def from_value(value: str) -> "WorkflowNodeType":
        """Get enum from string value"""
        if isinstance(value, WorkflowNodeType):
            return value
        return WorkflowNodeType(value)


class PathDecisionStrategy(Enum):
    """Strategies for selecting optimal workflow path"""

    MINIMIZE_COST = "minimize_cost"
    MINIMIZE_RISK = "minimize_risk"
    BALANCED = "balanced"
    MAXIMIZE_QUALITY = "maximize_quality"
    USER_CHOICE = "user_choice"

    @staticmethod
    def from_value(value: str) -> "PathDecisionStrategy":
        """Get enum from string value"""
        if isinstance(value, PathDecisionStrategy):
            return value
        return PathDecisionStrategy(value)


@dataclass
class WorkflowNode:
    """Represents a step/node in a workflow graph"""

    node_id: str
    node_type: WorkflowNodeType
    label: str
    estimated_tokens: int = 0
    questions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def from_dict(data: dict) -> "WorkflowNode":
        """Deserialize from dictionary."""
        data = dict(data)
        if "node_type" in data:
            data["node_type"] = WorkflowNodeType.from_value(data["node_type"])
        return WorkflowNode(**data)

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        data = asdict(self)
        if "node_type" in data and isinstance(data["node_type"], WorkflowNodeType):
            data["node_type"] = data["node_type"].value
        return data


@dataclass
class WorkflowEdge:
    """Represents a transition/edge between workflow nodes"""

    from_node: str
    to_node: str
    probability: float = 1.0
    condition: Optional[str] = None
    cost: int = 0

    @staticmethod
    def from_dict(data: dict) -> "WorkflowEdge":
        """Deserialize from dictionary."""
        return WorkflowEdge(**data)

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return asdict(self)


@dataclass
class WorkflowPath:
    """Complete path through workflow with calculated metrics"""

    path_id: str
    nodes: List[str]  # Ordered list of node IDs in this path
    edges: List[str]  # Ordered list of edge IDs in this path
    total_cost_tokens: int = 0
    total_cost_usd: float = 0.0
    risk_score: float = 0.0
    rework_probability: float = 0.0
    incompleteness_risk: float = 0.0
    complexity_risk: float = 0.0
    category_coverage: Dict[str, float] = field(default_factory=dict)
    missing_categories: List[str] = field(default_factory=list)
    quality_score: float = 0.0
    expected_maturity_gain: float = 0.0
    roi_score: float = 0.0

    @staticmethod
    def from_dict(data: dict) -> "WorkflowPath":
        """Deserialize from dictionary."""
        return WorkflowPath(**data)

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return asdict(self)


@dataclass
class WorkflowDefinition:
    """Complete workflow graph definition with nodes, edges, and metadata"""

    workflow_id: str
    name: str
    phase: str  # "discovery", "analysis", "design", "implementation"
    nodes: Dict[str, WorkflowNode]  # node_id -> WorkflowNode
    edges: List[WorkflowEdge]
    start_node: str  # ID of start node
    end_nodes: List[str]  # IDs of possible end nodes
    strategy: str = "balanced"
    metadata: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def from_dict(data: dict) -> "WorkflowDefinition":
        """Deserialize from dictionary."""
        data = dict(data)
        # Convert nodes dict values to WorkflowNode objects if needed
        if "nodes" in data and data["nodes"]:
            data["nodes"] = {
                k: WorkflowNode.from_dict(v) if isinstance(v, dict) else v
                for k, v in data["nodes"].items()
            }
        # Convert edges list to WorkflowEdge objects if needed
        if "edges" in data and data["edges"]:
            data["edges"] = [
                WorkflowEdge.from_dict(e) if isinstance(e, dict) else e for e in data["edges"]
            ]
        return WorkflowDefinition(**data)

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        data = asdict(self)
        # Convert nested objects back to dicts
        if "nodes" in data and data["nodes"]:
            data["nodes"] = {
                k: v.to_dict() if hasattr(v, "to_dict") else v for k, v in data["nodes"].items()
            }
        if "edges" in data and data["edges"]:
            data["edges"] = [e.to_dict() if hasattr(e, "to_dict") else e for e in data["edges"]]
        return data


@dataclass
class WorkflowApprovalRequest:
    """Request for user/system approval of a workflow path"""

    request_id: str
    project_id: str
    phase: str
    workflow: WorkflowDefinition
    all_paths: List[WorkflowPath]
    recommended_path: WorkflowPath
    strategy: PathDecisionStrategy
    created_at: str
    requested_by: str
    status: str = "pending"  # "pending", "approved", "rejected"
    approved_path_id: Optional[str] = None
    approval_timestamp: Optional[str] = None

    @staticmethod
    def from_dict(data: dict) -> "WorkflowApprovalRequest":
        """Deserialize from dictionary."""
        data = dict(data)
        # Convert nested objects
        if "workflow" in data and isinstance(data["workflow"], dict):
            data["workflow"] = WorkflowDefinition.from_dict(data["workflow"])
        if "all_paths" in data and data["all_paths"]:
            data["all_paths"] = [
                WorkflowPath.from_dict(p) if isinstance(p, dict) else p for p in data["all_paths"]
            ]
        if "recommended_path" in data and isinstance(data["recommended_path"], dict):
            data["recommended_path"] = WorkflowPath.from_dict(data["recommended_path"])
        if "strategy" in data:
            data["strategy"] = PathDecisionStrategy.from_value(data["strategy"])
        return WorkflowApprovalRequest(**data)

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        data = asdict(self)
        # Convert nested objects
        if "workflow" in data and hasattr(data["workflow"], "to_dict"):
            data["workflow"] = data["workflow"].to_dict()
        if "all_paths" in data and data["all_paths"]:
            data["all_paths"] = [
                p.to_dict() if hasattr(p, "to_dict") else p for p in data["all_paths"]
            ]
        if "recommended_path" in data and hasattr(data["recommended_path"], "to_dict"):
            data["recommended_path"] = data["recommended_path"].to_dict()
        if "strategy" in data and isinstance(data["strategy"], PathDecisionStrategy):
            data["strategy"] = data["strategy"].value
        return data


@dataclass
class WorkflowExecutionState:
    """Tracks current execution state within an approved workflow path"""

    execution_id: str
    workflow_id: str
    approved_path_id: str
    current_node_id: str
    completed_nodes: List[str] = field(default_factory=list)
    remaining_nodes: List[str] = field(default_factory=list)
    actual_tokens_used: int = 0
    estimated_tokens_remaining: int = 0
    started_at: str = ""
    status: str = "active"  # "active", "completed", "paused"

    @staticmethod
    def from_dict(data: dict) -> "WorkflowExecutionState":
        """Deserialize from dictionary."""
        return WorkflowExecutionState(**data)

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return asdict(self)
