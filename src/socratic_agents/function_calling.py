"""Function calling support for LLM agents."""

import inspect
import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Type, get_type_hints

logger = logging.getLogger(__name__)


class ParameterType(str, Enum):
    """Supported parameter types for function schemas."""

    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"


@dataclass
class ParameterSchema:
    """Schema for a function parameter."""

    name: str
    type: ParameterType
    description: str
    required: bool = True
    enum_values: Optional[List[Any]] = None
    default_value: Optional[Any] = None
    items_type: Optional[ParameterType] = None  # For arrays

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        schema = {
            "name": self.name,
            "type": self.type.value,
            "description": self.description,
            "required": self.required,
        }

        if self.enum_values:
            schema["enum"] = self.enum_values

        if self.default_value is not None:
            schema["default"] = self.default_value

        if self.items_type:
            schema["items_type"] = self.items_type.value

        return schema


@dataclass
class FunctionSchema:
    """Schema definition for a function that can be called by LLMs."""

    name: str
    description: str
    callable_fn: Callable
    parameters: List[ParameterSchema] = field(default_factory=list)
    return_type: str = "any"
    return_description: str = ""
    tags: List[str] = field(default_factory=list)
    version: str = "1.0"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to OpenAI function calling format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        p.name: {
                            "type": p.type.value,
                            "description": p.description,
                            "enum": p.enum_values,
                        } if p.enum_values else {
                            "type": p.type.value,
                            "description": p.description,
                        }
                        for p in self.parameters
                    },
                    "required": [p.name for p in self.parameters if p.required],
                },
            },
        }

    def validate_call(self, arguments: Dict[str, Any]) -> bool:
        """
        Validate function call arguments.

        Args:
            arguments: Arguments to validate

        Returns:
            True if valid, raises ValueError otherwise
        """
        required_params = {p.name for p in self.parameters if p.required}
        provided_params = set(arguments.keys())

        missing = required_params - provided_params
        if missing:
            raise ValueError(f"Missing required parameters: {missing}")

        # Type validation
        for param in self.parameters:
            if param.name in arguments:
                value = arguments[param.name]

                if param.type == ParameterType.STRING and not isinstance(value, str):
                    raise ValueError(f"{param.name} must be string, got {type(value)}")
                elif param.type == ParameterType.INTEGER and not isinstance(value, int):
                    raise ValueError(f"{param.name} must be integer, got {type(value)}")
                elif param.type == ParameterType.NUMBER and not isinstance(
                    value, (int, float)
                ):
                    raise ValueError(f"{param.name} must be number, got {type(value)}")
                elif param.type == ParameterType.BOOLEAN and not isinstance(value, bool):
                    raise ValueError(f"{param.name} must be boolean, got {type(value)}")
                elif param.type == ParameterType.ARRAY and not isinstance(value, list):
                    raise ValueError(f"{param.name} must be array, got {type(value)}")

                # Enum validation
                if param.enum_values and value not in param.enum_values:
                    raise ValueError(f"{param.name} must be one of {param.enum_values}")

        return True


@dataclass
class FunctionCall:
    """Represents a function call made by an LLM."""

    function_name: str
    arguments: Dict[str, Any]
    call_id: str = ""
    status: str = "pending"  # pending, executing, completed, failed
    result: Any = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "function_name": self.function_name,
            "arguments": self.arguments,
            "call_id": self.call_id,
            "status": self.status,
            "result": self.result,
            "error": self.error,
        }


class FunctionRegistry:
    """Registry for managing callable functions."""

    def __init__(self):
        """Initialize function registry."""
        self.functions: Dict[str, FunctionSchema] = {}
        self.logger = logging.getLogger(__name__)

    def register(
        self,
        fn: Callable,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> FunctionSchema:
        """
        Register a function.

        Args:
            fn: Function to register
            description: Function description
            tags: Optional tags for categorization

        Returns:
            FunctionSchema created for the function
        """
        name = fn.__name__
        docstring = fn.__doc__ or ""
        description = description or docstring.split("\n")[0]

        # Extract parameters from function signature
        sig = inspect.signature(fn)
        parameters = []

        for param_name, param in sig.parameters.items():
            if param_name in ("self", "cls"):
                continue

            # Infer type from annotation
            param_type = self._infer_parameter_type(param.annotation)
            required = param.default == inspect.Parameter.empty

            param_schema = ParameterSchema(
                name=param_name,
                type=param_type,
                description=self._extract_param_doc(docstring, param_name),
                required=required,
                default_value=param.default if param.default != inspect.Parameter.empty else None,
            )
            parameters.append(param_schema)

        # Get return type
        return_type = "any"
        if sig.return_annotation != inspect.Signature.empty:
            return_type = str(sig.return_annotation)

        schema = FunctionSchema(
            name=name,
            description=description,
            callable_fn=fn,
            parameters=parameters,
            return_type=return_type,
            tags=tags or [],
        )

        self.functions[name] = schema
        self.logger.info(f"Registered function: {name}")

        return schema

    def get_function(self, name: str) -> Optional[FunctionSchema]:
        """Get function schema by name."""
        return self.functions.get(name)

    def call_function(
        self,
        name: str,
        arguments: Dict[str, Any],
    ) -> Any:
        """
        Call a registered function.

        Args:
            name: Function name
            arguments: Function arguments

        Returns:
            Function result

        Raises:
            ValueError: If function not found or validation fails
        """
        schema = self.get_function(name)
        if schema is None:
            raise ValueError(f"Function {name} not registered")

        # Validate arguments
        schema.validate_call(arguments)

        try:
            result = schema.callable_fn(**arguments)
            self.logger.debug(f"Function {name} executed successfully")
            return result
        except Exception as e:
            self.logger.error(f"Function {name} failed: {e}")
            raise

    def get_schema_for_llm(self) -> List[Dict[str, Any]]:
        """
        Get all function schemas in LLM format.

        Returns:
            List of OpenAI-compatible function schemas
        """
        return [schema.to_dict() for schema in self.functions.values()]

    def get_function_by_tag(self, tag: str) -> List[FunctionSchema]:
        """Get all functions with a specific tag."""
        return [f for f in self.functions.values() if tag in f.tags]

    def list_functions(self) -> List[str]:
        """List all registered function names."""
        return list(self.functions.keys())

    def _infer_parameter_type(self, annotation: Any) -> ParameterType:
        """Infer parameter type from type annotation."""
        if annotation == inspect.Parameter.empty or annotation is None:
            return ParameterType.STRING

        if annotation == str:
            return ParameterType.STRING
        elif annotation == int:
            return ParameterType.INTEGER
        elif annotation in (float, int):
            return ParameterType.NUMBER
        elif annotation == bool:
            return ParameterType.BOOLEAN
        elif annotation in (list, List):
            return ParameterType.ARRAY
        elif annotation in (dict, Dict):
            return ParameterType.OBJECT
        else:
            # Check for generic types like List[str], Dict[str, Any]
            origin = getattr(annotation, "__origin__", None)
            if origin == list:
                return ParameterType.ARRAY
            elif origin == dict:
                return ParameterType.OBJECT

        return ParameterType.STRING

    def _extract_param_doc(self, docstring: str, param_name: str) -> str:
        """Extract parameter documentation from docstring."""
        lines = docstring.split("\n")
        in_args = False

        for i, line in enumerate(lines):
            if "Args:" in line or "Parameters:" in line:
                in_args = True
                continue
            elif in_args and line.strip().startswith(param_name):
                # Extract until next line or next section
                desc_lines = []
                for j in range(i + 1, len(lines)):
                    next_line = lines[j]
                    if (next_line.strip() and not next_line.startswith(" ") or
                        any(x in next_line for x in ["Args:", "Returns:", "Raises:"])):
                        break
                    if next_line.strip():
                        desc_lines.append(next_line.strip())

                return " ".join(desc_lines)

        return ""


class FunctionCallExecutor:
    """Executes function calls from LLM responses."""

    def __init__(self, registry: FunctionRegistry):
        """
        Initialize executor.

        Args:
            registry: FunctionRegistry with registered functions
        """
        self.registry = registry
        self.call_history: List[FunctionCall] = []
        self.logger = logging.getLogger(__name__)

    def execute_call(self, function_name: str, arguments: Dict[str, Any]) -> FunctionCall:
        """
        Execute a function call.

        Args:
            function_name: Name of function to call
            arguments: Arguments to pass

        Returns:
            FunctionCall with result
        """
        call = FunctionCall(
            function_name=function_name,
            arguments=arguments,
            call_id=f"{function_name}_{len(self.call_history)}",
        )

        try:
            call.status = "executing"
            result = self.registry.call_function(function_name, arguments)
            call.result = result
            call.status = "completed"
        except Exception as e:
            call.error = str(e)
            call.status = "failed"
            self.logger.error(f"Function call failed: {e}")

        self.call_history.append(call)
        return call

    def execute_calls(
        self,
        calls: List[Dict[str, Any]],
    ) -> List[FunctionCall]:
        """
        Execute multiple function calls.

        Args:
            calls: List of {"function_name": str, "arguments": dict}

        Returns:
            List of FunctionCall results
        """
        results = []
        for call in calls:
            result = self.execute_call(
                call["function_name"],
                call.get("arguments", {}),
            )
            results.append(result)

        return results

    def get_call_results(self) -> List[Dict[str, Any]]:
        """Get all call results formatted for LLM."""
        return [
            {
                "id": call.call_id,
                "name": call.function_name,
                "result": call.result if call.status == "completed" else None,
                "error": call.error if call.status == "failed" else None,
            }
            for call in self.call_history
        ]
