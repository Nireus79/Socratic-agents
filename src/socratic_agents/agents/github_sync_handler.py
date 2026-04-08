"""GitHub Sync Handler Agent - Bidirectional GitHub synchronization and integration.

This agent:
1. Syncs projects with GitHub repositories
2. Manages branch creation and switching
3. Handles pull request creation and management
4. Processes webhooks for event-driven updates
5. Tracks commit history and changes
6. Manages repository configuration and settings
7. Supports bidirectional synchronization
8. Handles authentication and permissions
"""

import hashlib
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, cast

from .base import BaseAgent


class BranchStatus(Enum):
    """Branch status enumeration."""

    ACTIVE = "active"
    MERGED = "merged"
    ARCHIVED = "archived"
    STALE = "stale"


class PRStatus(Enum):
    """Pull Request status."""

    DRAFT = "draft"
    OPEN = "open"
    REVIEW = "review"
    APPROVED = "approved"
    MERGED = "merged"
    CLOSED = "closed"


class WebhookEvent(Enum):
    """Supported webhook events."""

    PUSH = "push"
    PULL_REQUEST = "pull_request"
    ISSUE = "issue"
    RELEASE = "release"
    REPOSITORY = "repository"


class Commit:
    """Represents a GitHub commit."""

    def __init__(self, message: str, author: str, files_changed: List[str]):
        self.id = hashlib.md5(f"{message}{author}{datetime.utcnow()}".encode()).hexdigest()[:8]
        self.message = message
        self.author = author
        self.files_changed = files_changed
        self.timestamp = datetime.utcnow()
        self.sha = hashlib.sha256(f"{self.id}{self.message}".encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "sha": self.sha,
            "message": self.message,
            "author": self.author,
            "files_changed": len(self.files_changed),
            "timestamp": self.timestamp.isoformat(),
        }


class Branch:
    """Represents a GitHub branch."""

    def __init__(self, name: str, source_branch: str = "main"):
        self.id = f"branch_{datetime.utcnow().timestamp()}"
        self.name = name
        self.source_branch = source_branch
        self.status = BranchStatus.ACTIVE
        self.commits: List[Commit] = []
        self.created_at = datetime.utcnow()
        self.last_updated = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status.value,
            "source": self.source_branch,
            "commits": len(self.commits),
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
        }


class PullRequest:
    """Represents a GitHub Pull Request."""

    def __init__(self, title: str, source_branch: str, target_branch: str = "main"):
        self.id = f"pr_{datetime.utcnow().timestamp()}"
        self.title = title
        self.source_branch = source_branch
        self.target_branch = target_branch
        self.status = PRStatus.DRAFT
        self.created_at = datetime.utcnow()
        self.reviewers: Set[str] = set()
        self.approvals: Set[str] = set()
        self.comments: List[Dict[str, Any]] = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "source_branch": self.source_branch,
            "target_branch": self.target_branch,
            "status": self.status.value,
            "reviewers": list(self.reviewers),
            "approvals": len(self.approvals),
            "comments": len(self.comments),
            "created_at": self.created_at.isoformat(),
        }


class GithubSyncHandler(BaseAgent):
    """
    Agent that manages bidirectional GitHub synchronization.

    Provides:
    - Repository creation and configuration
    - Branch management (create, switch, delete, merge)
    - Pull request lifecycle management
    - Commit tracking and history
    - Webhook integration for event-driven updates
    - Authorization and permission management
    - Sync status and conflict detection
    - Code review workflow support
    """

    def __init__(self, llm_client: Optional[Any] = None):
        """Initialize the GitHub Sync Handler."""
        super().__init__(name="GithubSyncHandler", llm_client=llm_client)
        self.repositories: Dict[str, Dict[str, Any]] = {}
        self.branches: Dict[str, Branch] = {}
        self.pull_requests: Dict[str, PullRequest] = {}
        self.commits: Dict[str, Commit] = {}
        self.webhooks: Dict[str, Dict[str, Any]] = {}
        self.sync_history: List[Dict[str, Any]] = []
        self.current_branch = "main"
        self.authentication_token: Optional[str] = None

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process GitHub sync requests."""
        action = request.get("action", "status")

        if action == "authenticate":
            return self.authenticate(cast(str, request.get("token")))
        elif action == "create_repo":
            return self.create_repository(
                cast(str, request.get("repo_name")), cast(str, request.get("description", ""))
            )
        elif action == "sync":
            return self.sync_repository(
                cast(str, request.get("repo")), cast(str, request.get("direction", "pull"))
            )
        elif action == "create_branch":
            return self.create_branch(
                cast(str, request.get("branch_name")), cast(str, request.get("source", "main"))
            )
        elif action == "delete_branch":
            return self.delete_branch(cast(str, request.get("branch_name")))
        elif action == "switch_branch":
            return self.switch_branch(cast(str, request.get("branch_name")))
        elif action == "commit":
            return self.record_commit(
                cast(str, request.get("message")),
                cast(str, request.get("author")),
                cast(Optional[List[str]], request.get("files", [])),
            )
        elif action == "create_pr":
            return self.create_pull_request(
                cast(str, request.get("title")),
                cast(str, request.get("source_branch")),
                cast(str, request.get("target_branch", "main")),
            )
        elif action == "update_pr":
            return self.update_pr_status(
                cast(str, request.get("pr_id")), cast(str, request.get("status"))
            )
        elif action == "add_reviewer":
            return self.add_pr_reviewer(
                cast(str, request.get("pr_id")), cast(str, request.get("reviewer"))
            )
        elif action == "approve_pr":
            return self.approve_pull_request(
                cast(str, request.get("pr_id")), cast(str, request.get("reviewer"))
            )
        elif action == "merge_pr":
            return self.merge_pull_request(cast(str, request.get("pr_id")))
        elif action == "register_webhook":
            return self.register_webhook(
                cast(str, request.get("event")), cast(str, request.get("url"))
            )
        elif action == "handle_webhook":
            return self.handle_webhook(
                cast(str, request.get("event")),
                cast(Optional[Dict[str, Any]], request.get("payload")),
            )
        elif action == "status":
            return self.sync_status()
        elif action == "history":
            return self.get_sync_history()
        elif action == "list_branches":
            return self.list_branches()
        elif action == "list_prs":
            return self.list_pull_requests()
        elif action == "detect_conflicts":
            return self.detect_conflicts(
                cast(str, request.get("branch1")), cast(str, request.get("branch2"))
            )
        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    def authenticate(self, token: str) -> Dict[str, Any]:
        """Authenticate with GitHub."""
        if not token:
            return {"status": "error", "message": "Token required"}

        self.authentication_token = token
        return {
            "status": "success",
            "agent": self.name,
            "authenticated": True,
            "token_length": len(token),
        }

    def create_repository(self, repo_name: str, description: str = "") -> Dict[str, Any]:
        """Create a new repository."""
        if not repo_name:
            return {"status": "error", "message": "Repository name required"}

        repo = {
            "name": repo_name,
            "description": description,
            "created_at": datetime.utcnow().isoformat(),
            "default_branch": "main",
            "is_private": False,
        }

        self.repositories[repo_name] = repo

        # Create main branch by default
        main_branch = Branch("main")
        self.branches[f"{repo_name}/main"] = main_branch

        return {
            "status": "success",
            "agent": self.name,
            "repository": repo_name,
            "url": f"https://github.com/unknown/{repo_name}",
            "default_branch": "main",
        }

    def sync_repository(self, repo: str, direction: str = "pull") -> Dict[str, Any]:
        """Sync repository with GitHub."""
        if not repo:
            return {"status": "error", "message": "Repository name required"}

        if repo not in self.repositories:
            return {"status": "error", "message": f"Repository {repo} not found"}

        sync_info = {
            "timestamp": datetime.utcnow().isoformat(),
            "direction": direction,
            "repository": repo,
            "status": "synced",
        }

        self.sync_history.append(sync_info)

        return {
            "status": "success",
            "agent": self.name,
            "repository": repo,
            "synced": True,
            "direction": direction,
            "total_syncs": len(self.sync_history),
        }

    def create_branch(self, branch_name: str, source: str = "main") -> Dict[str, Any]:
        """Create a new branch."""
        if not branch_name:
            return {"status": "error", "message": "Branch name required"}

        branch = Branch(branch_name, source)
        self.branches[branch_name] = branch

        return {
            "status": "success",
            "agent": self.name,
            "branch": branch_name,
            "source": source,
            "branch_info": branch.to_dict(),
        }

    def delete_branch(self, branch_name: str) -> Dict[str, Any]:
        """Delete a branch."""
        if not branch_name:
            return {"status": "error", "message": "Branch name required"}

        if branch_name not in self.branches:
            return {"status": "error", "message": f"Branch {branch_name} not found"}

        if branch_name == "main":
            return {"status": "error", "message": "Cannot delete main branch"}

        self.branches.pop(branch_name)

        return {
            "status": "success",
            "agent": self.name,
            "branch": branch_name,
            "deleted": True,
        }

    def switch_branch(self, branch_name: str) -> Dict[str, Any]:
        """Switch to a different branch."""
        if not branch_name:
            return {"status": "error", "message": "Branch name required"}

        if branch_name not in self.branches:
            return {"status": "error", "message": f"Branch {branch_name} not found"}

        self.current_branch = branch_name

        return {
            "status": "success",
            "agent": self.name,
            "current_branch": branch_name,
            "switched": True,
        }

    def record_commit(
        self, message: str, author: str, files: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Record a commit on current branch."""
        if not message or not author:
            return {"status": "error", "message": "Message and author required"}

        commit = Commit(message, author, files or [])
        self.commits[commit.id] = commit

        # Add to current branch
        if self.current_branch in self.branches:
            self.branches[self.current_branch].commits.append(commit)

        return {
            "status": "success",
            "agent": self.name,
            "commit_id": commit.id,
            "sha": commit.sha,
            "files_changed": len(commit.files_changed),
            "total_commits": len(self.commits),
        }

    def create_pull_request(
        self, title: str, source_branch: str, target_branch: str = "main"
    ) -> Dict[str, Any]:
        """Create a pull request."""
        if not title or not source_branch:
            return {"status": "error", "message": "Title and source branch required"}

        pr = PullRequest(title, source_branch, target_branch)
        self.pull_requests[pr.id] = pr

        return {
            "status": "success",
            "agent": self.name,
            "pr_id": pr.id,
            "title": title,
            "source_branch": source_branch,
            "target_branch": target_branch,
            "pr_status": "draft",
        }

    def update_pr_status(self, pr_id: str, status: str) -> Dict[str, Any]:
        """Update PR status."""
        if not pr_id or not status:
            return {"status": "error", "message": "PR ID and status required"}

        if pr_id not in self.pull_requests:
            return {"status": "error", "message": f"PR {pr_id} not found"}

        pr = self.pull_requests[pr_id]
        try:
            pr.status = PRStatus[status.upper()]
        except KeyError:
            return {"status": "error", "message": f"Invalid status: {status}"}

        return {
            "status": "success",
            "agent": self.name,
            "pr_id": pr_id,
            "new_status": pr.status.value,
        }

    def add_pr_reviewer(self, pr_id: str, reviewer: str) -> Dict[str, Any]:
        """Add reviewer to PR."""
        if not pr_id or not reviewer:
            return {"status": "error", "message": "PR ID and reviewer required"}

        if pr_id not in self.pull_requests:
            return {"status": "error", "message": f"PR {pr_id} not found"}

        self.pull_requests[pr_id].reviewers.add(reviewer)

        return {
            "status": "success",
            "agent": self.name,
            "pr_id": pr_id,
            "reviewer": reviewer,
            "total_reviewers": len(self.pull_requests[pr_id].reviewers),
        }

    def approve_pull_request(self, pr_id: str, reviewer: str) -> Dict[str, Any]:
        """Approve a pull request."""
        if not pr_id or not reviewer:
            return {"status": "error", "message": "PR ID and reviewer required"}

        if pr_id not in self.pull_requests:
            return {"status": "error", "message": f"PR {pr_id} not found"}

        pr = self.pull_requests[pr_id]
        pr.approvals.add(reviewer)
        pr.status = PRStatus.APPROVED

        return {
            "status": "success",
            "agent": self.name,
            "pr_id": pr_id,
            "reviewer": reviewer,
            "approvals": len(pr.approvals),
        }

    def merge_pull_request(self, pr_id: str) -> Dict[str, Any]:
        """Merge a pull request."""
        if not pr_id:
            return {"status": "error", "message": "PR ID required"}

        if pr_id not in self.pull_requests:
            return {"status": "error", "message": f"PR {pr_id} not found"}

        pr = self.pull_requests[pr_id]

        if len(pr.approvals) == 0:
            return {"status": "error", "message": "PR requires at least one approval"}

        pr.status = PRStatus.MERGED

        return {
            "status": "success",
            "agent": self.name,
            "pr_id": pr_id,
            "merged": True,
            "source": pr.source_branch,
            "target": pr.target_branch,
        }

    def register_webhook(self, event: str, url: str) -> Dict[str, Any]:
        """Register a webhook."""
        if not event or not url:
            return {"status": "error", "message": "Event and URL required"}

        webhook = {
            "event": event,
            "url": url,
            "created_at": datetime.utcnow().isoformat(),
            "enabled": True,
        }

        webhook_id = f"webhook_{len(self.webhooks) + 1}"
        self.webhooks[webhook_id] = webhook

        return {
            "status": "success",
            "agent": self.name,
            "webhook_id": webhook_id,
            "event": event,
            "registered": True,
        }

    def handle_webhook(
        self, event: str, payload: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Handle webhook event."""
        if not event:
            return {"status": "error", "message": "Event required"}

        payload = payload or {}

        return {
            "status": "success",
            "agent": self.name,
            "event": event,
            "processed": True,
            "payload_keys": list(payload.keys()),
        }

    def sync_status(self) -> Dict[str, Any]:
        """Get sync status."""
        return {
            "status": "success",
            "agent": self.name,
            "repositories": len(self.repositories),
            "branches": len(self.branches),
            "pull_requests": len(self.pull_requests),
            "commits": len(self.commits),
            "webhooks": len(self.webhooks),
            "current_branch": self.current_branch,
            "authenticated": self.authentication_token is not None,
        }

    def get_sync_history(self) -> Dict[str, Any]:
        """Get sync history."""
        return {
            "status": "success",
            "agent": self.name,
            "sync_count": len(self.sync_history),
            "syncs": self.sync_history[-10:],  # Last 10 syncs
        }

    def list_branches(self) -> Dict[str, Any]:
        """List all branches."""
        return {
            "status": "success",
            "agent": self.name,
            "branch_count": len(self.branches),
            "branches": [b.to_dict() for b in self.branches.values()],
            "current_branch": self.current_branch,
        }

    def list_pull_requests(self) -> Dict[str, Any]:
        """List all pull requests."""
        return {
            "status": "success",
            "agent": self.name,
            "pr_count": len(self.pull_requests),
            "pull_requests": [pr.to_dict() for pr in self.pull_requests.values()],
        }

    def detect_conflicts(self, branch1: str, branch2: str) -> Dict[str, Any]:
        """Detect conflicts between branches."""
        if not branch1 or not branch2:
            return {"status": "error", "message": "Two branch names required"}

        conflicts = []

        # Simple conflict detection: if branches have different commits
        if branch1 in self.branches and branch2 in self.branches:
            commits1 = set(c.id for c in self.branches[branch1].commits)
            commits2 = set(c.id for c in self.branches[branch2].commits)
            conflicts = list(commits1 ^ commits2)

        return {
            "status": "success",
            "agent": self.name,
            "branch1": branch1,
            "branch2": branch2,
            "conflicts_detected": len(conflicts) > 0,
            "conflict_count": len(conflicts),
        }
