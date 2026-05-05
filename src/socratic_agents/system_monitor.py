from __future__ import annotations

"""
System monitoring agent for Socrates AI
"""

import asyncio
import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional

from socratic_agents.models import TokenUsage

from .base import Agent

if TYPE_CHECKING:
    from .agent_bus import AgentBus


class SystemMonitorAgent(Agent):
    """Monitors system health, token usage, and API limits"""

    def __init__(
        self,
        database_service: Optional[Any] = None,
        llm_service: Optional[Any] = None,
        vector_db_service: Optional[Any] = None,
        file_service: Optional[Any] = None,
        auth_service: Optional[Any] = None,
        event_emitter_service: Optional[Any] = None,
        agent_bus: Optional["AgentBus"] = None,
    ):
        super().__init__(
            "SystemMonitor",
            database_service=database_service,
            llm_service=llm_service,
            vector_db_service=vector_db_service,
            file_service=file_service,
            auth_service=auth_service,
            event_emitter_service=event_emitter_service,
            agent_bus=agent_bus,
        )
        self.token_usage = []
        self.connection_status = True
        self.last_health_check = datetime.datetime.now()

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process monitoring requests (synchronous wrapper)"""
        action = request.get("action")

        if action == "track_tokens":
            return self._track_tokens_sync(request)
        elif action == "check_health":
            return self._check_health_sync(request)
        elif action == "get_stats":
            return self._get_stats_sync(request)
        elif action == "check_limits":
            return self._check_limits_sync(request)

        return {"status": "error", "message": "Unknown action"}

    async def process_async(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process monitoring requests asynchronously"""
        action = request.get("action")

        if action == "track_tokens":
            return await self._track_tokens_async(request)
        elif action == "check_health":
            return await self._check_health_async(request)
        elif action == "get_stats":
            return await self._get_stats_async(request)
        elif action == "check_limits":
            return await self._check_limits_async(request)

        return {"status": "error", "message": "Unknown action"}

    def _track_tokens_sync(self, request: Dict) -> Dict:
        """Synchronous wrapper"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                return {"status": "error", "message": "Use process_async()"}
        except RuntimeError:
            pass
        return asyncio.run(self._track_tokens_async(request))

    async def _track_tokens_async(self, request: Dict) -> Dict:
        """Track API token usage"""
        usage = TokenUsage(
            input_tokens=request.get("input_tokens", 0),
            output_tokens=request.get("output_tokens", 0),
            total_tokens=request.get("total_tokens", 0),
            cost_estimate=request.get("cost_estimate", 0.0),
            timestamp=datetime.datetime.now(),
        )

        self.token_usage.append(usage)

        # Check if approaching limits
        total_tokens = sum(u.total_tokens for u in self.token_usage[-10:])
        warning = total_tokens > 50000  # Warning threshold

        return {
            "status": "success",
            "current_usage": usage,
            "warning": warning,
            "total_recent": total_tokens,
        }

    def _check_health_sync(self, request: Dict) -> Dict:
        """Synchronous wrapper"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                return {"status": "error", "message": "Use process_async()"}
        except RuntimeError:
            pass
        return asyncio.run(self._check_health_async(request))

    async def _check_health_async(self, request: Dict) -> Dict:
        """Check system health and API connection"""
        # Test Claude API connection
        try:
            if self.llm_service:
                await self.llm_service.test_connection()
            self.connection_status = True
            self.last_health_check = datetime.datetime.now()

            return {"status": "success", "connection": True, "last_check": self.last_health_check}
        except Exception as e:
            self.connection_status = False
            self.log(f"Health check failed: {e}", "ERROR")

            return {"status": "error", "connection": False, "error": str(e)}

    def _get_stats_sync(self, request: Dict) -> Dict:
        """Synchronous wrapper"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                return {"status": "error", "message": "Use process_async()"}
        except RuntimeError:
            pass
        return asyncio.run(self._get_stats_async(request))

    async def _get_stats_async(self, request: Dict) -> Dict:
        """Get system statistics"""
        total_tokens = sum(u.total_tokens for u in self.token_usage)
        total_cost = sum(u.cost_estimate for u in self.token_usage)

        return {
            "status": "success",
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "api_calls": len(self.token_usage),
            "connection_status": self.connection_status,
        }

    def _check_limits_sync(self, request: Dict) -> Dict:
        """Synchronous wrapper"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                return {"status": "error", "message": "Use process_async()"}
        except RuntimeError:
            pass
        return asyncio.run(self._check_limits_async(request))

    async def _check_limits_async(self, request: Dict) -> Dict:
        """Check if approaching usage limits"""
        recent_usage = sum(u.total_tokens for u in self.token_usage[-5:])
        warnings = []

        if recent_usage > 40000:
            warnings.append("High token usage detected")
        if not self.connection_status:
            warnings.append("API connection issues")

        return {"status": "success", "warnings": warnings, "recent_usage": recent_usage}
