"""Authentication service interface - abstraction for user/auth operations."""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional


class AuthService(ABC):
    """Abstract interface for authentication and user management."""

    @abstractmethod
    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user information by ID."""
        pass

    @abstractmethod
    async def get_user_auth_method(self, user_id: str) -> str:
        """Get user's preferred auth method (api_key, oauth, etc.)."""
        pass

    @abstractmethod
    async def verify_credentials(self, user_id: str, password: str) -> bool:
        """Verify user credentials."""
        pass

    @abstractmethod
    async def get_user_api_keys(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's API keys."""
        pass

    @abstractmethod
    async def create_api_key(self, user_id: str, name: str) -> str:
        """Create a new API key for user."""
        pass

    @abstractmethod
    async def revoke_api_key(self, user_id: str, key_id: str) -> bool:
        """Revoke an API key."""
        pass

    @abstractmethod
    async def get_user_subscription(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's subscription information."""
        pass

    @abstractmethod
    async def check_subscription_active(self, user_id: str) -> bool:
        """Check if user has active subscription."""
        pass
