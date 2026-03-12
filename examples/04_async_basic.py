#!/usr/bin/env python
"""
Demonstrates basic async usage with Socratic Agents.

Shows how to use process_async() for non-blocking agent operations.

Requirements: pip install socratic-agents
"""

import asyncio
from socratic_agents import (
    SocraticCounselor,
    CodeGenerator,
    CodeValidator,
)


async def single_agent_async():
    """Demonstrate single agent async call."""
    print("=== SINGLE AGENT ASYNC ===\n")

    counselor = SocraticCounselor()

    # Use process_async instead of process
    result = await counselor.process_async({
        "action": "guide",
        "topic": "Python async programming",
        "level": "intermediate"
    })

    print(f"Async result received!")
    print(f"Questions: {result.get('questions', [])[:3]}")
    print()


async def parallel_agents():
    """Demonstrate parallel agent execution."""
    print("=== PARALLEL AGENT EXECUTION ===\n")

    counselor = SocraticCounselor()
    generator = CodeGenerator()
    validator = CodeValidator()

    # Create tasks
    counselor_task = counselor.process_async({
        "action": "guide",
        "topic": "async patterns",
        "level": "advanced"
    })

    generator_task = generator.process_async({
        "prompt": "async function for API calls",
        "language": "python"
    })

    validator_task = validator.process_async({
        "code": "async def fetch(): return 'data'",
        "language": "python"
    })

    # Wait for all to complete (runs concurrently!)
    print("Running 3 agents in parallel...")
    import time
    start = time.perf_counter()

    guidance, code, validation = await asyncio.gather(
        counselor_task,
        generator_task,
        validator_task
    )

    end = time.perf_counter()
    print(f"✓ All completed in {end - start:.2f}s")
    print()

    print(f"Guidance questions: {len(guidance.get('questions', []))}")
    print(f"Generated code: {len(code.get('code', ''))} chars")
    print(f"Validation result: {validation.get('valid', False)}")
    print()


async def async_workflow():
    """Demonstrate async workflow with multiple steps."""
    print("=== ASYNC WORKFLOW ===\n")

    generator = CodeGenerator()
    validator = CodeValidator()

    # Step 1: Generate code
    print("1. Generating code...")
    gen_result = await generator.process_async({
        "prompt": "Fibonacci function with memoization",
        "language": "python"
    })
    generated_code = gen_result.get("code", "")
    print(f"   Generated {len(generated_code)} chars")

    # Step 2: Validate generated code
    print("2. Validating code...")
    val_result = await validator.process_async({
        "code": generated_code,
        "language": "python"
    })
    print(f"   Valid: {val_result.get('valid', False)}")
    print()


async def main():
    """Run all async examples."""
    print("=" * 60)
    print("ASYNC AGENT EXAMPLES")
    print("=" * 60)
    print()

    await single_agent_async()
    await parallel_agents()
    await async_workflow()

    print("=" * 60)
    print("All async examples complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
