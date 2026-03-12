#!/usr/bin/env python
"""
Demonstrates using Socratic Agents WITH Socrates Nexus for LLM-powered features.

This example shows how to use Socrates Nexus LLM client to enhance agent behavior.

Requirements:
  pip install socratic-agents[nexus]

Set your API key:
  export ANTHROPIC_API_KEY="your-key"
  or set ANTHROPIC_API_KEY environment variable
"""

import os
from socratic_agents import SocraticCounselor, CodeGenerator


def main():
    print("=" * 60)
    print("LLM-POWERED AGENT USAGE (With Socrates Nexus)")
    print("=" * 60)
    print()

    # Initialize Socrates Nexus LLM client
    try:
        from socrates_nexus import LLMClient
    except ImportError:
        print("ERROR: Socrates Nexus not installed!")
        print("Install with: pip install socratic-agents[nexus]")
        return

    # Try to initialize LLM client
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("NOTE: ANTHROPIC_API_KEY not set")
        print("      Set it to use LLM features: export ANTHROPIC_API_KEY=your-key")
        print("      Using agents without LLM enhancement instead...")
        print()

        # Fall back to agents without LLM
        counselor = SocraticCounselor()
        result = counselor.process({
            "action": "guide",
            "topic": "machine learning gradient descent",
            "level": "intermediate"
        })

        print("SOCRATIC COUNSELOR (without LLM)")
        print("-" * 60)
        questions = result.get('questions', [])
        print(f"Topic: machine learning gradient descent")
        for i, q in enumerate(questions[:3], 1):
            print(f"  {i}. {q}")
        print()
        return

    # Create LLM client
    try:
        llm = LLMClient(
            provider="anthropic",
            model="claude-sonnet",
        )
        print("✓ LLM client initialized successfully!")
        print()
    except Exception as e:
        print(f"✗ Failed to initialize LLM client: {e}")
        print("  Check your ANTHROPIC_API_KEY environment variable")
        return

    # 1. Counselor with LLM - Intelligent question generation
    print("1. SOCRATIC COUNSELOR - LLM-Enhanced")
    print("-" * 60)
    try:
        counselor = SocraticCounselor(llm_client=llm)
        result = counselor.process({
            "action": "guide",
            "topic": "machine learning gradient descent",
            "level": "intermediate"
        })

        print("Topic: machine learning gradient descent (intermediate level)")
        questions = result.get('questions', [])
        print(f"Questions generated: {len(questions)}")

        for i, q in enumerate(questions[:3], 1):
            print(f"  {i}. {q}")
        print()

    except Exception as e:
        print(f"Error during counseling: {e}")
        print()

    # 2. Code Generator with LLM - Real code generation
    print("2. CODE GENERATOR - LLM-Powered Generation")
    print("-" * 60)
    try:
        generator = CodeGenerator(llm_client=llm)
        code_result = generator.process({
            "prompt": "Create a simple binary search algorithm in Python",
            "language": "python"
        })

        code = code_result.get('code', '')
        print("Prompt: Create a simple binary search algorithm in Python")
        print()
        print("Generated Code:")
        print(code[:300] if len(code) > 300 else code)
        if len(code) > 300:
            print("... (truncated)")
        print()

    except Exception as e:
        print(f"Error during code generation: {e}")
        print()

    print("=" * 60)
    print("LLM-powered agents using Socrates Nexus!")
    print("For advanced features: Configure your LLM API keys")
    print("=" * 60)


if __name__ == "__main__":
    main()
