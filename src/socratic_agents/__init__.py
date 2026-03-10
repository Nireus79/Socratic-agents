"""Socratic Agents - Multi-agent orchestration system for AI workflows."""

__version__ = "0.1.0"
__author__ = "Socratic Agents Contributors"

# Core base class
from .agents.base import BaseAgent

# Agent imports (will be populated as agents are properly structured)
# For now, we provide access to all agents

__all__ = [
    "BaseAgent",
]
