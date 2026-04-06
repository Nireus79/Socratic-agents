"""Code Generator Agent - Intelligent code generation with real implementation."""

import logging
from typing import Any, Dict, Optional

from .base import BaseAgent

logger = logging.getLogger(__name__)


class CodeGenerator(BaseAgent):
    """
    Agent that generates code based on descriptions and requirements.

    Provides:
    - LLM-powered code generation
    - Multi-language support
    - Code validation and formatting
    - Integration with knowledge base for artifact storage
    """

    def __init__(self, llm_client: Optional[Any] = None, knowledge_store: Optional[Any] = None):
        """
        Initialize the Code Generator.

        Args:
            llm_client: Optional LLM client for code generation
            knowledge_store: Optional knowledge store for artifact persistence
        """
        super().__init__(name="CodeGenerator", llm_client=llm_client)
        self.knowledge_store = knowledge_store
        self.logger = logging.getLogger(f"{__name__}.CodeGenerator")

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a code generation request."""
        action = request.get("action", "generate")

        if action == "generate":
            return self._handle_generate(request)
        elif action == "generate_with_explanation":
            return self._handle_generate_with_explanation(request)
        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    def _handle_generate(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle basic code generation."""
        prompt = request.get("prompt", "")
        language = request.get("language", "python")
        project_id = request.get("project_id")

        if not prompt:
            return {"status": "error", "message": "Prompt required"}

        # Generate code
        code = self._generate_code_implementation(prompt, language)

        if not code:
            return {
                "status": "error",
                "message": "Failed to generate code",
            }

        # Store in knowledge base if project_id provided
        artifact_id = None
        if project_id and self.knowledge_store:
            try:
                artifact_id = self.knowledge_store.store_artifact(
                    project_id=project_id,
                    artifact_type="code",
                    language=language,
                    content=code,
                    metadata={"prompt": prompt},
                )
                self.logger.info(f"Stored generated code artifact: {artifact_id}")
            except Exception as e:
                self.logger.warning(f"Failed to store artifact: {e}")

        return {
            "status": "success",
            "agent": self.name,
            "language": language,
            "code": code,
            "prompt": prompt,
            "artifact_id": artifact_id,
            "lines_of_code": len(code.split("\n")),
        }

    def _handle_generate_with_explanation(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle code generation with explanation."""
        prompt = request.get("prompt", "")
        language = request.get("language", "python")

        if not prompt:
            return {"status": "error", "message": "Prompt required"}

        # Generate code
        code = self._generate_code_implementation(prompt, language)

        # Generate explanation
        explanation = self._generate_explanation(prompt, code, language)

        return {
            "status": "success",
            "agent": self.name,
            "language": language,
            "code": code,
            "explanation": explanation,
            "prompt": prompt,
        }

    def generate(self, prompt: str, language: str = "python") -> str:
        """
        Generate code for a given prompt (convenience method).

        Args:
            prompt: Description of the code to generate
            language: Programming language (default: python)

        Returns:
            Generated code
        """
        result = self.process({"prompt": prompt, "language": language})
        code = result.get("code", "")
        return str(code) if code else ""

    def _generate_code_implementation(self, prompt: str, language: str) -> str:
        """
        Generate code using LLM or return fallback.

        Args:
            prompt: Code generation prompt
            language: Programming language

        Returns:
            Generated code
        """
        if self.llm_client:
            # Use LLM for code generation
            llm_prompt = self._build_code_prompt(prompt, language)
            try:
                response = self.llm_client.chat(llm_prompt)
                code = str(response.content) if response.content else ""

                # Clean up response if it includes markdown code blocks
                code = self._extract_code_from_response(code, language)
                return code

            except Exception as e:
                self.logger.error(f"Code generation error: {e}")
                return ""
        else:
            # Fallback: generate simple template code
            return self._generate_template_code(prompt, language)

    def _generate_explanation(self, prompt: str, code: str, language: str) -> str:
        """Generate explanation for generated code."""
        if self.llm_client:
            llm_prompt = (
                f"Explain this {language} code in 2-3 sentences:\n\n{code}\n\n"
                f"Context: {prompt}"
            )
            try:
                response = self.llm_client.chat(llm_prompt)
                return str(response.content) if response.content else ""
            except Exception as e:
                self.logger.warning(f"Failed to generate explanation: {e}")
                return ""
        return ""

    def _build_code_prompt(self, prompt: str, language: str) -> str:
        """Build a structured prompt for code generation."""
        return (
            f"Generate production-quality {language} code for the following requirement:\n\n"
            f"{prompt}\n\n"
            f"Requirements:\n"
            f"- Include error handling\n"
            f"- Add docstrings/comments\n"
            f"- Follow {language} best practices\n"
            f"- Be concise but complete\n"
        )

    def _extract_code_from_response(self, response: str, language: str) -> str:
        """Extract code from response that may include markdown formatting."""
        # Remove markdown code blocks if present
        if f"```{language}" in response:
            # Extract content between code blocks
            start = response.find(f"```{language}") + len(f"```{language}")
            end = response.find("```", start)
            if end > start:
                return response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            if end > start:
                return response[start:end].strip()

        return response.strip()

    def _generate_template_code(self, prompt: str, language: str) -> str:
        """Generate simple template code when LLM is not available."""
        templates = {
            "python": self._get_python_template,
            "javascript": self._get_javascript_template,
            "typescript": self._get_typescript_template,
            "java": self._get_java_template,
        }

        template_func = templates.get(language.lower(), self._get_generic_template)
        return template_func(prompt)

    def _get_python_template(self, prompt: str) -> str:
        """Get Python code template."""
        return f'''"""
{prompt}
"""

def main():
    """Main function."""
    print("Implement: {prompt}")
    pass

if __name__ == "__main__":
    main()
'''

    def _get_javascript_template(self, prompt: str) -> str:
        """Get JavaScript code template."""
        return f'''/**
 * {prompt}
 */

function main() {{
    console.log("Implement: {prompt}");
}}

main();
'''

    def _get_typescript_template(self, prompt: str) -> str:
        """Get TypeScript code template."""
        return f'''/**
 * {prompt}
 */

function main(): void {{
    console.log("Implement: {prompt}");
}}

main();
'''

    def _get_java_template(self, prompt: str) -> str:
        """Get Java code template."""
        return f'''/**
 * {prompt}
 */
public class Main {{
    public static void main(String[] args) {{
        System.out.println("Implement: {prompt}");
    }}
}}
'''

    def _get_generic_template(self, prompt: str) -> str:
        """Get generic code template."""
        return f'''# {prompt}
# TODO: Implement {prompt}
'''
