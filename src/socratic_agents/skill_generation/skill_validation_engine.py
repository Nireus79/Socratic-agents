"""Validation engine for generated skills."""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class ValidationResult:
    """Result of skill validation."""

    is_valid: bool
    skill_id: str
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    safety_checks_passed: bool = True
    convention_compliant: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "is_valid": self.is_valid,
            "skill_id": self.skill_id,
            "errors": self.errors,
            "warnings": self.warnings,
            "safety_checks_passed": self.safety_checks_passed,
            "convention_compliant": self.convention_compliant,
        }


class SkillValidationEngine:
    """Validates generated skills before use."""

    def __init__(self):
        """Initialize the Skill Validation Engine."""
        self.logger = logging.getLogger(f"socratic_agents.{self.__class__.__name__}")
        self.max_skill_id_length = 50
        self.max_description_length = 500
        self.max_config_depth = 5

        # Harmful words/patterns to detect
        self.harmful_patterns = [
            "delete",
            "drop",
            "shutdown",
            "disable",
            "harmful",
            "malicious",
            "exploit",
            "break",
        ]

    def validate_skill(self, skill: Any) -> ValidationResult:
        """Validate a single skill."""
        result = ValidationResult(is_valid=True, skill_id=getattr(skill, "id", "unknown"))

        # Check structure
        if not self._check_structure(skill, result):
            result.is_valid = False

        # Check safety
        if not self._check_safety(skill, result):
            result.is_valid = False
            result.safety_checks_passed = False

        # Check conventions
        if not self._check_convention(skill, result):
            result.convention_compliant = False

        return result

    def validate_batch(self, skills: List[Any]) -> Dict[str, ValidationResult]:
        """Validate multiple skills."""
        results: Dict[str, ValidationResult] = {}
        for skill in skills:
            skill_id = getattr(skill, "id", f"skill_{len(results)}")
            results[skill_id] = self.validate_skill(skill)
        return results

    def _check_structure(self, skill: Any, result: ValidationResult) -> bool:
        """Check structural integrity."""
        errors = []

        # Check required fields
        if not hasattr(skill, "id") or not skill.id:
            errors.append("Missing required field: id")

        if not hasattr(skill, "target_agent") or not skill.target_agent:
            errors.append("Missing required field: target_agent")

        if not hasattr(skill, "skill_type") or not skill.skill_type:
            errors.append("Missing required field: skill_type")

        if not hasattr(skill, "config") or not isinstance(skill.config, dict):
            errors.append("Missing or invalid field: config must be a dict")

        if not hasattr(skill, "maturity_phase") or not skill.maturity_phase:
            errors.append("Missing required field: maturity_phase")

        if errors:
            result.errors.extend(errors)
            return False

        # Check field types
        if not isinstance(skill.id, str):
            result.errors.append("Field 'id' must be string")
            return False

        if not isinstance(skill.target_agent, str):
            result.errors.append("Field 'target_agent' must be string")
            return False

        return True

    def _check_safety(self, skill: Any, result: ValidationResult) -> bool:
        """Check for harmful patterns."""
        safe = True

        # Check skill ID for harmful patterns
        if self._contains_harmful_pattern(str(skill.id)):
            result.errors.append("Skill ID contains harmful pattern")
            safe = False

        # Check config for harmful patterns
        config_str = str(skill.config)
        if self._contains_harmful_pattern(config_str):
            result.errors.append("Skill config contains harmful pattern")
            safe = False

        # Check for suspicious values
        if isinstance(skill.confidence, (int, float)):
            if not (0.0 <= skill.confidence <= 1.0):
                result.errors.append("Confidence must be between 0.0 and 1.0")
                safe = False

        return safe

    def _check_convention(self, skill: Any, result: ValidationResult) -> bool:
        """Check naming and format conventions."""
        compliant = True

        # Check skill ID naming convention (snake_case)
        if not self._is_valid_identifier(skill.id):
            result.warnings.append(f"Skill ID '{skill.id}' should use snake_case")
            compliant = False

        # Check length limits
        if len(skill.id) > self.max_skill_id_length:
            result.warnings.append(f"Skill ID exceeds max length of {self.max_skill_id_length}")
            compliant = False

        # Check maturity phase value
        valid_phases = ["discovery", "definition", "execution", "optimization"]
        if skill.maturity_phase not in valid_phases:
            result.warnings.append(f"Maturity phase '{skill.maturity_phase}' not in {valid_phases}")
            compliant = False

        # Check skill type value
        valid_types = [
            "behavior_parameter",
            "method",
            "workflow",
            "configuration",
        ]
        if skill.skill_type not in valid_types:
            result.warnings.append(f"Skill type '{skill.skill_type}' not in {valid_types}")
            compliant = False

        return compliant

    def _contains_harmful_pattern(self, text: str) -> bool:
        """Check if text contains harmful patterns."""
        text_lower = text.lower()
        for pattern in self.harmful_patterns:
            if pattern in text_lower:
                return True
        return False

    @staticmethod
    def _is_valid_identifier(identifier: str) -> bool:
        """Check if identifier follows naming convention."""
        if not identifier:
            return False

        # Allow alphanumeric and underscores
        if not all(c.isalnum() or c == "_" for c in identifier):
            return False

        # Should not start with number
        if identifier[0].isdigit():
            return False

        return True
