"""User Manager Agent - User context, profiles, and preference management.

This agent:
1. Manages user profiles and accounts
2. Tracks user preferences and settings
3. Enforces role-based access control
4. Manages user activity and sessions
5. Handles notification preferences
6. Tracks user learning patterns
7. Manages user subscription status
8. Supports user deactivation and archival
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, cast

from .base import BaseAgent


class UserRole(Enum):
    """User roles with permission levels."""

    ADMIN = "admin"
    INSTRUCTOR = "instructor"
    STUDENT = "student"
    GUEST = "guest"


class UserStatus(Enum):
    """User account status."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"


class UserProfile:
    """Represents a user profile."""

    def __init__(self, user_id: str, email: str, full_name: str, role: UserRole = UserRole.STUDENT):
        self.user_id = user_id
        self.email = email
        self.full_name = full_name
        self.role = role
        self.status = UserStatus.ACTIVE
        self.created_at = datetime.utcnow()
        self.last_login: Optional[datetime] = None
        self.preferences: Dict[str, Any] = {}
        self.learning_stats = {
            "questions_answered": 0,
            "sessions_completed": 0,
            "learning_streak": 0,
            "total_time_minutes": 0,
        }
        self.notification_settings = {
            "email_notifications": True,
            "daily_digest": True,
            "immediate_alerts": False,
        }
        self.permissions: Set[str] = self._get_default_permissions(role)
        self.subscription_status = "free"
        self.subscription_expires: Optional[datetime] = None

    def _get_default_permissions(self, role: UserRole) -> Set[str]:
        """Get default permissions for a role."""
        permissions_map = {
            UserRole.ADMIN: {"read", "write", "delete", "manage_users", "manage_settings"},
            UserRole.INSTRUCTOR: {"read", "write", "view_analytics", "manage_courses"},
            UserRole.STUDENT: {"read", "write", "view_own_progress"},
            UserRole.GUEST: {"read"},
        }
        return permissions_map.get(role, {"read"})

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "user_id": self.user_id,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "preferences": self.preferences,
            "learning_stats": self.learning_stats,
            "subscription_status": self.subscription_status,
        }


class UserManager(BaseAgent):
    """
    Agent that manages user profiles, preferences, and access control.

    Provides:
    - User account creation and management
    - User profile management with detailed attributes
    - Role-based access control (RBAC)
    - Preference and settings management
    - Activity and session tracking
    - Notification preference management
    - Learning statistics and progress tracking
    - Subscription and quota management
    - User deactivation and archival
    """

    def __init__(self, llm_client: Optional[Any] = None):
        """Initialize the User Manager."""
        super().__init__(name="UserManager", llm_client=llm_client)
        self.users: Dict[str, UserProfile] = {}
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.user_activity: Dict[str, List[Dict[str, Any]]] = {}
        self.role_permissions: Dict[str, Set[str]] = {}
        self.quotas: Dict[str, Dict[str, int]] = {}

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process user management requests."""
        action = request.get("action", "list")

        if action == "create":
            return self.create_user(
                cast(str, request.get("user_id")),
                cast(str, request.get("email")),
                cast(str, request.get("full_name")),
                cast(str, request.get("role", "student")),
            )
        elif action == "get":
            return self.get_user(cast(str, request.get("user_id")))
        elif action == "update":
            return self.update_user(
                cast(str, request.get("user_id")),
                cast(Optional[Dict[str, Any]], request.get("updates")),
            )
        elif action == "update_preferences":
            return self.update_preferences(
                cast(str, request.get("user_id")),
                cast(Optional[Dict[str, Any]], request.get("preferences")),
            )
        elif action == "update_settings":
            return self.update_settings(
                cast(str, request.get("user_id")),
                cast(Optional[Dict[str, Any]], request.get("settings")),
            )
        elif action == "delete":
            return self.delete_user(cast(str, request.get("user_id")))
        elif action == "deactivate":
            return self.deactivate_user(cast(str, request.get("user_id")))
        elif action == "archive":
            return self.archive_user(cast(str, request.get("user_id")))
        elif action == "list":
            return self.list_users(
                cast(Optional[str], request.get("role")), cast(Optional[str], request.get("status"))
            )
        elif action == "start_session":
            return self.start_session(cast(str, request.get("user_id")))
        elif action == "end_session":
            return self.end_session(cast(str, request.get("session_id")))
        elif action == "record_activity":
            return self.record_activity(
                cast(str, request.get("user_id")),
                cast(Optional[Dict[str, Any]], request.get("activity")),
            )
        elif action == "get_activity":
            return self.get_user_activity(
                cast(str, request.get("user_id")), cast(int, request.get("limit", 10))
            )
        elif action == "grant_permission":
            return self.grant_permission(
                cast(str, request.get("user_id")), cast(str, request.get("permission"))
            )
        elif action == "revoke_permission":
            return self.revoke_permission(
                cast(str, request.get("user_id")), cast(str, request.get("permission"))
            )
        elif action == "check_permission":
            return self.check_permission(
                cast(str, request.get("user_id")), cast(str, request.get("permission"))
            )
        elif action == "update_learning_stats":
            return self.update_learning_stats(
                cast(str, request.get("user_id")),
                cast(Optional[Dict[str, int]], request.get("stats")),
            )
        elif action == "set_subscription":
            return self.set_subscription(
                cast(str, request.get("user_id")),
                cast(str, request.get("subscription_type")),
                cast(int, request.get("duration_days")),
            )
        elif action == "check_quota":
            return self.check_quota(
                cast(str, request.get("user_id")), cast(str, request.get("resource"))
            )
        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    def create_user(
        self, user_id: str, email: str, full_name: str, role: str = "student"
    ) -> Dict[str, Any]:
        """Create a new user."""
        if not user_id or not email or not full_name:
            return {"status": "error", "message": "User ID, email, and full name required"}

        if user_id in self.users:
            return {"status": "error", "message": f"User {user_id} already exists"}

        try:
            user_role = UserRole[role.upper()]
        except KeyError:
            return {"status": "error", "message": f"Invalid role: {role}"}

        user = UserProfile(user_id, email, full_name, user_role)
        self.users[user_id] = user
        self.user_activity[user_id] = []
        self.quotas[user_id] = {"queries": 1000, "storage_mb": 100}

        return {
            "status": "success",
            "agent": self.name,
            "user_id": user_id,
            "role": role,
            "total_users": len(self.users),
        }

    def get_user(self, user_id: str) -> Dict[str, Any]:
        """Get user profile."""
        if not user_id:
            return {"status": "error", "message": "User ID required"}

        if user_id not in self.users:
            return {"status": "error", "message": f"User {user_id} not found"}

        return {
            "status": "success",
            "agent": self.name,
            "user": self.users[user_id].to_dict(),
        }

    def update_user(self, user_id: str, updates: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Update user profile."""
        if not user_id:
            return {"status": "error", "message": "User ID required"}

        if user_id not in self.users:
            return {"status": "error", "message": f"User {user_id} not found"}

        user = self.users[user_id]
        updates = updates or {}

        if "email" in updates:
            user.email = updates["email"]
        if "full_name" in updates:
            user.full_name = updates["full_name"]

        return {
            "status": "success",
            "agent": self.name,
            "user_id": user_id,
            "updated": True,
        }

    def update_preferences(
        self, user_id: str, preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Update user preferences."""
        if not user_id:
            return {"status": "error", "message": "User ID required"}

        if user_id not in self.users:
            return {"status": "error", "message": f"User {user_id} not found"}

        user = self.users[user_id]
        user.preferences.update(preferences or {})

        return {
            "status": "success",
            "agent": self.name,
            "user_id": user_id,
            "preferences": user.preferences,
        }

    def update_settings(
        self, user_id: str, settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Update user notification settings."""
        if not user_id:
            return {"status": "error", "message": "User ID required"}

        if user_id not in self.users:
            return {"status": "error", "message": f"User {user_id} not found"}

        user = self.users[user_id]
        user.notification_settings.update(settings or {})

        return {
            "status": "success",
            "agent": self.name,
            "user_id": user_id,
            "notification_settings": user.notification_settings,
        }

    def delete_user(self, user_id: str) -> Dict[str, Any]:
        """Delete a user (permanent)."""
        if not user_id:
            return {"status": "error", "message": "User ID required"}

        if user_id not in self.users:
            return {"status": "error", "message": f"User {user_id} not found"}

        del self.users[user_id]
        if user_id in self.user_activity:
            del self.user_activity[user_id]
        if user_id in self.quotas:
            del self.quotas[user_id]

        return {
            "status": "success",
            "agent": self.name,
            "user_id": user_id,
            "deleted": True,
        }

    def deactivate_user(self, user_id: str) -> Dict[str, Any]:
        """Deactivate a user account."""
        if not user_id:
            return {"status": "error", "message": "User ID required"}

        if user_id not in self.users:
            return {"status": "error", "message": f"User {user_id} not found"}

        self.users[user_id].status = UserStatus.INACTIVE

        return {
            "status": "success",
            "agent": self.name,
            "user_id": user_id,
            "new_status": "inactive",
        }

    def archive_user(self, user_id: str) -> Dict[str, Any]:
        """Archive a user account."""
        if not user_id:
            return {"status": "error", "message": "User ID required"}

        if user_id not in self.users:
            return {"status": "error", "message": f"User {user_id} not found"}

        self.users[user_id].status = UserStatus.ARCHIVED

        return {
            "status": "success",
            "agent": self.name,
            "user_id": user_id,
            "new_status": "archived",
        }

    def list_users(
        self, role: Optional[str] = None, status: Optional[str] = None
    ) -> Dict[str, Any]:
        """List users with optional filtering."""
        users = list(self.users.values())

        if role:
            users = [u for u in users if u.role.value == role]

        if status:
            users = [u for u in users if u.status.value == status]

        return {
            "status": "success",
            "agent": self.name,
            "user_count": len(users),
            "users": [u.to_dict() for u in users],
        }

    def start_session(self, user_id: str) -> Dict[str, Any]:
        """Start a user session."""
        if not user_id:
            return {"status": "error", "message": "User ID required"}

        if user_id not in self.users:
            return {"status": "error", "message": f"User {user_id} not found"}

        session_id = f"session_{datetime.utcnow().timestamp()}"
        self.sessions[session_id] = {
            "user_id": user_id,
            "started_at": datetime.utcnow().isoformat(),
            "ended_at": None,
        }

        self.users[user_id].last_login = datetime.utcnow()

        return {
            "status": "success",
            "agent": self.name,
            "session_id": session_id,
            "user_id": user_id,
        }

    def end_session(self, session_id: str) -> Dict[str, Any]:
        """End a user session."""
        if not session_id:
            return {"status": "error", "message": "Session ID required"}

        if session_id not in self.sessions:
            return {"status": "error", "message": f"Session {session_id} not found"}

        self.sessions[session_id]["ended_at"] = datetime.utcnow().isoformat()

        return {
            "status": "success",
            "agent": self.name,
            "session_id": session_id,
            "ended": True,
        }

    def record_activity(
        self, user_id: str, activity: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Record user activity."""
        if not user_id:
            return {"status": "error", "message": "User ID required"}

        if user_id not in self.users:
            return {"status": "error", "message": f"User {user_id} not found"}

        activity = activity or {}
        activity["timestamp"] = datetime.utcnow().isoformat()

        self.user_activity[user_id].append(activity)

        return {
            "status": "success",
            "agent": self.name,
            "user_id": user_id,
            "activity_recorded": True,
        }

    def get_user_activity(self, user_id: str, limit: int = 10) -> Dict[str, Any]:
        """Get user activity history."""
        if not user_id:
            return {"status": "error", "message": "User ID required"}

        if user_id not in self.users:
            return {"status": "error", "message": f"User {user_id} not found"}

        activity = self.user_activity.get(user_id, [])[-limit:]

        return {
            "status": "success",
            "agent": self.name,
            "user_id": user_id,
            "activity_count": len(activity),
            "activity": activity,
        }

    def grant_permission(self, user_id: str, permission: str) -> Dict[str, Any]:
        """Grant permission to user."""
        if not user_id or not permission:
            return {"status": "error", "message": "User ID and permission required"}

        if user_id not in self.users:
            return {"status": "error", "message": f"User {user_id} not found"}

        self.users[user_id].permissions.add(permission)

        return {
            "status": "success",
            "agent": self.name,
            "user_id": user_id,
            "permission": permission,
            "granted": True,
        }

    def revoke_permission(self, user_id: str, permission: str) -> Dict[str, Any]:
        """Revoke permission from user."""
        if not user_id or not permission:
            return {"status": "error", "message": "User ID and permission required"}

        if user_id not in self.users:
            return {"status": "error", "message": f"User {user_id} not found"}

        self.users[user_id].permissions.discard(permission)

        return {
            "status": "success",
            "agent": self.name,
            "user_id": user_id,
            "permission": permission,
            "revoked": True,
        }

    def check_permission(self, user_id: str, permission: str) -> Dict[str, Any]:
        """Check if user has permission."""
        if not user_id or not permission:
            return {"status": "error", "message": "User ID and permission required"}

        if user_id not in self.users:
            return {"status": "error", "message": f"User {user_id} not found"}

        has_permission = permission in self.users[user_id].permissions

        return {
            "status": "success",
            "agent": self.name,
            "user_id": user_id,
            "permission": permission,
            "has_permission": has_permission,
        }

    def update_learning_stats(
        self, user_id: str, stats: Optional[Dict[str, int]] = None
    ) -> Dict[str, Any]:
        """Update user learning statistics."""
        if not user_id:
            return {"status": "error", "message": "User ID required"}

        if user_id not in self.users:
            return {"status": "error", "message": f"User {user_id} not found"}

        user = self.users[user_id]
        stats = stats or {}

        for key, value in stats.items():
            if key in user.learning_stats:
                user.learning_stats[key] = value

        return {
            "status": "success",
            "agent": self.name,
            "user_id": user_id,
            "learning_stats": user.learning_stats,
        }

    def set_subscription(
        self, user_id: str, subscription_type: str, duration_days: int = 30
    ) -> Dict[str, Any]:
        """Set user subscription."""
        if not user_id or not subscription_type:
            return {"status": "error", "message": "User ID and subscription type required"}

        if user_id not in self.users:
            return {"status": "error", "message": f"User {user_id} not found"}

        user = self.users[user_id]
        user.subscription_status = subscription_type
        user.subscription_expires = datetime.utcnow() + timedelta(days=duration_days)

        return {
            "status": "success",
            "agent": self.name,
            "user_id": user_id,
            "subscription": subscription_type,
            "expires": user.subscription_expires.isoformat(),
        }

    def check_quota(self, user_id: str, resource: str) -> Dict[str, Any]:
        """Check user resource quota."""
        if not user_id or not resource:
            return {"status": "error", "message": "User ID and resource required"}

        if user_id not in self.users:
            return {"status": "error", "message": f"User {user_id} not found"}

        quota = self.quotas.get(user_id, {})
        limit = quota.get(resource, 0)

        return {
            "status": "success",
            "agent": self.name,
            "user_id": user_id,
            "resource": resource,
            "limit": limit,
        }
