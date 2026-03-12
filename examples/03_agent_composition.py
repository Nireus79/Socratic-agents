#!/usr/bin/env python
"""
Demonstrates composing multiple Socratic Agents together.

Shows a complete workflow:
  1. Generate code
  2. Validate syntax
  3. Analyze quality
  4. Generate improvement skills
  5. Track learning patterns

Works with or without Socrates Nexus LLM client.

Requirements: pip install socratic-agents
Optional: pip install socratic-agents[nexus]
"""

from socratic_agents import (
    CodeGenerator,
    CodeValidator,
    QualityController,
    LearningAgent,
    SkillGeneratorAgent,
)


def main():
    print("=" * 70)
    print("AGENT COMPOSITION - Complete Quality Control Workflow")
    print("=" * 70)
    print()

    # Create agents
    generator = CodeGenerator()
    validator = CodeValidator()
    quality = QualityController()
    learning = LearningAgent()
    skill_gen = SkillGeneratorAgent()

    # The code we'll process
    specification = "Implement quicksort algorithm in Python"

    print(f"WORKFLOW SPECIFICATION: {specification}")
    print()
    print("-" * 70)

    # Step 1: Generate code
    print("STEP 1: CODE GENERATION")
    print("-" * 70)
    print(f"Prompt: {specification}")
    gen_result = generator.process({
        "prompt": specification,
        "language": "python"
    })

    generated_code = gen_result.get("code", "")
    print(f"Generated code ({len(generated_code)} chars):")
    print(generated_code[:200])
    if len(generated_code) > 200:
        print("... (truncated)")
    print()

    # Step 2: Validate syntax
    print("STEP 2: CODE VALIDATION")
    print("-" * 70)
    val_result = validator.process({
        "code": generated_code,
        "language": "python"
    })

    is_valid = val_result.get('valid', False)
    issues = val_result.get('issues', [])
    print(f"Syntax Valid: {is_valid}")
    print(f"Issues Found: {len(issues)}")
    if issues:
        for issue in issues[:3]:
            print(f"  - {issue}")
    print()

    # Step 3: Quality analysis
    print("STEP 3: QUALITY ANALYSIS")
    print("-" * 70)
    quality_result = quality.process({
        "action": "detect_weak_areas",
        "code": generated_code
    })

    quality_score = quality_result.get('quality_score', 0)
    weak_categories = quality_result.get('weak_categories', {})

    print(f"Overall Quality Score: {quality_score:.1f}/100")
    if weak_categories:
        print(f"Weak Areas Detected:")
        for category, score in list(weak_categories.items())[:5]:
            print(f"  - {category}: {score:.1f}%")
    print()

    # Step 4: Generate improvement skills
    print("STEP 4: SKILL GENERATION FOR IMPROVEMENT")
    print("-" * 70)
    skill_result = skill_gen.process({
        "action": "generate",
        "maturity_data": quality_result
    })

    skills = skill_result.get('skills', [])
    print(f"Skills Generated: {len(skills)}")
    for i, skill in enumerate(skills[:3], 1):
        skill_dict = skill if isinstance(skill, dict) else {"name": str(skill)}
        skill_name = skill_dict.get('name', str(skill))
        print(f"  {i}. {skill_name}")
    print()

    # Step 5: Learning agent tracks patterns
    print("STEP 5: LEARNING - PATTERN TRACKING")
    print("-" * 70)
    learning_result = learning.process({
        "action": "record_interaction",
        "interaction_type": "code_generation",
        "context": {
            "prompt": specification,
            "quality_score": quality_score,
            "language": "python",
            "weak_areas": len(weak_categories)
        }
    })

    print(f"Interaction Recorded: {learning_result.get('status', 'unknown')}")
    print(f"Data Points Captured:")
    print(f"  - Prompt: {specification}")
    print(f"  - Quality Score: {quality_score:.1f}")
    print(f"  - Language: Python")
    print(f"  - Weak Areas: {len(weak_categories)}")
    print()

    # Summary
    print("=" * 70)
    print("WORKFLOW COMPLETE")
    print("=" * 70)
    print()
    print("Summary:")
    print(f"  ✓ Code generated: {len(generated_code)} chars")
    print(f"  ✓ Validation: {'PASS' if is_valid else 'FAIL'} ({len(issues)} issues)")
    print(f"  ✓ Quality score: {quality_score:.1f}/100")
    print(f"  ✓ Skills generated: {len(skills)}")
    print(f"  ✓ Learning pattern recorded")
    print()
    print("This workflow demonstrates:")
    print("  - Agent composition without orchestrator")
    print("  - Sequential processing through multiple agents")
    print("  - Data flow between agents")
    print("  - Learning from interactions")
    print()


if __name__ == "__main__":
    main()
