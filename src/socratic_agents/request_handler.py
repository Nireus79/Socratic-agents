"""
Request Handler - Standardizes agent request/response processing.

Provides consistent request validation, routing, and response formatting
across all agents.
"""

import logging
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)


class AgentResponse:
    """Standard response format for all agent operations."""

    def __init__(
        self,
        status: str,
        data: Optional[Dict[str, Any]] = None,
        message: str = "",
        error_code: Optional[str] = None,
    ):
        """
        Initialize agent response.

        Args:
            status: "success" or "error"
            data: Response data dictionary
            message: Human-readable message
            error_code: Optional error code for errors
        """
        self.status = status
        self.data = data or {}
        self.message = message
        self.error_code = error_code

    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        response = {
            "status": self.status,
            "data": self.data,
            "message": self.message,
        }
        if self.error_code:
            response["error_code"] = self.error_code
        return response

    @staticmethod
    def success(data: Dict[str, Any] = None, message: str = "Success") -> "AgentResponse":
        """Create a success response."""
        return AgentResponse(status="success", data=data, message=message)

    @staticmethod
    def error(
        message: str, error_code: str = "AGENT_ERROR", data: Dict[str, Any] = None
    ) -> "AgentResponse":
        """Create an error response."""
        return AgentResponse(status="error", data=data, message=message, error_code=error_code)


class RequestHandler:
    """
    Standardizes request validation, routing, and response handling.

    Ensures all agents follow a consistent request/response protocol.
    """

    def __init__(self):
        """Initialize request handler."""
        self.logger = logging.getLogger("socratic_agents.request_handler")

    @staticmethod
    def validate_request(request: Dict[str, Any]) -> bool:
        """
        Validate request format.

        Args:
            request: Request dictionary

        Returns:
            True if valid, False otherwise
        """
        if not isinstance(request, dict):
            return False
        # All requests should have at least an action
        return "action" in request

    @staticmethod
    def validate_response(response: Any) -> bool:
        """
        Validate response format.

        Args:
            response: Response from agent

        Returns:
            True if valid, False otherwise
        """
        if isinstance(response, AgentResponse):
            return True
        if isinstance(response, dict):
            return "status" in response and response["status"] in ["success", "error"]
        return False

    def normalize_response(self, response: Any) -> Dict[str, Any]:
        """
        Normalize agent response to standard format.

        Converts AgentResponse objects and raw dicts to standard format.

        Args:
            response: Raw response from agent

        Returns:
            Standardized response dictionary
        """
        if isinstance(response, AgentResponse):
            return response.to_dict()

        if isinstance(response, dict):
            # Ensure status field exists
            if "status" not in response:
                response["status"] = "success"
            if "data" not in response:
                response["data"] = {}
            if "message" not in response:
                response["message"] = ""
            return response

        # Fallback: wrap in standard format
        return {
            "status": "success",
            "data": {"result": response},
            "message": "Agent completed",
        }

    async def handle_request_async(
        self,
        agent: Any,
        request: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Handle asynchronous agent request.

        Args:
            agent: Agent instance
            request: Request dictionary

        Returns:
            Standardized response
        """
        try:
            if not self.validate_request(request):
                return AgentResponse.error("Invalid request format").to_dict()

            # Call agent's process_async if available, otherwise process
            if hasattr(agent, "process_async"):
                response = await agent.process_async(request)
            else:
                response = agent.process(request)

            # Normalize response
            return self.normalize_response(response)

        except Exception as e:
            self.logger.error(f"Error handling request: {e}", exc_info=True)
            return AgentResponse.error(str(e), error_code="REQUEST_ERROR").to_dict()

    def handle_request_sync(
        self,
        agent: Any,
        request: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Handle synchronous agent request.

        Args:
            agent: Agent instance
            request: Request dictionary

        Returns:
            Standardized response
        """
        try:
            if not self.validate_request(request):
                return AgentResponse.error("Invalid request format").to_dict()

            # Call agent's process method
            response = agent.process(request)

            # Normalize response
            return self.normalize_response(response)

        except Exception as e:
            self.logger.error(f"Error handling request: {e}", exc_info=True)
            return AgentResponse.error(str(e), error_code="REQUEST_ERROR").to_dict()
