"""Project context model for Socratic Agents"""

import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional

from .role import TeamMemberRole


@dataclass
class ProjectContext:
    """Represents a project's complete context and metadata"""

    project_id: str
    name: str
    owner: str
    phase: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    collaborators: List[str] = None
    description: str = ""
    goals: str = ""
    requirements: List[str] = None
    tech_stack: List[str] = None
    constraints: List[str] = None
    team_structure: str = "individual"
    language_preferences: str = "python"
    deployment_target: str = "local"
    code_style: str = "standard"
    conversation_history: List[Dict] = None
    chat_mode: str = "socratic"
    is_archived: bool = False
    archived_at: Optional[datetime.datetime] = None
    progress: int = 0
    status: str = "active"
    project_type: str = "software"
    is_system_project: bool = False
    system_project_type: Optional[str] = None
    team_members: Optional[List[TeamMemberRole]] = None
    pending_questions: Optional[List[Dict]] = None
    notes: Optional[List[Dict]] = None
    code_history: Optional[List[Dict]] = None
    phase_maturity_scores: Dict[str, float] = None
    overall_maturity: float = 0.0
    category_scores: Dict[str, Dict[str, float]] = None
    categorized_specs: Dict[str, List[Dict]] = None
    maturity_history: List[Dict] = None
    analytics_metrics: Dict[str, any] = None
    workflow_definitions: Dict[str, any] = None
    workflow_approval_requests: Optional[List[Dict]] = None
    active_workflow_execution: Optional[Dict[str, any]] = None
    workflow_history: Optional[List[Dict]] = None
    metadata: Optional[Dict[str, any]] = None
    llm_configuration: Optional[Dict[str, any]] = None
    repository_url: Optional[str] = None
    repository_owner: Optional[str] = None
    repository_name: Optional[str] = None
    repository_description: Optional[str] = None
    repository_language: Optional[str] = None
    repository_imported_at: Optional[datetime.datetime] = None
    repository_file_count: int = 0
    repository_has_tests: bool = False
    last_export_time: Optional[datetime.datetime] = None
    last_export_format: Optional[str] = None
    export_count: int = 0
    is_published_to_github: bool = False
    github_repo_url: Optional[str] = None
    github_clone_url: Optional[str] = None
    github_published_date: Optional[datetime.datetime] = None
    github_repo_private: bool = True
    github_username: Optional[str] = None
    has_git_initialized: bool = False
    git_branch: Optional[str] = None
    git_remote_url: Optional[str] = None
    uncommitted_changes: bool = False

    def __post_init__(self):
        """Initialize default values"""
        self._initialize_list_fields()
        self._initialize_team_members()
        self._initialize_maturity_fields()
        self._initialize_workflow_fields()

    def _initialize_list_fields(self) -> None:
        if self.collaborators is None:
            self.collaborators = []
        if self.requirements is None:
            self.requirements = []
        if self.tech_stack is None:
            self.tech_stack = []
        if self.constraints is None:
            self.constraints = []
        if self.conversation_history is None:
            self.conversation_history = []
        if self.notes is None:
            self.notes = []
        if self.pending_questions is None:
            self.pending_questions = []

    def _initialize_team_members(self) -> None:
        if self.team_members is None:
            self.team_members = []
            if self.owner:
                owner_member = TeamMemberRole(
                    username=self.owner,
                    role="owner",
                    skills=[],
                    joined_at=self.created_at,
                )
                self.team_members.append(owner_member)

    def _initialize_maturity_fields(self) -> None:
        if self.phase_maturity_scores is None:
            self.phase_maturity_scores = {"discovery": 0.0, "analysis": 0.0, "design": 0.0, "implementation": 0.0}
        if self.category_scores is None:
            self.category_scores = {}
        if self.categorized_specs is None:
            self.categorized_specs = {}
        if self.maturity_history is None:
            self.maturity_history = []
        if self.analytics_metrics is None:
            self.analytics_metrics = {"velocity": 0.0, "total_qa_sessions": 0}
        self.overall_maturity = self._calculate_overall_maturity()

    def _calculate_overall_maturity(self) -> float:
        if not self.phase_maturity_scores:
            return 0.0
        scored_phases = [s for s in self.phase_maturity_scores.values() if s > 0]
        return sum(scored_phases) / len(scored_phases) if scored_phases else 0.0

    def _initialize_workflow_fields(self) -> None:
        if self.workflow_definitions is None:
            self.workflow_definitions = {}
        if self.workflow_approval_requests is None:
            self.workflow_approval_requests = []
        if self.workflow_history is None:
            self.workflow_history = []
        if self.metadata is None:
            self.metadata = {}
        if "use_workflow_optimization" not in self.metadata:
            self.metadata["use_workflow_optimization"] = False

    def get_member_role(self, username: str) -> Optional[str]:
        for member in self.team_members or []:
            if member.username == username:
                return member.role
        return None

    def is_solo_project(self) -> bool:
        return len(self.team_members or []) <= 1
