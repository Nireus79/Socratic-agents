"""Pytest configuration and fixtures for Socratic Agents tests."""

from unittest.mock import Mock

import pytest


@pytest.fixture
def sample_task() -> str:
    """Sample task for testing."""
    return "Generate a Python function for sorting"


@pytest.fixture
def sample_agents() -> list:
    """Sample agent list for testing."""
    return ["code_generator", "code_validator"]


@pytest.fixture
def mock_llm_client():
    """Mock LLM client for testing without real API calls."""
    mock = Mock()
    mock.chat.return_value = Mock(content="Generated response from LLM")
    return mock


@pytest.fixture
def mock_llm_client_error():
    """Mock LLM client that raises errors for testing error handling."""
    mock = Mock()
    mock.chat.side_effect = Exception("LLM service unavailable")
    return mock


@pytest.fixture
def sample_code() -> str:
    """Sample Python code for validation testing."""
    return """def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""


@pytest.fixture
def sample_code_with_errors() -> str:
    """Sample Python code with syntax/quality issues."""
    return """def bad_function():
x = 1
y = 2
  z = 3
return x + y + z
"""
