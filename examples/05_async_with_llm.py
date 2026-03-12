#!/usr/bin/env python
"""
Demonstrates async usage with LLM-powered agents.

Shows how async becomes more valuable with I/O-bound LLM calls,
enabling true parallelism for multiple LLM requests.

Requirements: pip install socratic-agents[nexus]
"""

import asyncio
import os
from socratic_agents import (
    LLMPoweredCounselor,
    LLMPoweredCodeGenerator,
    LLMPoweredCodeValidator,
)


async def concurrent_llm_calls():
    """Demonstrate concurrent LLM calls for better performance."""
    print("=== CONCURRENT LLM CALLS ===\n")

    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠ ANTHROPIC_API_KEY not set - using mock mode")
        print("  Set API key to see real concurrent LLM calls\n")
        return

    from socrates_nexus import LLMClient
    llm = LLMClient(provider="anthropic", model="claude-sonnet")

    # Create LLM-powered agents
    counselor = LLMPoweredCounselor(llm_client=llm)
    generator = LLMPoweredCodeGenerator(llm_client=llm)

    import time

    # Sequential execution (slow)
    print("Sequential execution:")
    start = time.perf_counter()

    result1 = counselor.guide_with_context("algorithms", level="advanced")
    result2 = generator.generate_with_tests("Binary search tree", language="python")

    sequential_time = time.perf_counter() - start
    print(f"  Time: {sequential_time:.2f}s\n")

    # Parallel execution (fast!)
    print("Parallel execution:")
    start = time.perf_counter()

    # Note: Agents don't have native async yet, so this uses executor pattern
    # Future: If LLM client supports async, this would be truly concurrent
    results = await asyncio.gather(
        asyncio.to_thread(counselor.guide_with_context, "algorithms", level="advanced"),
        asyncio.to_thread(generator.generate_with_tests, "Binary search tree", language="python")
    )

    parallel_time = time.perf_counter() - start
    print(f"  Time: {parallel_time:.2f}s")
    if sequential_time > 0:
        print(f"  Speedup: {sequential_time / parallel_time:.1f}x faster!\n")


async def main():
    """Run async LLM examples."""
    print("=" * 60)
    print("ASYNC LLM AGENT EXAMPLES")
    print("=" * 60)
    print()

    await concurrent_llm_calls()

    print("=" * 60)
    print("Async with LLM complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
