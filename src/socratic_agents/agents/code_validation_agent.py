"""Code Validator Agent - Validates and tests code."""

from typing import Any, Dict, Optional, List
from .base import BaseAgent


class CodeValidator(BaseAgent):
    """
    Agent that validates and tests code for correctness.
    """

    def __init__(self, llm_client: Optional[Any] = None):
        """Initialize the Code Validator."""
        super().__init__(name="CodeValidator", llm_client=llm_client)

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a code validation request."""
        code = request.get("code", "")
        language = request.get("language", "python")

        if not code:
            return {"status": "error", "message": "Code required"}

        # Validate the code
        issues = self._validate_code(code, language)
        valid = len(issues) == 0

        return {
            "status": "success",
            "agent": self.name,
            "valid": valid,
            "issues": issues,
            "issue_count": len(issues),
        }

    def validate(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Validate code for issues.

        Args:
            code: Code to validate
            language: Programming language

        Returns:
            Validation results with issues found
        """
        return self.process({"code": code, "language": language})

    def _validate_code(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Validate code and return list of issues."""
        issues = []

        # Basic validation
        if not code.strip():
            issues.append({"severity": "error", "line": 0, "message": "Code is empty"})
            return issues

        # Use LLM for deeper analysis if available
        if self.llm_client:
            try:
                prompt = f"Analyze this {language} code for errors and issues:\n{code}"
                response = self.llm_client.chat(prompt)
                # Parse LLM response for issues (simplified)
                if "error" in response.content.lower() or "issue" in response.content.lower():
                    issues.append({"severity": "info", "message": response.content})
            except Exception as e:
                self.logger.warning(f"LLM analysis failed: {e}")

        return issues
