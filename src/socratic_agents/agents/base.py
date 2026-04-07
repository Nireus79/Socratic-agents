"""Base Agent class for Socratic Agents - imported from socratic-core (hub).

This module re-exports the unified Agent base class from socratic-core,
implementing the hub-and-spoke architecture where all 12 Socratic libraries
import the Agent base class from a single source of truth.
"""

# Import unified Agent from socratic-core (hub-and-spoke architecture)
from socratic_core import Agent

# Backward compatibility alias - existing code may use BaseAgent
BaseAgent = Agent

__all__ = ["Agent", "BaseAgent"]
