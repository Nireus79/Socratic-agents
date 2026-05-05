from __future__ import annotations

"""
Code generation agent for Socrates AI
"""

import asyncio
from typing import TYPE_CHECKING, Any, Dict, Optional

from .base import Agent
from .interfaces import DatabaseService, LLMService

if TYPE_CHECKING:
    from .agent_bus import AgentBus


class CodeGeneratorAgent(Agent):
    """Generates code and documentation based on project context"""

    def __init__(
        self,
        name: str = "CodeGenerator",
        llm_service: Optional[LLMService] = None,
        database_service: Optional[DatabaseService] = None,
        agent_bus: Optional["AgentBus"] = None,
    ):
        """Initialize CodeGeneratorAgent with injected dependencies."""
        super().__init__(name, agent_bus)
        self.llm_service = llm_service
        self.database_service = database_service

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process code generation requests (synchronous wrapper)"""
        action = request.get("action")

        if action == "generate_artifact":
            return self._generate_artifact(request)
        elif action == "generate_documentation":
            return self._generate_documentation(request)
        # Legacy support
        elif action == "generate_script":
            return self._generate_artifact(request)

        return {"status": "error", "message": "Unknown action"}

    async def process_async(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process code generation requests asynchronously"""
        action = request.get("action")

        if action == "generate_artifact":
            return await self._generate_artifact_async(request)
        elif action == "generate_documentation":
            return await self._generate_documentation_async(request)
        # Legacy support
        elif action == "generate_script":
            return await self._generate_artifact_async(request)

        return {"status": "error", "message": "Unknown action"}

    def _generate_artifact(self, request: Dict) -> Dict:
        """Generate project-type-appropriate artifact (sync wrapper)"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                return {
                    "status": "error",
                    "message": "Use process_async() instead of process() in async context",
                }
        except RuntimeError:
            pass

        return asyncio.run(self._generate_artifact_async(request))

    async def _generate_artifact_async(self, request: Dict) -> Dict:
        """Generate project-type-appropriate artifact"""
        if not self.llm_service:
            return {"status": "error", "message": "LLM service not configured"}

        project = request.get("project")

        if not project:
            return {"status": "error", "message": "Project is required"}

        # Build comprehensive context
        context = self._build_generation_context(project)

        # Generate artifact based on project type
        try:
            artifact = await self.llm_service.generate_artifact(context, project.project_type)
        except Exception as e:
            self.log(f"ERROR: Failed to generate artifact: {str(e)}")
            return {"status": "error", "message": f"Generation failed: {str(e)}"}

        # Determine artifact type
        artifact_type_map = {
            "software": "code",
            "business": "business_plan",
            "research": "research_protocol",
            "creative": "creative_brief",
            "marketing": "marketing_plan",
            "educational": "curriculum",
        }
        artifact_type = artifact_type_map.get(project.project_type, "code")

        self.log(f"Generated {artifact_type} for {project.project_type} project '{project.name}'")

        return {
            "status": "success",
            "artifact": artifact,
            "artifact_type": artifact_type,
            "script": artifact,  # Legacy compatibility
            "context_used": context,
        }

    def _generate_documentation(self, request: Dict) -> Dict:
        """Generate documentation for artifact (sync wrapper)"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                return {
                    "status": "error",
                    "message": "Use process_async() instead of process() in async context",
                }
        except RuntimeError:
            pass

        return asyncio.run(self._generate_documentation_async(request))

    async def _generate_documentation_async(self, request: Dict) -> Dict:
        """Generate documentation for project artifact"""
        if not self.llm_service:
            return {"status": "error", "message": "LLM service not configured"}

        project = request.get("project")
        artifact = request.get("artifact") or request.get("script")

        if not project:
            return {"status": "error", "message": "Project is required"}

        # Determine artifact type
        artifact_type_map = {
            "software": "code",
            "business": "business_plan",
            "research": "research_protocol",
            "creative": "creative_brief",
            "marketing": "marketing_plan",
            "educational": "curriculum",
        }
        artifact_type = artifact_type_map.get(project.project_type, "code")

        if not artifact:
            self.log(f"WARNING: Generating {artifact_type} documentation without artifact")

        try:
            documentation = await self.llm_service.generate_documentation(
                project, artifact, artifact_type
            )

            self.log(f"Generated documentation for {artifact_type}")

            return {
                "status": "success",
                "documentation": documentation,
            }
        except Exception as e:
            self.log(f"ERROR: Failed to generate documentation: {e}")
            return {
                "status": "error",
                "message": f"Documentation generation failed: {str(e)}",
            }

    def _build_generation_context(self, project: Any) -> str:
        """Build comprehensive context for code generation"""
        context_parts = [
            f"Project: {project.name}",
            f"Phase: {project.phase}",
        ]

        # Add optional fields with safe defaults
        if hasattr(project, "goals") and project.goals:
            context_parts.append(f"Goals: {project.goals}")

        if hasattr(project, "tech_stack") and project.tech_stack:
            context_parts.append(f"Tech Stack: {', '.join(project.tech_stack)}")

        if hasattr(project, "requirements") and project.requirements:
            context_parts.append(f"Requirements: {', '.join(project.requirements)}")

        if hasattr(project, "constraints") and project.constraints:
            context_parts.append(f"Constraints: {', '.join(project.constraints)}")

        if hasattr(project, "deployment_target") and project.deployment_target:
            context_parts.append(f"Target: {project.deployment_target}")

        if hasattr(project, "code_style") and project.code_style:
            context_parts.append(f"Style: {project.code_style}")

        return "\n".join(context_parts)
