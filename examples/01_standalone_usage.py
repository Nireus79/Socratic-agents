#!/usr/bin/env python
"""
Demonstrates using Socratic Agents WITHOUT Socrates Nexus.

Agents use rule-based behavior and internal templates when no LLM client is provided.
This example requires: pip install socratic-agents
"""

from socratic_agents import (
    SocraticCounselor,
    CodeGenerator,
    CodeValidator,
    QualityController,
)


def main():
    print("=" * 60)
    print("STANDALONE AGENT USAGE (No LLM Required)")
    print("=" * 60)
    print()

    # 1. Socratic Counselor - Uses question templates
    print("1. SOCRATIC COUNSELOR - Guided Learning")
    print("-" * 60)
    counselor = SocraticCounselor()
    result = counselor.process({
        "action": "guide",
        "topic": "Python recursion",
        "level": "beginner"
    })

    questions = result.get('questions', [])
    print(f"Topic: Python recursion (beginner level)")
    print(f"Questions generated: {len(questions)}")
    for i, q in enumerate(questions[:3], 1):
        print(f"  {i}. {q}")
    print()

    # 2. Code Generator - Returns stub code
    print("2. CODE GENERATOR - Code Template Generation")
    print("-" * 60)
    generator = CodeGenerator()
    code_result = generator.process({
        "prompt": "Create a fibonacci function",
        "language": "python"
    })

    code = code_result.get('code', '')
    print(f"Prompt: Create a fibonacci function")
    print(f"Language: Python")
    print(f"Generated code (stub):")
    print(code[:150] if len(code) > 150 else code)
    if len(code) > 150:
        print("...")
    print()

    # 3. Code Validator - Basic syntax checks
    print("3. CODE VALIDATOR - Syntax & Quality Checks")
    print("-" * 60)
    validator = CodeValidator()
    test_code = """def hello():
    print('world')
    return 42"""

    val_result = validator.process({
        "code": test_code,
        "language": "python"
    })

    print(f"Code being validated:")
    print(test_code)
    print()
    print(f"Validation Results:")
    print(f"  Valid: {val_result.get('valid', False)}")
    print(f"  Issues found: {len(val_result.get('issues', []))}")
    if val_result.get('issues'):
        for issue in val_result['issues'][:3]:
            print(f"    - {issue}")
    print()

    # 4. Quality Controller - Static analysis & metrics
    print("4. QUALITY CONTROLLER - Code Quality Analysis")
    print("-" * 60)
    quality = QualityController()
    quality_result = quality.process({
        "action": "detect_weak_areas",
        "code": "def simple(): pass"
    })

    print(f"Code analyzed: def simple(): pass")
    print(f"Quality Score: {quality_result.get('quality_score', 0):.1f}/100")

    weak_categories = quality_result.get('weak_categories', {})
    if weak_categories:
        print(f"Weak areas detected:")
        for category, score in list(weak_categories.items())[:3]:
            print(f"  - {category}: {score:.1f}%")
    print()

    print("=" * 60)
    print("Standalone agents working WITHOUT Socrates Nexus!")
    print("For LLM-powered features: pip install socratic-agents[nexus]")
    print("=" * 60)


if __name__ == "__main__":
    main()
