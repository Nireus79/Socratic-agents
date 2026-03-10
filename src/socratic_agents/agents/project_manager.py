"""Project Manager Agent - Project planning and management."""

from typing import Any, Dict, Optional, List
from .base import BaseAgent


class ProjectManager(BaseAgent):
    """Agent that manages projects, tasks, and timelines."""

    def __init__(self, llm_client: Optional[Any] = None):
        """Initialize the Project Manager."""
        super().__init__(name="ProjectManager", llm_client=llm_client)
        self.projects: Dict[str, Any] = {}
        self.tasks: List[Dict[str, Any]] = []

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process project management requests."""
        action = request.get("action", "list")
        if action == "create":
            return self.create_project(request.get("project_name"), request.get("description"))
        elif action == "add_task":
            return self.add_task(request.get("project_id"), request.get("task"))
        elif action == "list":
            return self.list_projects()
        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    def create_project(self, name: str, description: str = "") -> Dict[str, Any]:
        """Create a new project."""
        if not name:
            return {"status": "error", "message": "Project name required"}
        project_id = f"proj_{len(self.projects) + 1}"
        self.projects[project_id] = {"name": name, "description": description, "tasks": []}
        return {"status": "success", "agent": self.name, "project_id": project_id, "project_name": name}

    def add_task(self, project_id: str, task: str) -> Dict[str, Any]:
        """Add a task to a project."""
        if not project_id or not task:
            return {"status": "error", "message": "Project ID and task required"}
        if project_id not in self.projects:
            return {"status": "error", "message": f"Project {project_id} not found"}
        task_obj = {"id": len(self.tasks) + 1, "task": task, "status": "pending"}
        self.tasks.append(task_obj)
        self.projects[project_id]["tasks"].append(task_obj["id"])
        return {"status": "success", "agent": self.name, "task_id": task_obj["id"], "project_id": project_id}

    def list_projects(self) -> Dict[str, Any]:
        """List all projects."""
        return {"status": "success", "agent": self.name, "projects": list(self.projects.keys()), "project_count": len(self.projects), "task_count": len(self.tasks)}
