from __future__ import annotations

"""
User management agent for Socrates AI
"""

import asyncio
from typing import TYPE_CHECKING, Any, Dict, Optional

from .base import Agent

if TYPE_CHECKING:
    from .agent_bus import AgentBus


class UserManagerAgent(Agent):
    """Manages user accounts, archival, and deletion"""

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
            "UserManager",
            database_service=database_service,
            llm_service=llm_service,
            vector_db_service=vector_db_service,
            file_service=file_service,
            auth_service=auth_service,
            event_emitter_service=event_emitter_service,
            agent_bus=agent_bus,
        )

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process user management requests (synchronous wrapper)"""
        action = request.get("action")

        if action == "archive_user":
            return self._archive_user_sync(request)
        elif action == "restore_user":
            return self._restore_user_sync(request)
        elif action == "delete_user_permanently":
            return self._delete_user_permanently_sync(request)
        elif action == "get_archived_users":
            return self._get_archived_users_sync(request)

        return {"status": "error", "message": "Unknown action"}

    async def process_async(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process user management requests asynchronously"""
        action = request.get("action")

        if action == "archive_user":
            return await self._archive_user_async(request)
        elif action == "restore_user":
            return await self._restore_user_async(request)
        elif action == "delete_user_permanently":
            return await self._delete_user_permanently_async(request)
        elif action == "get_archived_users":
            return await self._get_archived_users_async(request)

        return {"status": "error", "message": "Unknown action"}

    def _archive_user_sync(self, request: Dict) -> Dict:
        """Synchronous wrapper"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                return {"status": "error", "message": "Use process_async()"}
        except RuntimeError:
            pass
        return asyncio.run(self._archive_user_async(request))

    async def _archive_user_async(self, request: Dict) -> Dict:
        """Archive a user account"""
        username = request.get("username")
        requester = request.get("requester")
        archive_projects = request.get("archive_projects", True)

        # Users can only archive themselves
        if requester != username:
            return {"status": "error", "message": "Users can only archive their own accounts"}

        success = False
        if self.database_service:
            success = await self.database_service.archive_user(username, archive_projects)
        if success:
            self.log(f"Archived user '{username}'")
            return {"status": "success", "message": "Account archived successfully"}
        else:
            return {"status": "error", "message": "Failed to archive account"}

    def _restore_user_sync(self, request: Dict) -> Dict:
        """Synchronous wrapper"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                return {"status": "error", "message": "Use process_async()"}
        except RuntimeError:
            pass
        return asyncio.run(self._restore_user_async(request))

    async def _restore_user_async(self, request: Dict) -> Dict:
        """Restore an archived user account"""
        username = request.get("username")

        success = False
        if self.database_service:
            success = await self.database_service.restore_user(username)
        if success:
            self.log(f"Restored user '{username}'")
            return {"status": "success", "message": "Account restored successfully"}
        else:
            return {
                "status": "error",
                "message": "Failed to restore account or account not archived",
            }

    def _delete_user_permanently_sync(self, request: Dict) -> Dict:
        """Synchronous wrapper"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                return {"status": "error", "message": "Use process_async()"}
        except RuntimeError:
            pass
        return asyncio.run(self._delete_user_permanently_async(request))

    async def _delete_user_permanently_async(self, request: Dict) -> Dict:
        """Permanently delete a user account"""
        username = request.get("username")
        requester = request.get("requester")
        confirmation = request.get("confirmation", "")

        # Users can only delete themselves
        if requester != username:
            return {"status": "error", "message": "Users can only delete their own accounts"}

        # Require confirmation
        if confirmation != "DELETE":
            return {
                "status": "error",
                "message": 'Must type "DELETE" to confirm permanent deletion',
            }

        success = False
        if self.database_service:
            success = await self.database_service.permanently_delete_user(username)
        if success:
            self.log(f"PERMANENTLY DELETED user '{username}'")
            return {"status": "success", "message": "Account permanently deleted"}
        else:
            return {"status": "error", "message": "Failed to delete account"}

    def _get_archived_users_sync(self, request: Dict) -> Dict:
        """Synchronous wrapper"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                return {"status": "error", "message": "Use process_async()"}
        except RuntimeError:
            pass
        return asyncio.run(self._get_archived_users_async(request))

    async def _get_archived_users_async(self, request: Dict) -> Dict:
        """Get list of archived users"""
        archived = []
        if self.database_service:
            archived = await self.database_service.get_archived_items("users")
        return {"status": "success", "archived_users": archived}
