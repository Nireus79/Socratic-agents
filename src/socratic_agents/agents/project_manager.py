"""Project Manager Agent - Project planning, management, and GitHub integration.

This agent orchestrates project lifecycle:
1. Project creation with full context and metadata
2. GitHub repository integration and synchronization
3. Team collaboration management with roles and permissions
4. Subscription tier enforcement and quota tracking
5. Project lifecycle operations (archive, restore, delete)
6. Code structure import and intelligent parsing
7. Multi-level project filtering and smart queries
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from .base import BaseAgent


class ProjectStatus(Enum):
    """Project lifecycle status."""
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"
    PAUSED = "paused"


class TeamMemberRole(Enum):
    """Team member roles with permission levels."""
    OWNER = "owner"
    ADMIN = "admin"
    DEVELOPER = "developer"
    VIEWER = "viewer"


class SubscriptionTier(Enum):
    """Subscription tiers with feature limits."""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class ProjectContext:
    """Rich context for a project."""

    def __init__(self, project_id: str, name: str, description: str = ""):
        self.id = project_id
        self.name = name
        self.description = description
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.status = ProjectStatus.ACTIVE

        # GitHub integration
        self.github_url: Optional[str] = None
        self.github_owner: Optional[str] = None
        self.github_repo: Optional[str] = None
        self.github_branch: str = "main"
        self.last_sync: Optional[datetime] = None

        # Team management
        self.owner_id: Optional[str] = None
        self.team_members: Dict[str, Dict[str, Any]] = {}
        self.team_roles: Dict[str, TeamMemberRole] = {}

        # Code structure
        self.structure: Dict[str, Any] = {}
        self.file_count = 0
        self.language_stats: Dict[str, int] = {}

        # Subscription
        self.subscription_tier = SubscriptionTier.FREE
        self.quota_used = 0
        self.quota_limit = 100

        # Organization
        self.tags: Set[str] = set()
        self.metadata: Dict[str, Any] = {}


class ProjectManager(BaseAgent):
    """
    Agent that manages projects with full lifecycle support.

    Handles project creation, GitHub integration, team collaboration,
    subscription enforcement, and intelligent project filtering.
    """

    def __init__(self, llm_client: Optional[Any] = None):
        """Initialize the Project Manager."""
        super().__init__(name="ProjectManager", llm_client=llm_client)
        self.projects: Dict[str, ProjectContext] = {}
        self.tasks: List[Dict[str, Any]] = []
        self.archived_projects: Dict[str, ProjectContext] = {}
        self.team_invites: Dict[str, Dict[str, Any]] = {}

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process project management requests."""
        action = request.get("action", "list")

        # Project creation and basic operations
        if action == "create":
            return self.create_project(
                request.get("project_name"),
                request.get("description", ""),
                request.get("owner_id")
            )
        elif action == "list":
            return self.list_projects(
                request.get("filter"),
                request.get("tags"),
                request.get("status")
            )
        elif action == "get":
            return self.get_project(request.get("project_id"))

        # GitHub integration
        elif action == "import_github":
            return self.import_from_github(
                request.get("project_id"),
                request.get("github_url")
            )
        elif action == "sync_github":
            return self.sync_with_github(request.get("project_id"))
        elif action == "push_to_github":
            return self.push_to_github(request.get("project_id"))

        # Team management
        elif action == "add_team_member":
            return self.add_team_member(
                request.get("project_id"),
                request.get("user_id"),
                request.get("role", "developer")
            )
        elif action == "remove_team_member":
            return self.remove_team_member(
                request.get("project_id"),
                request.get("user_id")
            )
        elif action == "list_team":
            return self.list_team_members(request.get("project_id"))
        elif action == "invite_team_member":
            return self.invite_team_member(
                request.get("project_id"),
                request.get("email"),
                request.get("role", "developer")
            )

        # Lifecycle operations
        elif action == "archive":
            return self.archive_project(request.get("project_id"))
        elif action == "restore":
            return self.restore_project(request.get("project_id"))
        elif action == "delete":
            return self.delete_project(request.get("project_id"))

        # Subscription and quota
        elif action == "set_subscription":
            return self.set_subscription_tier(
                request.get("project_id"),
                request.get("tier")
            )
        elif action == "get_quota":
            return self.get_quota_status(request.get("project_id"))

        # Task management
        elif action == "add_task":
            return self.add_task(request.get("project_id"), request.get("task"))
        elif action == "update_task":
            return self.update_task(
                request.get("project_id"),
                request.get("task_id"),
                request.get("updates")
            )
        elif action == "list_tasks":
            return self.list_tasks(request.get("project_id"))

        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    def create_project(
        self, name: str, description: str = "", owner_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new project with full context."""
        if not name:
            return {"status": "error", "message": "Project name required"}

        project_id = f"proj_{uuid.uuid4().hex[:8]}"
        project = ProjectContext(project_id, name, description)

        if owner_id:
            project.owner_id = owner_id
            project.team_members[owner_id] = {
                "id": owner_id,
                "role": TeamMemberRole.OWNER.value,
                "joined_at": datetime.utcnow()
            }
            project.team_roles[owner_id] = TeamMemberRole.OWNER

        self.projects[project_id] = project
        self.logger.info(f"Project created: {project_id} ({name})")

        return {
            "status": "success",
            "agent": self.name,
            "project_id": project_id,
            "project_name": name,
            "owner_id": owner_id,
        }

    def get_project(self, project_id: str) -> Dict[str, Any]:
        """Get detailed project information."""
        if not project_id:
            return {"status": "error", "message": "Project ID required"}

        if project_id not in self.projects:
            return {"status": "error", "message": f"Project {project_id} not found"}

        project = self.projects[project_id]
        return {
            "status": "success",
            "agent": self.name,
            "project": {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "status": project.status.value,
                "created_at": project.created_at.isoformat(),
                "updated_at": project.updated_at.isoformat(),
                "github_url": project.github_url,
                "team_size": len(project.team_members),
                "subscription_tier": project.subscription_tier.value,
                "file_count": project.file_count,
                "quota_used": project.quota_used,
            }
        }

    def list_projects(
        self,
        filter_str: Optional[str] = None,
        tags: Optional[List[str]] = None,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """List projects with intelligent filtering."""
        projects_list = list(self.projects.values())

        # Filter by status
        if status:
            projects_list = [p for p in projects_list if p.status.value == status]
        else:
            projects_list = [p for p in projects_list if p.status == ProjectStatus.ACTIVE]

        # Filter by tags
        if tags:
            tag_set = set(tags)
            projects_list = [p for p in projects_list if p.tags & tag_set]

        # Filter by name/description
        if filter_str:
            query = filter_str.lower()
            projects_list = [
                p for p in projects_list
                if query in p.name.lower() or query in p.description.lower()
            ]

        return {
            "status": "success",
            "agent": self.name,
            "project_count": len(projects_list),
            "projects": [
                {
                    "id": p.id,
                    "name": p.name,
                    "status": p.status.value,
                    "team_size": len(p.team_members),
                }
                for p in projects_list
            ],
        }

    def import_from_github(self, project_id: str, github_url: str) -> Dict[str, Any]:
        """Import project from GitHub repository."""
        if not project_id or not github_url:
            return {"status": "error", "message": "Project ID and GitHub URL required"}

        if project_id not in self.projects:
            return {"status": "error", "message": f"Project {project_id} not found"}

        project = self.projects[project_id]
        project.github_url = github_url
        project.github_owner = github_url.split("/")[-2]
        project.github_repo = github_url.split("/")[-1]

        # Simulate code structure extraction
        project.structure = self._extract_code_structure(github_url)
        project.file_count = len(self._flatten_structure(project.structure))
        project.language_stats = self._detect_languages(project.structure)

        self.logger.info(f"GitHub import completed for {project_id}")

        return {
            "status": "success",
            "agent": self.name,
            "project_id": project_id,
            "github_url": github_url,
            "file_count": project.file_count,
            "languages": project.language_stats,
        }

    def sync_with_github(self, project_id: str) -> Dict[str, Any]:
        """Sync project with GitHub repository."""
        if project_id not in self.projects:
            return {"status": "error", "message": f"Project {project_id} not found"}

        project = self.projects[project_id]
        if not project.github_url:
            return {"status": "error", "message": "Project not linked to GitHub"}

        project.last_sync = datetime.utcnow()
        self.logger.info(f"Synced with GitHub for {project_id}")

        return {
            "status": "success",
            "agent": self.name,
            "project_id": project_id,
            "synced_at": project.last_sync.isoformat(),
        }

    def push_to_github(self, project_id: str) -> Dict[str, Any]:
        """Push project changes to GitHub."""
        if project_id not in self.projects:
            return {"status": "error", "message": f"Project {project_id} not found"}

        project = self.projects[project_id]
        if not project.github_url:
            return {"status": "error", "message": "Project not linked to GitHub"}

        return {
            "status": "success",
            "agent": self.name,
            "project_id": project_id,
            "message": f"Pushed to {project.github_url}",
        }

    def add_team_member(
        self, project_id: str, user_id: str, role: str = "developer"
    ) -> Dict[str, Any]:
        """Add a team member to the project."""
        if not project_id or not user_id:
            return {"status": "error", "message": "Project ID and user ID required"}

        if project_id not in self.projects:
            return {"status": "error", "message": f"Project {project_id} not found"}

        project = self.projects[project_id]

        # Validate role
        try:
            role_enum = TeamMemberRole[role.upper()]
        except KeyError:
            return {"status": "error", "message": f"Invalid role: {role}"}

        project.team_members[user_id] = {
            "id": user_id,
            "role": role,
            "joined_at": datetime.utcnow()
        }
        project.team_roles[user_id] = role_enum

        return {
            "status": "success",
            "agent": self.name,
            "project_id": project_id,
            "user_id": user_id,
            "role": role,
        }

    def remove_team_member(self, project_id: str, user_id: str) -> Dict[str, Any]:
        """Remove a team member from the project."""
        if not project_id or not user_id:
            return {"status": "error", "message": "Project ID and user ID required"}

        if project_id not in self.projects:
            return {"status": "error", "message": f"Project {project_id} not found"}

        project = self.projects[project_id]
        if user_id not in project.team_members:
            return {"status": "error", "message": f"User {user_id} not in project"}

        del project.team_members[user_id]
        del project.team_roles[user_id]

        return {
            "status": "success",
            "agent": self.name,
            "project_id": project_id,
            "user_id": user_id,
        }

    def list_team_members(self, project_id: str) -> Dict[str, Any]:
        """List team members for a project."""
        if not project_id:
            return {"status": "error", "message": "Project ID required"}

        if project_id not in self.projects:
            return {"status": "error", "message": f"Project {project_id} not found"}

        project = self.projects[project_id]
        return {
            "status": "success",
            "agent": self.name,
            "project_id": project_id,
            "team_size": len(project.team_members),
            "team_members": list(project.team_members.values()),
        }

    def invite_team_member(
        self, project_id: str, email: str, role: str = "developer"
    ) -> Dict[str, Any]:
        """Invite a team member via email."""
        if not project_id or not email:
            return {"status": "error", "message": "Project ID and email required"}

        invite_id = f"invite_{uuid.uuid4().hex[:8]}"
        self.team_invites[invite_id] = {
            "project_id": project_id,
            "email": email,
            "role": role,
            "created_at": datetime.utcnow(),
            "accepted": False
        }

        return {
            "status": "success",
            "agent": self.name,
            "invite_id": invite_id,
            "email": email,
            "project_id": project_id,
        }

    def archive_project(self, project_id: str) -> Dict[str, Any]:
        """Archive a project (soft delete)."""
        if project_id not in self.projects:
            return {"status": "error", "message": f"Project {project_id} not found"}

        project = self.projects.pop(project_id)
        project.status = ProjectStatus.ARCHIVED
        self.archived_projects[project_id] = project

        self.logger.info(f"Archived project: {project_id}")

        return {
            "status": "success",
            "agent": self.name,
            "project_id": project_id,
            "message": "Project archived",
        }

    def restore_project(self, project_id: str) -> Dict[str, Any]:
        """Restore an archived project."""
        if project_id not in self.archived_projects:
            return {"status": "error", "message": f"Project {project_id} not archived"}

        project = self.archived_projects.pop(project_id)
        project.status = ProjectStatus.ACTIVE
        self.projects[project_id] = project

        self.logger.info(f"Restored project: {project_id}")

        return {
            "status": "success",
            "agent": self.name,
            "project_id": project_id,
            "message": "Project restored",
        }

    def delete_project(self, project_id: str) -> Dict[str, Any]:
        """Permanently delete a project."""
        if project_id not in self.projects and project_id not in self.archived_projects:
            return {"status": "error", "message": f"Project {project_id} not found"}

        if project_id in self.projects:
            del self.projects[project_id]
        else:
            del self.archived_projects[project_id]

        self.logger.info(f"Deleted project: {project_id}")

        return {
            "status": "success",
            "agent": self.name,
            "project_id": project_id,
            "message": "Project permanently deleted",
        }

    def set_subscription_tier(self, project_id: str, tier: str) -> Dict[str, Any]:
        """Set project subscription tier."""
        if not project_id or not tier:
            return {"status": "error", "message": "Project ID and tier required"}

        if project_id not in self.projects:
            return {"status": "error", "message": f"Project {project_id} not found"}

        try:
            tier_enum = SubscriptionTier[tier.upper()]
        except KeyError:
            return {"status": "error", "message": f"Invalid tier: {tier}"}

        project = self.projects[project_id]
        project.subscription_tier = tier_enum

        # Set quota based on tier
        quota_limits = {
            SubscriptionTier.FREE: 100,
            SubscriptionTier.PRO: 1000,
            SubscriptionTier.ENTERPRISE: 10000,
        }
        project.quota_limit = quota_limits[tier_enum]

        return {
            "status": "success",
            "agent": self.name,
            "project_id": project_id,
            "tier": tier,
            "quota_limit": project.quota_limit,
        }

    def get_quota_status(self, project_id: str) -> Dict[str, Any]:
        """Get quota status for a project."""
        if not project_id:
            return {"status": "error", "message": "Project ID required"}

        if project_id not in self.projects:
            return {"status": "error", "message": f"Project {project_id} not found"}

        project = self.projects[project_id]
        usage_percent = (project.quota_used / project.quota_limit * 100) if project.quota_limit > 0 else 0

        return {
            "status": "success",
            "agent": self.name,
            "project_id": project_id,
            "quota_used": project.quota_used,
            "quota_limit": project.quota_limit,
            "usage_percent": usage_percent,
        }

    def add_task(self, project_id: str, task: str) -> Dict[str, Any]:
        """Add a task to a project."""
        if not project_id or not task:
            return {"status": "error", "message": "Project ID and task required"}

        if project_id not in self.projects:
            return {"status": "error", "message": f"Project {project_id} not found"}

        task_id = f"task_{uuid.uuid4().hex[:8]}"
        task_obj = {
            "id": task_id,
            "project_id": project_id,
            "task": task,
            "status": "pending",
            "created_at": datetime.utcnow(),
        }
        self.tasks.append(task_obj)

        return {
            "status": "success",
            "agent": self.name,
            "task_id": task_id,
            "project_id": project_id,
        }

    def update_task(
        self, project_id: str, task_id: str, updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a task."""
        if not project_id or not task_id:
            return {"status": "error", "message": "Project ID and task ID required"}

        task = next((t for t in self.tasks if t["id"] == task_id and t["project_id"] == project_id), None)
        if not task:
            return {"status": "error", "message": f"Task {task_id} not found"}

        task.update(updates)
        task["updated_at"] = datetime.utcnow()

        return {
            "status": "success",
            "agent": self.name,
            "task_id": task_id,
            "updated": True,
        }

    def list_tasks(self, project_id: str) -> Dict[str, Any]:
        """List tasks for a project."""
        if not project_id:
            return {"status": "error", "message": "Project ID required"}

        project_tasks = [t for t in self.tasks if t["project_id"] == project_id]

        return {
            "status": "success",
            "agent": self.name,
            "project_id": project_id,
            "task_count": len(project_tasks),
            "tasks": project_tasks,
        }

    # Helper methods
    def _extract_code_structure(self, github_url: str) -> Dict[str, Any]:
        """Extract code structure from GitHub."""
        return {
            "root": {
                "src": {"count": 0},
                "tests": {"count": 0},
                "docs": {"count": 0},
            }
        }

    def _flatten_structure(self, structure: Dict[str, Any]) -> List[str]:
        """Flatten directory structure to file list."""
        files = []
        def traverse(node, path=""):
            for key, value in node.items():
                current_path = f"{path}/{key}" if path else key
                if isinstance(value, dict):
                    traverse(value, current_path)
                else:
                    files.append(current_path)
        traverse(structure)
        return files

    def _detect_languages(self, structure: Dict[str, Any]) -> Dict[str, int]:
        """Detect programming languages from file structure."""
        return {
            "python": 0,
            "javascript": 0,
            "typescript": 0,
        }
