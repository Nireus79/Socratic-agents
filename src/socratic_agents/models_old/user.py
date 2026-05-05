"""User model for Socratic Agents"""

import datetime
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class User:
    """Represents a user of Socratic Agents"""

    username: str
    email: str
    passcode_hash: str
    created_at: datetime.datetime
    projects: Optional[List[str]] = None
    is_archived: bool = False
    archived_at: Optional[datetime.datetime] = None
    subscription_tier: str = "free"
    subscription_status: str = "active"
    subscription_start: Optional[datetime.datetime] = None
    subscription_end: Optional[datetime.datetime] = None
    questions_used_this_month: int = 0
    usage_reset_date: Optional[datetime.datetime] = None
    testing_mode: bool = False
    claude_auth_method: str = "api_key"
    github_token: Optional[str] = None
    github_username: Optional[str] = None
    github_token_expires: Optional[datetime.datetime] = None
    has_github_auth: bool = False
    default_export_format: str = "zip"
    auto_initialize_git: bool = True
    default_repo_visibility: str = "private"

    def __post_init__(self):
        """Initialize projects list and subscription fields"""
        if self.projects is None:
            self.projects = []
        if self.subscription_start is None:
            self.subscription_start = datetime.datetime.now()
        if self.usage_reset_date is None:
            now = datetime.datetime.now()
            if now.month == 12:
                self.usage_reset_date = datetime.datetime(now.year + 1, 1, 1)
            else:
                self.usage_reset_date = datetime.datetime(now.year, now.month + 1, 1)
