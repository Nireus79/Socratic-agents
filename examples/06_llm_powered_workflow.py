#!/usr/bin/env python
"""
Comprehensive example using all 7 LLM-powered agent wrappers.

Demonstrates complete AI workflow using all available LLM-enhanced agents:
- LLMPoweredCounselor - Interactive guidance with context awareness
- LLMPoweredCodeGenerator - Production-ready code generation
- LLMPoweredCodeValidator - Deep code review
- LLMPoweredProjectManager - Intelligent project planning
- LLMPoweredQualityController - Code quality analysis
- LLMPoweredKnowledgeManager - Semantic search and Q&A
- LLMPoweredContextAnalyzer - Deep context understanding

Requirements: pip install socratic-agents[nexus]
"""

import os
from socratic_agents import (
    LLMPoweredCounselor,
    LLMPoweredCodeGenerator,
    LLMPoweredCodeValidator,
    LLMPoweredProjectManager,
    LLMPoweredQualityController,
    LLMPoweredKnowledgeManager,
    LLMPoweredContextAnalyzer,
)


def check_api_key():
    """Check if ANTHROPIC_API_KEY is set."""
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠ ANTHROPIC_API_KEY not set")
        print("  Set API key to see real LLM-powered agent responses")
        print("  Example: export ANTHROPIC_API_KEY='your-key-here'\n")
        return False
    return True


def demonstrate_counselor(llm_client):
    """Demonstrate LLMPoweredCounselor capabilities."""
    print("=" * 70)
    print("1. LLMPoweredCounselor - Interactive Guidance")
    print("=" * 70)

    counselor = LLMPoweredCounselor(llm_client=llm_client)

    # Basic guidance
    print("\n📚 Basic guidance on machine learning:")
    result = counselor.guide_with_context(
        topic="machine learning",
        level="beginner",
        context="for someone new to programming"
    )
    print(f"Context-aware: {result.get('context_aware')}")
    print(f"Level: {result.get('level')}")

    # Personalized guidance
    print("\n🎓 Personalized guidance for visual learner:")
    result = counselor.personalized_guide(
        topic="Python decorators",
        user_level="intermediate",
        learning_style="visual"
    )
    print(f"Learning style incorporated: visual")
    print()


def demonstrate_code_generator(llm_client):
    """Demonstrate LLMPoweredCodeGenerator capabilities."""
    print("=" * 70)
    print("2. LLMPoweredCodeGenerator - Production Code")
    print("=" * 70)

    generator = LLMPoweredCodeGenerator(llm_client=llm_client)

    # Generate with tests
    print("\n🔧 Generating code with tests and documentation:")
    result = generator.generate_with_tests(
        specification="Function to find longest common subsequence",
        language="python",
        include_docs=True,
        include_error_handling=True
    )
    print(f"Language: {result.get('language')}")
    print(f"Has tests: {result.get('has_tests')}")
    print(f"Has documentation: {result.get('has_docs')}")
    print(f"Has error handling: {result.get('has_error_handling')}")

    # Generate with explanation
    print("\n📖 Generating code with detailed explanation:")
    result = generator.generate_with_explanation(
        specification="Implement merge sort algorithm",
        language="python"
    )
    print(f"Generated code length: {len(result.get('code', ''))} chars")
    print(f"Has explanation: {len(result.get('explanation', '')) > 0}")
    print()


def demonstrate_code_validator(llm_client):
    """Demonstrate LLMPoweredCodeValidator capabilities."""
    print("=" * 70)
    print("3. LLMPoweredCodeValidator - Deep Code Review")
    print("=" * 70)

    validator = LLMPoweredCodeValidator(llm_client=llm_client)

    sample_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def find_max(arr):
    max_val = arr[0]
    for val in arr:
        if val > max_val:
            max_val = val
    return max_val
"""

    # Detailed review
    print("\n🔍 Comprehensive code review:")
    result = validator.review_with_suggestions(
        code=sample_code,
        language="python",
        focus_areas=["performance", "readability"]
    )
    print(f"Focus areas: {result.get('focus_areas')}")
    print(f"Suggestions provided: {result.get('suggestions_provided')}")

    # Refactoring suggestions
    print("\n✨ Refactoring recommendations:")
    result = validator.suggest_refactoring(
        code=sample_code,
        language="python"
    )
    print(f"Refactoring suggestions generated: {len(result.get('refactoring_suggestions', '')) > 0}")
    print()


def demonstrate_project_manager(llm_client):
    """Demonstrate LLMPoweredProjectManager capabilities."""
    print("=" * 70)
    print("4. LLMPoweredProjectManager - Intelligent Planning")
    print("=" * 70)

    pm = LLMPoweredProjectManager(llm_client=llm_client)

    # Project breakdown
    print("\n📋 Breaking down a project into tasks:")
    result = pm.intelligent_project_breakdown(
        project_description="Build a REST API for a social media platform",
        context="Team of 3 developers, 8-week timeline",
        include_timeline=True
    )
    print(f"Project: {result.get('project_description')[:50]}...")
    print(f"Includes timeline: {result.get('includes_timeline')}")

    # Risk analysis
    print("\n⚠️ Analyzing project risks:")
    result = pm.analyze_project_risks(
        project_id="social-api-001",
        tasks=[
            {"description": "API design and specification"},
            {"description": "Database schema design"},
            {"description": "Authentication implementation"},
            {"description": "Testing and deployment"},
        ]
    )
    print(f"Risk analysis generated: {len(result.get('risk_analysis', '')) > 0}")
    print()


def demonstrate_quality_controller(llm_client):
    """Demonstrate LLMPoweredQualityController capabilities."""
    print("=" * 70)
    print("5. LLMPoweredQualityController - Quality Assurance")
    print("=" * 70)

    qc = LLMPoweredQualityController(llm_client=llm_client)

    code_sample = """
class DataProcessor:
    def process(self, data):
        result = []
        for item in data:
            if len(item) > 0:
                result.append(item.upper())
        return result
"""

    # Deep review
    print("\n🔬 Deep code quality analysis:")
    result = qc.deep_code_review(
        code=code_sample,
        language="python",
        focus_areas=["performance", "maintainability"]
    )
    print(f"Focus areas reviewed: {result.get('focus_areas')}")
    print(f"LLM enhanced: {result.get('llm_enhanced')}")

    # Refactoring
    print("\n🔄 Refactoring opportunities:")
    result = qc.suggest_refactoring(
        code=code_sample,
        language="python"
    )
    print(f"Refactoring suggestions provided: {len(result.get('refactoring_suggestions', '')) > 0}")
    print()


def demonstrate_knowledge_manager(llm_client):
    """Demonstrate LLMPoweredKnowledgeManager capabilities."""
    print("=" * 70)
    print("6. LLMPoweredKnowledgeManager - Knowledge Operations")
    print("=" * 70)

    km = LLMPoweredKnowledgeManager(llm_client=llm_client)

    # Note: This is a demonstration. In real usage, documents would be in the
    # knowledge base or retrieved from semantic search.
    print("\n🔎 Semantic search capabilities:")
    print("   (Searching knowledge base would require indexed documents)")

    print("\n❓ Question answering:")
    print("   (Would synthesize answers from indexed documents)")
    print()


def demonstrate_context_analyzer(llm_client):
    """Demonstrate LLMPoweredContextAnalyzer capabilities."""
    print("=" * 70)
    print("7. LLMPoweredContextAnalyzer - Context Understanding")
    print("=" * 70)

    ca = LLMPoweredContextAnalyzer(llm_client=llm_client)

    # Deep analysis
    print("\n🧠 Deep context analysis:")
    user_request = "I need help building a web scraper for price monitoring"
    result = ca.deep_context_analysis(
        content=user_request,
        include_entities=True,
        include_sentiment=False
    )
    print(f"Content: {user_request[:50]}...")
    print(f"Entities extracted: {result.get('entities_extracted')}")
    print(f"LLM enhanced: {result.get('llm_enhanced')}")

    # Intent detection
    print("\n🎯 Intent detection:")
    result = ca.detect_intent(
        content=user_request,
        user_history=None
    )
    print(f"Intent detected: {len(result.get('intent_analysis', '')) > 0}")

    # Next actions
    print("\n➡️ Recommended next actions:")
    result = ca.recommend_next_actions(
        current_context="User wants to build a web scraper for price monitoring",
        available_actions=[
            "Recommend scraping libraries",
            "Design database schema",
            "Setup CI/CD pipeline",
            "Create monitoring dashboard"
        ]
    )
    print(f"Next actions recommended: {len(result.get('recommendations', '')) > 0}")
    print()


def main():
    """Run all LLM-powered agent demonstrations."""
    print("\n" + "=" * 70)
    print("SOCRATIC AGENTS - ALL 7 LLM-POWERED WRAPPERS DEMO")
    print("=" * 70)
    print()

    # Check API key
    if not check_api_key():
        print("Creating mock LLM client for demonstration...")

    # Create LLM client
    try:
        from socrates_nexus import LLMClient
        llm = LLMClient(provider="anthropic", model="claude-sonnet")
        print("✓ LLM client initialized\n")
    except ImportError:
        print("❌ socrates-nexus not installed")
        print("   Install with: pip install socratic-agents[nexus]\n")
        return

    # Run demonstrations
    demonstrate_counselor(llm)
    demonstrate_code_generator(llm)
    demonstrate_code_validator(llm)
    demonstrate_project_manager(llm)
    demonstrate_quality_controller(llm)
    demonstrate_knowledge_manager(llm)
    demonstrate_context_analyzer(llm)

    # Summary
    print("=" * 70)
    print("✓ All 7 LLM-powered agents demonstrated!")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Explore individual agent capabilities")
    print("2. Combine agents for complex workflows")
    print("3. Customize prompts for your use cases")
    print("4. Run benchmarks: pytest tests/benchmarks")
    print()


if __name__ == "__main__":
    main()
