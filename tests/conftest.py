"""Pytest configuration and fixtures for Socratic Agents tests."""

import pytest


@pytest.fixture
def sample_task() -> str:
    """Sample task for testing."""
    return "Generate a Python function for sorting"


@pytest.fixture
def sample_agents() -> list:
    """Sample agent list for testing."""
    return ["code_generator", "code_validator"]
