"""User Manager Agent - User context and preference management."""

from typing import Any, Dict, Optional, List
from .base import BaseAgent


class UserManager(BaseAgent):
    """Agent that manages user context and preferences."""

    def __init__(self, llm_client: Optional[Any] = None):
        """Initialize the User Manager."""
        super().__init__(name="UserManager", llm_client=llm_client)
        self.users: Dict[str, Any] = {}

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process user management requests."""
        action = request.get("action", "list")
        if action == "create":
            return self.create_user(request.get("user_id"), request.get("preferences"))
        elif action == "update":
            return self.update_preferences(request.get("user_id"), request.get("preferences"))
        elif action == "get":
            return self.get_user(request.get("user_id"))
        elif action == "list":
            return self.list_users()
        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    def create_user(self, user_id: str, preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a new user."""
        if not user_id:
            return {"status": "error", "message": "User ID required"}
        self.users[user_id] = {"id": user_id, "preferences": preferences or {}}
        return {"status": "success", "agent": self.name, "user_id": user_id, "total_users": len(self.users)}

    def update_preferences(self, user_id: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Update user preferences."""
        if not user_id:
            return {"status": "error", "message": "User ID required"}
        if user_id not in self.users:
            return {"status": "error", "message": f"User {user_id} not found"}
        self.users[user_id]["preferences"].update(preferences or {})
        return {"status": "success", "agent": self.name, "user_id": user_id, "preferences_updated": True}

    def get_user(self, user_id: str) -> Dict[str, Any]:
        """Get user info."""
        if not user_id:
            return {"status": "error", "message": "User ID required"}
        if user_id not in self.users:
            return {"status": "error", "message": f"User {user_id} not found"}
        return {"status": "success", "agent": self.name, "user": self.users[user_id]}

    def list_users(self) -> Dict[str, Any]:
        """List all users."""
        return {"status": "success", "agent": self.name, "users": list(self.users.keys()), "user_count": len(self.users)}
