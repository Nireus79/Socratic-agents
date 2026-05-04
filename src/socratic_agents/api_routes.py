"""REST API routes for agent services."""

from typing import Any, Dict, List, Optional

try:
    from fastapi import APIRouter, HTTPException, Body, Query
    from pydantic import BaseModel, Field
except ImportError:
    raise ImportError(
        "FastAPI is required for REST API. Install with: pip install socratic-agents[api]"
    )


class AgentRequest(BaseModel):
    """Request model for agent processing."""

    action: str = Field(..., description="Action to perform")
    data: Dict[str, Any] = Field(default_factory=dict, description="Request data")
    high_impact: bool = Field(default=False, description="Whether this is high-impact")


class AgentResponse(BaseModel):
    """Response model from agent processing."""

    status: str
    data: Dict[str, Any] = Field(default_factory=dict)
    governance: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class GovernanceDecision(BaseModel):
    """Constitutional decision metadata."""

    decision_id: str
    allowed: bool
    decision_type: str
    confidence: float
    violations: Optional[List[Dict[str, str]]] = None


def create_agent_router(orchestrator: Any) -> APIRouter:
    """
    Create API router for agent operations.

    Args:
        orchestrator: AgentOrchestrator instance

    Returns:
        FastAPI APIRouter with agent endpoints
    """
    router = APIRouter(prefix="/agents", tags=["agents"])

    @router.get("/")
    async def list_agents() -> Dict[str, List[str]]:
        """List all available agents."""
        return {"agents": orchestrator.list_agents()}

    @router.get("/{agent_id}")
    async def get_agent_info(agent_id: str) -> Dict[str, Any]:
        """Get information about a specific agent."""
        agent = orchestrator.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent not found: {agent_id}")

        return {
            "id": agent_id,
            "name": getattr(agent, "name", agent_id),
            "type": agent.__class__.__name__,
        }

    @router.post("/{agent_id}/execute")
    async def execute_agent(agent_id: str, request: AgentRequest) -> AgentResponse:
        """Execute an agent with a request."""
        agent = orchestrator.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent not found: {agent_id}")

        try:
            result = await orchestrator.process_async(agent_id, request.dict())

            governance_data = result.pop("__governance__", None)

            return AgentResponse(
                status=result.get("status", "success"),
                data=result,
                governance=governance_data,
                error=result.get("error"),
            )
        except PermissionError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/{agent_id}/history")
    async def get_agent_history(
        agent_id: str,
        limit: int = Query(10, ge=1, le=100),
    ) -> Dict[str, Any]:
        """Get execution history for an agent."""
        # This would be populated by actual implementation
        # For now, return empty history
        return {
            "agent_id": agent_id,
            "history": [],
            "count": 0,
        }

    return router


def create_governance_router(governor: Any) -> APIRouter:
    """
    Create API router for governance operations.

    Args:
        governor: Governor instance

    Returns:
        FastAPI APIRouter with governance endpoints
    """
    router = APIRouter(prefix="/governance", tags=["governance"])

    @router.get("/decisions")
    async def list_decisions(limit: int = Query(10, ge=1, le=100)) -> Dict[str, Any]:
        """List recent governance decisions."""
        # Get from precedent engine
        if hasattr(governor, "precedent_engine"):
            stats = await governor.precedent_engine.get_statistics()
            return {"statistics": stats, "limit": limit}
        return {"decisions": [], "count": 0}

    @router.get("/constitution")
    async def get_constitution() -> Dict[str, Any]:
        """Get current constitution."""
        if hasattr(governor, "constitution"):
            return {"constitution": governor.constitution.to_dict()}
        return {"constitution": {}}

    @router.get("/principles")
    async def list_principles() -> Dict[str, List[str]]:
        """List all constitutional principles."""
        if hasattr(governor, "constitution"):
            principles = list(governor.constitution.principles.keys())
            return {"principles": principles}
        return {"principles": []}

    return router


def create_precedent_router(governor: Any) -> APIRouter:
    """
    Create API router for precedent operations.

    Args:
        governor: Governor instance

    Returns:
        FastAPI APIRouter with precedent endpoints
    """
    router = APIRouter(prefix="/precedents", tags=["precedents"])

    @router.get("/")
    async def list_precedents(
        limit: int = Query(10, ge=1, le=100),
    ) -> Dict[str, Any]:
        """List precedent cases."""
        if hasattr(governor, "precedent_engine"):
            cases = await governor.precedent_engine.get_all_cases()
            return {
                "cases": cases[:limit] if cases else [],
                "count": len(cases) if cases else 0,
            }
        return {"cases": [], "count": 0}

    @router.get("/{case_id}")
    async def get_precedent(case_id: str) -> Dict[str, Any]:
        """Get a specific precedent case."""
        if hasattr(governor, "precedent_engine"):
            case = await governor.precedent_engine.get_case(case_id)
            if case:
                return {"case": case}
        raise HTTPException(status_code=404, detail=f"Case not found: {case_id}")

    @router.post("/search")
    async def search_precedents(
        query: str = Body(...),
        limit: int = Query(10, ge=1, le=100),
    ) -> Dict[str, Any]:
        """Search precedent cases by action description."""
        if hasattr(governor, "precedent_engine"):
            similar = await governor.precedent_engine.find_similar_cases(query, limit=limit)
            return {
                "query": query,
                "results": similar,
                "count": len(similar),
            }
        return {"query": query, "results": [], "count": 0}

    return router
