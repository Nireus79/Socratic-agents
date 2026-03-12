"""Tests for async agent functionality."""

import pytest
import asyncio
from socratic_agents import SocraticCounselor, CodeGenerator, CodeValidator


class TestAsyncBasicFunctionality:
    """Test basic async functionality."""

    @pytest.mark.asyncio
    async def test_process_async_exists(self):
        """Test that process_async method exists on agents."""
        agent = SocraticCounselor()
        assert hasattr(agent, "process_async")
        assert callable(agent.process_async)

    @pytest.mark.asyncio
    async def test_single_agent_async(self):
        """Test single agent async call."""
        counselor = SocraticCounselor()
        result = await counselor.process_async(
            {"action": "guide", "topic": "testing", "level": "beginner"}
        )

        assert "questions" in result
        assert isinstance(result["questions"], list)

    @pytest.mark.asyncio
    async def test_parallel_agents(self):
        """Test parallel agent execution with asyncio.gather."""
        counselor = SocraticCounselor()
        generator = CodeGenerator()

        results = await asyncio.gather(
            counselor.process_async({"action": "guide", "topic": "async"}),
            generator.process_async({"prompt": "async function", "language": "python"}),
        )

        assert len(results) == 2
        assert "questions" in results[0]
        assert "code" in results[1]


class TestAsyncResultConsistency:
    """Test that async results match synchronous results."""

    @pytest.mark.asyncio
    async def test_async_sync_equivalence(self):
        """Test that async and sync produce same results."""
        agent = SocraticCounselor()
        request = {"action": "guide", "topic": "Python", "level": "beginner"}

        # Get sync result
        sync_result = agent.process(request)

        # Get async result
        async_result = await agent.process_async(request)

        # Results should be equivalent
        assert sync_result.keys() == async_result.keys()
        assert sync_result.get("status") == async_result.get("status")

    @pytest.mark.asyncio
    async def test_multiple_agents_consistency(self):
        """Test that all agents work asynchronously consistently."""
        agents = [
            SocraticCounselor(),
            CodeGenerator(),
            CodeValidator(),
        ]

        # Test each agent has async support
        for agent in agents:
            assert hasattr(agent, "process_async")

        # Test they all return results
        results = await asyncio.gather(
            *[
                agent.process_async(
                    {"action": "test"}
                    if i == 0
                    else (
                        {"prompt": "test", "language": "python"}
                        if i == 1
                        else {"code": "pass", "language": "python"}
                    )
                )
                for i, agent in enumerate(agents)
            ]
        )

        assert len(results) == 3
        assert all(isinstance(r, dict) for r in results)
