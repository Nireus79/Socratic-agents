"""Code Generator Agent - Intelligent code generation."""

from typing import Any, Dict, Optional
from .base import BaseAgent


class CodeGenerator(BaseAgent):
    """
    Agent that generates code based on descriptions and requirements.
    """

    def __init__(self, llm_client: Optional[Any] = None):
        """Initialize the Code Generator."""
        super().__init__(name="CodeGenerator", llm_client=llm_client)

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a code generation request."""
        prompt = request.get("prompt", "")
        language = request.get("language", "python")

        if not prompt:
            return {"status": "error", "message": "Prompt required"}

        # Use LLM to generate code if available
        code = self._generate_code(prompt, language)

        return {
            "status": "success",
            "agent": self.name,
            "language": language,
            "code": code,
            "prompt": prompt,
        }

    def generate(self, prompt: str, language: str = "python") -> str:
        """
        Generate code for a given prompt.

        Args:
            prompt: Description of the code to generate
            language: Programming language (default: python)

        Returns:
            Generated code
        """
        result = self.process({"prompt": prompt, "language": language})
        return result.get("code", "")

    def _generate_code(self, prompt: str, language: str) -> str:
        """Generate code using LLM if available, otherwise return stub."""
        if self.llm_client:
            # Use Socrates Nexus LLM to generate code
            llm_prompt = f"Generate {language} code for: {prompt}"
            try:
                response = self.llm_client.chat(llm_prompt)
                return response.content
            except Exception as e:
                self.logger.error(f"Code generation error: {e}")
                return f"# Error generating code: {e}"
        else:
            # Stub implementation
            return f"# Generated {language} code for: {prompt}\n# (LLM client not configured)"
