"""FastAPI application for agent services."""

from typing import Any, Optional

try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
except ImportError:
    raise ImportError("FastAPI is required. Install with: pip install socratic-agents[api]")

from .api_routes import create_agent_router, create_governance_router, create_precedent_router


def create_app(
    orchestrator: Any,
    governor: Optional[Any] = None,
    title: str = "Socratic Agents API",
    version: str = "1.0.0-alpha",
) -> FastAPI:
    """
    Create FastAPI application for agent services.

    Args:
        orchestrator: AgentOrchestrator instance
        governor: Optional Governor instance for governance endpoints
        title: API title
        version: API version

    Returns:
        FastAPI application instance
    """
    app = FastAPI(
        title=title,
        description="Multi-agent orchestration with constitutional AI governance",
        version=version,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check
    @app.get("/health")
    async def health_check() -> dict:
        """Health check endpoint."""
        return {
            "status": "healthy",
            "agents": len(orchestrator.list_agents()),
            "governor": "active" if governor else "inactive",
        }

    # Add routers
    app.include_router(create_agent_router(orchestrator))

    if governor:
        app.include_router(create_governance_router(governor))
        app.include_router(create_precedent_router(governor))

    # Error handlers
    @app.exception_handler(PermissionError)
    async def permission_error_handler(request, exc):
        return JSONResponse(
            status_code=403,
            content={"detail": str(exc), "type": "permission_error"},
        )

    return app


def run_api_server(
    orchestrator: Any,
    governor: Optional[Any] = None,
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = False,
) -> None:
    """
    Run the API server.

    Args:
        orchestrator: AgentOrchestrator instance
        governor: Optional Governor instance
        host: Host to bind to
        port: Port to bind to
        reload: Whether to enable auto-reload
    """
    import uvicorn

    app = create_app(orchestrator, governor)
    uvicorn.run(app, host=host, port=port, reload=reload)
