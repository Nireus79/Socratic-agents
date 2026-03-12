"""Benchmark-specific fixtures and utilities."""

import pytest
import tracemalloc
from typing import Callable, Dict, Any


@pytest.fixture
def memory_tracker():
    """Track memory usage during benchmarks."""

    def track(func: Callable) -> Dict[str, int]:
        tracemalloc.start()
        func()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        return {"current_kb": current // 1024, "peak_kb": peak // 1024}

    return track


@pytest.fixture
def sample_maturity_data():
    """Sample maturity data for benchmarks."""
    return {
        "current_phase": "discovery",
        "completion_percent": 35,
        "weak_categories": ["problem_definition", "scope"],
        "category_scores": {
            "problem_definition": 0.3,
            "scope": 0.4,
            "architecture": 0.8,
        },
    }


@pytest.fixture
def sample_learning_data():
    """Sample learning data for benchmarks."""
    return {"learning_velocity": "medium", "engagement_score": 0.75, "completion_rate": 0.6}


@pytest.fixture
def sample_code_medium():
    """Medium-sized code sample for benchmarks."""
    return """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n-1)

class Calculator:
    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b

    def multiply(self, a, b):
        return a * b

    def divide(self, a, b):
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
"""


@pytest.fixture
def sample_code_large():
    """Large code sample for stress testing."""
    # Generate a large code block
    return "\n".join([f"def function_{i}(x):\n    return x * {i}\n" for i in range(100)])
