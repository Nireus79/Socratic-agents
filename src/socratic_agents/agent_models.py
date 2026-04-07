"""Type-safe request/response models for all agents using Pydantic.

This module defines request and response models for each agent action,
replacing Dict[str, Any] with properly typed Pydantic BaseModel classes.
This eliminates type checking errors and improves IDE support.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field


# ============================================================================
# BASE MODELS - Used by multiple agents
# ============================================================================


class ProjectContext(BaseModel):
    """Project context passed to agents."""

    project_id: str = Field(..., description="Unique project identifier")
    name: str = Field(..., description="Project name")
    phase: str = Field(default="discovery", description="Current project phase")
    status: str = Field(default="active", description="Project status")
    owner: Optional[str] = None
    description: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentResponse(BaseModel):
    """Base response model for all agents."""

    status: Literal["success", "error", "warning"] = Field(
        ..., description="Response status"
    )
    message: Optional[str] = Field(default=None, description="Status message")
    agent: Optional[str] = Field(default=None, description="Agent name")
    timestamp: Optional[datetime] = Field(
        default_factory=datetime.utcnow, description="Response timestamp"
    )


# ============================================================================
# SOCRATIC COUNSELOR AGENT MODELS
# ============================================================================


class SocraticCounselorGenerateQuestionRequest(BaseModel):
    """Request to generate a Socratic question."""

    action: Literal["generate_question"] = "generate_question"
    project: ProjectContext = Field(..., description="Project context")
    current_user: Optional[str] = Field(None, description="Current user ID")
    force_refresh: bool = Field(default=False, description="Force new question generation")


class SocraticCounselorGenerateQuestionResponse(AgentResponse):
    """Response with generated Socratic question."""

    question: Optional[str] = Field(None, description="Generated question")
    existing: bool = Field(default=False, description="Whether question was existing")


# ============================================================================
# CODE GENERATOR AGENT MODELS
# ============================================================================


class CodeGeneratorGenerateRequest(BaseModel):
    """Request to generate code."""

    action: Literal["generate"] = "generate"
    prompt: str = Field(..., description="Code generation prompt")
    language: str = Field(default="python", description="Programming language")
    project_id: Optional[str] = Field(None, description="Project ID")


class CodeGeneratorGenerateProjectRequest(BaseModel):
    """Request to generate a project."""

    action: Literal["generate_project"] = "generate_project"
    project: ProjectContext = Field(..., description="Project context")
    current_user: Optional[str] = Field(None, description="Current user ID")


class CodeGeneratorGenerateWithExplanationRequest(BaseModel):
    """Request to generate code with explanation."""

    action: Literal["generate_with_explanation"] = "generate_with_explanation"
    project: ProjectContext = Field(..., description="Project context")
    current_user: Optional[str] = Field(None, description="Current user ID")


class CodeGeneratorGetProjectRequest(BaseModel):
    """Request to get project details."""

    action: Literal["get_project"] = "get_project"
    project_id: str = Field(..., description="Project ID")


class CodeGeneratorListProjectsRequest(BaseModel):
    """Request to list projects."""

    action: Literal["list_projects"] = "list_projects"


class CodeGeneratorGenerateArtifactRequest(BaseModel):
    """Request to generate code artifact."""

    action: Literal["generate_artifact"] = "generate_artifact"
    project: ProjectContext = Field(..., description="Project context")
    current_user: Optional[str] = Field(None, description="Current user ID")


class CodeGeneratorGenerateDocumentationRequest(BaseModel):
    """Request to generate documentation."""

    action: Literal["generate_documentation"] = "generate_documentation"
    project: ProjectContext = Field(..., description="Project context")
    artifact: Optional[str] = Field(None, description="Code to document")
    script: Optional[str] = Field(None, description="Alias for artifact (legacy)")
    current_user: Optional[str] = Field(None, description="Current user ID")


class CodeGeneratorGenerateArtifactResponse(AgentResponse):
    """Response with generated artifact."""

    artifact: Optional[str] = Field(None, description="Generated code")
    script: Optional[str] = Field(None, description="Legacy compatibility")
    artifact_type: Optional[str] = Field(None, description="Type of artifact")
    context_used: Optional[str] = Field(None, description="Context passed to LLM")
    save_path: Optional[str] = Field(None, description="Path where saved")
    is_multi_file: bool = Field(default=False)


class CodeGeneratorGenerateDocumentationResponse(AgentResponse):
    """Response with generated documentation."""

    documentation: Optional[str] = Field(None, description="Generated docs")
    save_path: Optional[str] = Field(None, description="Path where saved")


# ============================================================================
# CODE VALIDATOR AGENT MODELS
# ============================================================================


class CodeValidatorValidateProjectRequest(BaseModel):
    """Request to validate project."""

    action: Literal["validate_project"] = "validate_project"
    project_path: str = Field(..., description="Path to project")
    timeout: int = Field(default=300, description="Timeout in seconds")


class CodeValidatorValidationResult(BaseModel):
    """Validation results."""

    overall_status: Literal["pass", "warning", "fail"] = Field(
        ..., description="Overall validation status"
    )
    issues_count: int = Field(default=0)
    warnings_count: int = Field(default=0)
    syntax_valid: bool = Field(default=True)
    dependencies_valid: bool = Field(default=True)
    tests_status: Optional[str] = None
    details: Optional[str] = None


class CodeValidatorValidateProjectResponse(AgentResponse):
    """Response with validation results."""

    validation_summary: Optional[CodeValidatorValidationResult] = None
    validation_results: Dict[str, Any] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)


# ============================================================================
# KNOWLEDGE MANAGER AGENT MODELS
# ============================================================================


class KnowledgeSuggestion(BaseModel):
    """Knowledge suggestion to add to project."""

    id: str = Field(..., description="Suggestion ID")
    content: str = Field(..., description="Knowledge content")
    category: str = Field(..., description="Knowledge category")
    topic: Optional[str] = None
    difficulty: str = Field(default="intermediate")
    reason: str = Field(default="insufficient_context")
    agent: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="pending")


class KnowledgeManagerGetSuggestionsRequest(BaseModel):
    """Request to get knowledge suggestions."""

    action: Literal["get_suggestions"] = "get_suggestions"
    project_id: str = Field(default="default")
    status: str = Field(default="pending")


class KnowledgeManagerGetSuggestionsResponse(AgentResponse):
    """Response with knowledge suggestions."""

    suggestions: List[KnowledgeSuggestion] = Field(default_factory=list)
    count: int = Field(default=0)


class KnowledgeManagerApproveSuggestionRequest(BaseModel):
    """Request to approve a suggestion."""

    action: Literal["approve_suggestion"] = "approve_suggestion"
    project_id: str = Field(default="default")
    suggestion_id: str = Field(..., description="ID of suggestion to approve")


class KnowledgeManagerQueueStatusResponse(AgentResponse):
    """Response with queue status."""

    pending: int = Field(default=0)
    approved: int = Field(default=0)
    rejected: int = Field(default=0)
    total: int = Field(default=0)


# ============================================================================
# LEARNING AGENT MODELS
# ============================================================================


class UserLearningAgentTrackQuestionRequest(BaseModel):
    """Request to track question effectiveness."""

    action: Literal["track_question_effectiveness"] = "track_question_effectiveness"
    user_id: str = Field(..., description="User ID")
    question_template_id: str = Field(..., description="Question template ID")
    role: str = Field(default="general")
    answer_length: Optional[int] = None
    specs_extracted: Optional[int] = None
    answer_quality: Optional[float] = None


class UserLearningAgentTrackQuestionResponse(AgentResponse):
    """Response with effectiveness tracking."""

    effectiveness_score: float = Field(default=0.0)
    times_asked: int = Field(default=0)
    times_answered_well: int = Field(default=0)


# ============================================================================
# PROJECT MANAGER AGENT MODELS
# ============================================================================


class ProjectManagerCreateProjectRequest(BaseModel):
    """Request to create a new project."""

    action: Literal["create_project"] = "create_project"
    project_name: str = Field(..., description="Name of project")
    owner: str = Field(..., description="Project owner")
    project_type: str = Field(default="software")
    description: Optional[str] = None
    knowledge_base_content: Optional[str] = None


class ProjectManagerCreateProjectResponse(AgentResponse):
    """Response with created project."""

    project: Optional[ProjectContext] = None


class ProjectManagerAddCollaboratorRequest(BaseModel):
    """Request to add collaborator."""

    action: Literal["add_collaborator"] = "add_collaborator"
    project: ProjectContext = Field(..., description="Project context")
    username: str = Field(..., description="Username to add")
    role: Literal["creator", "lead", "specialist", "analyst", "coordinator"] = Field(
        ..., description="Role for user"
    )


class ProjectManagerListProjectsResponse(AgentResponse):
    """Response with list of projects."""

    projects: List[Dict[str, Any]] = Field(default_factory=list)
    count: int = Field(default=0)


# ============================================================================
# USER MANAGER AGENT MODELS
# ============================================================================


class UserManagerArchiveUserRequest(BaseModel):
    """Request to archive a user."""

    action: Literal["archive_user"] = "archive_user"
    username: str = Field(..., description="Username to archive")
    requester: str = Field(..., description="User making request")
    archive_projects: bool = Field(default=True)


class UserManagerDeleteUserRequest(BaseModel):
    """Request to permanently delete a user."""

    action: Literal["delete_user_permanently"] = "delete_user_permanently"
    username: str = Field(..., description="Username to delete")
    requester: str = Field(..., description="User making request")
    confirmation: Literal["DELETE"] = Field(..., description="Confirmation string")


# ============================================================================
# QUALITY CONTROLLER AGENT MODELS
# ============================================================================


class QualityControllerCalculateMaturityRequest(BaseModel):
    """Request to calculate phase maturity."""

    action: Literal["calculate_maturity", "get_phase_maturity"] = "calculate_maturity"
    project: ProjectContext = Field(..., description="Project context")
    phase: Optional[str] = None
    current_user: Optional[str] = None


class QualityControllerMaturityResponse(AgentResponse):
    """Response with maturity calculation."""

    overall_maturity: float = Field(default=0.0, description="Overall maturity 0-100")
    phase_maturity: Dict[str, float] = Field(default_factory=dict)
    phase_maturity_scores: Dict[str, Any] = Field(default_factory=dict)
    category_scores: Dict[str, Any] = Field(default_factory=dict)
    is_phase_ready: bool = Field(default=False)
    advancement_recommended: bool = Field(default=False)


# ============================================================================
# CONFLICT DETECTOR AGENT MODELS
# ============================================================================


class ConflictDetectorDetectConflictsRequest(BaseModel):
    """Request to detect conflicts."""

    action: Literal["detect_conflicts"] = "detect_conflicts"
    project: ProjectContext = Field(..., description="Project context")
    new_insights: Dict[str, Any] = Field(..., description="New insights to check")
    current_user: Optional[str] = None


class Conflict(BaseModel):
    """Detected conflict."""

    conflict_id: str = Field(..., description="Conflict ID")
    type: str = Field(..., description="Conflict type")
    severity: str = Field(..., description="Conflict severity")
    description: str = Field(..., description="Conflict description")
    suggestions: List[str] = Field(default_factory=list)


class ConflictDetectorDetectConflictsResponse(AgentResponse):
    """Response with detected conflicts."""

    conflicts: List[Conflict] = Field(default_factory=list)


# ============================================================================
# QUESTION QUEUE AGENT MODELS
# ============================================================================


class QuestionQueueAgentAddQuestionRequest(BaseModel):
    """Request to add question to queue."""

    action: Literal["add_question"] = "add_question"
    project_id: Optional[str] = None
    question: str = Field(..., description="Question text")
    phase: str = Field(..., description="Project phase")
    project: Optional[ProjectContext] = None


class QuestionQueueAgentGetQuestionsRequest(BaseModel):
    """Request to get questions for user."""

    action: Literal["get_user_questions"] = "get_user_questions"
    project_id: Optional[str] = None
    username: str = Field(..., description="Username")
    project: Optional[ProjectContext] = None


class QuestionQueueAgentAddQuestionResponse(AgentResponse):
    """Response from adding question."""

    question_id: Optional[str] = None
    assigned_to: List[str] = Field(default_factory=list)


class QuestionQueueAgentGetQuestionsResponse(AgentResponse):
    """Response with user's questions."""

    user_questions: List[Dict[str, Any]] = Field(default_factory=list)


# ============================================================================
# CONTEXT ANALYZER AGENT MODELS
# ============================================================================


class ContextAnalyzerAnalyzeRequest(BaseModel):
    """Request to analyze context."""

    action: str = Field(..., description="Action to perform")
    content: Optional[str] = None
    domain: Optional[str] = None
    name: Optional[str] = None
    query: Optional[str] = None
    limit: int = Field(default=5)
    metadata: Optional[Dict[str, Any]] = None


class ContextAnalyzerAnalyzeResponse(AgentResponse):
    """Response from context analysis."""

    contexts: Optional[List[Dict[str, Any]]] = None
    entities: Optional[Dict[str, str]] = None
    relationships: Optional[List[Dict[str, Any]]] = None
    domain: Optional[str] = None
    analysis: Optional[Dict[str, Any]] = None


# ============================================================================
# GENERIC AGENT REQUEST/RESPONSE WRAPPER
# ============================================================================


class GenericAgentResponse(AgentResponse):
    """Generic response wrapper for agents with dynamic data."""

    data: Optional[Dict[str, Any]] = Field(None, description="Response data")

    class Config:
        extra = "allow"  # Allow additional fields


__all__ = [
    # Base models
    "ProjectContext",
    "AgentResponse",
    # Socratic Counselor
    "SocraticCounselorGenerateQuestionRequest",
    "SocraticCounselorGenerateQuestionResponse",
    # Code Generator
    "CodeGeneratorGenerateRequest",
    "CodeGeneratorGenerateProjectRequest",
    "CodeGeneratorGenerateWithExplanationRequest",
    "CodeGeneratorGetProjectRequest",
    "CodeGeneratorListProjectsRequest",
    "CodeGeneratorGenerateArtifactRequest",
    "CodeGeneratorGenerateDocumentationRequest",
    "CodeGeneratorGenerateArtifactResponse",
    "CodeGeneratorGenerateDocumentationResponse",
    # Code Validator
    "CodeValidatorValidateProjectRequest",
    "CodeValidatorValidationResult",
    "CodeValidatorValidateProjectResponse",
    # Knowledge Manager
    "KnowledgeSuggestion",
    "KnowledgeManagerGetSuggestionsRequest",
    "KnowledgeManagerGetSuggestionsResponse",
    "KnowledgeManagerApproveSuggestionRequest",
    "KnowledgeManagerQueueStatusResponse",
    # Learning Agent
    "UserLearningAgentTrackQuestionRequest",
    "UserLearningAgentTrackQuestionResponse",
    # Project Manager
    "ProjectManagerCreateProjectRequest",
    "ProjectManagerCreateProjectResponse",
    "ProjectManagerAddCollaboratorRequest",
    "ProjectManagerListProjectsResponse",
    # User Manager
    "UserManagerArchiveUserRequest",
    "UserManagerDeleteUserRequest",
    # Quality Controller
    "QualityControllerCalculateMaturityRequest",
    "QualityControllerMaturityResponse",
    # Conflict Detector
    "ConflictDetectorDetectConflictsRequest",
    "Conflict",
    "ConflictDetectorDetectConflictsResponse",
    # Question Queue
    "QuestionQueueAgentAddQuestionRequest",
    "QuestionQueueAgentGetQuestionsRequest",
    "QuestionQueueAgentAddQuestionResponse",
    "QuestionQueueAgentGetQuestionsResponse",
    # Context Analyzer
    "ContextAnalyzerAnalyzeRequest",
    "ContextAnalyzerAnalyzeResponse",
    # Generic
    "GenericAgentResponse",
]
