#!/usr/bin/env python
"""
Example: Using SkillGeneratorAgent

This example demonstrates how to use the SkillGeneratorAgent to:
1. Generate skills for weak areas based on maturity and learning data
2. Evaluate skill effectiveness
3. List and filter generated skills
"""

from socratic_agents import SkillGeneratorAgent


def example_generate_discovery_skills():
    """Example 1: Generate skills for discovery phase."""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Generate Skills for Discovery Phase")
    print("=" * 70)

    agent = SkillGeneratorAgent()

    # Simulate maturity data from a project in discovery phase
    maturity_data = {
        "current_phase": "discovery",
        "completion_percent": 35,
        "weak_categories": ["problem_definition", "scope"],
        "category_scores": {
            "problem_definition": 0.3,  # Very weak
            "scope": 0.5,  # Moderately weak
            "target_audience": 0.85  # Strong
        }
    }

    # Simulate learning data from user engagement
    learning_data = {
        "learning_velocity": "medium",
        "engagement_score": 0.75,
        "question_effectiveness": {
            "discovery_questions": 0.8,
            "follow_up_questions": 0.7
        },
        "behavior_patterns": {
            "prefers_examples": True,
            "asks_clarifications": True
        }
    }

    # Generate skills
    result = agent.process({
        "action": "generate",
        "maturity_data": maturity_data,
        "learning_data": learning_data
    })

    print(f"\nStatus: {result['status']}")
    print(f"Phase: {result['phase']}")
    print(f"Completion: {result['completion_percent']}%")
    print(f"Skills Generated: {result['skills_generated']}\n")

    # Display recommendations
    print("Skill Recommendations (prioritized):")
    for i, rec in enumerate(result["recommendations"], 1):
        skill = rec["skill"]
        print(f"\n{i}. {skill['id']}")
        print(f"   Target Agent: {skill['target_agent']}")
        print(f"   Focus: {skill['category_focus']}")
        print(f"   Priority: {rec['priority']}")
        print(f"   Expected Impact: {rec['expected_impact']:.0%}")
        print(f"   Reason: {rec['reason']}")


def example_evaluate_skills():
    """Example 2: Evaluate skill effectiveness."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Evaluate Skill Effectiveness")
    print("=" * 70)

    agent = SkillGeneratorAgent()

    # Generate skills first
    gen_result = agent.process({
        "action": "generate",
        "maturity_data": {
            "current_phase": "discovery",
            "completion_percent": 35,
            "weak_categories": ["problem_definition"],
            "category_scores": {"problem_definition": 0.3}
        },
        "learning_data": {
            "learning_velocity": "medium",
            "engagement_score": 0.75
        }
    })

    skill_id = gen_result["skills"][0]["id"]
    print(f"\nGenerated skill: {skill_id}")

    # Simulate applying the skill and gathering feedback
    print("\nApplying skill and gathering feedback...")

    eval_result = agent.process({
        "action": "evaluate",
        "skill_id": skill_id,
        "feedback": "helped",
        "effectiveness_score": 0.85
    })

    print(f"\nEvaluation Result:")
    print(f"Status: {eval_result['status']}")
    print(f"Skill ID: {eval_result['skill_id']}")
    print(f"Feedback: {eval_result['feedback']}")
    print(f"Effectiveness Score: {eval_result['effectiveness_score']}")


def example_list_skills():
    """Example 3: List and filter skills."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: List and Filter Skills")
    print("=" * 70)

    agent = SkillGeneratorAgent()

    # Generate skills for multiple phases
    phases = [
        ("discovery", "problem_definition"),
        ("analysis", "functional_requirements"),
        ("design", "architecture"),
    ]

    print(f"\nGenerating skills for {len(phases)} phases...")

    for phase, weak_category in phases:
        agent.process({
            "action": "generate",
            "maturity_data": {
                "current_phase": phase,
                "completion_percent": 50,
                "weak_categories": [weak_category],
                "category_scores": {weak_category: 0.3}
            },
            "learning_data": {
                "learning_velocity": "medium",
                "engagement_score": 0.7
            }
        })

    # List all skills
    all_skills = agent.process({"action": "list"})
    print(f"\nTotal skills generated: {all_skills['skills_count']}")

    # List skills by phase
    for phase in ["discovery", "analysis", "design"]:
        phase_skills = agent.process({
            "action": "list",
            "phase": phase
        })
        print(f"Skills in {phase} phase: {phase_skills['skills_count']}")

    # List skills by target agent
    counselor_skills = agent.process({
        "action": "list",
        "agent_name": "SocraticCounselor"
    })
    print(f"\nSkills targeting SocraticCounselor: {counselor_skills['skills_count']}")

    generator_skills = agent.process({
        "action": "list",
        "agent_name": "CodeGenerator"
    })
    print(f"Skills targeting CodeGenerator: {generator_skills['skills_count']}")


def example_multi_phase_workflow():
    """Example 4: Complete multi-phase workflow."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Complete Multi-Phase Workflow")
    print("=" * 70)

    agent = SkillGeneratorAgent()
    phase_info = [
        {
            "name": "discovery",
            "weak_categories": ["problem_definition", "scope"],
            "category_scores": {
                "problem_definition": 0.25,
                "scope": 0.5,
                "target_audience": 0.8
            }
        },
        {
            "name": "analysis",
            "weak_categories": ["functional_requirements", "data_requirements"],
            "category_scores": {
                "functional_requirements": 0.3,
                "non_functional_requirements": 0.7,
                "data_requirements": 0.4
            }
        },
        {
            "name": "design",
            "weak_categories": ["architecture"],
            "category_scores": {
                "architecture": 0.2,
                "technology_stack": 0.6,
                "integrations": 0.7
            }
        }
    ]

    print("\nPhase-by-Phase Skill Generation:\n")

    for phase_data in phase_info:
        phase = phase_data["name"]
        print(f"{phase.upper()} PHASE:")
        print("-" * 40)

        # Generate skills
        gen_result = agent.process({
            "action": "generate",
            "maturity_data": {
                "current_phase": phase,
                "completion_percent": 40,
                "weak_categories": phase_data["weak_categories"],
                "category_scores": phase_data["category_scores"]
            },
            "learning_data": {
                "learning_velocity": "medium",
                "engagement_score": 0.7
            }
        })

        print(f"Generated {gen_result['skills_generated']} skills")

        # Show top priority skill
        if gen_result["recommendations"]:
            top_skill = gen_result["recommendations"][0]
            print(f"Top Priority: {top_skill['skill']['id']} ({top_skill['priority']})")
            print(f"Expected Impact: {top_skill['expected_impact']:.0%}")

        # Evaluate generated skills
        for skill in gen_result["skills"]:
            agent.process({
                "action": "evaluate",
                "skill_id": skill["id"],
                "feedback": "helped",
                "effectiveness_score": 0.75
            })

        print()

    # Final summary
    all_skills = agent.process({"action": "list"})
    print(f"\nFinal Summary: {all_skills['skills_count']} total skills generated and evaluated")


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("SKILLAGENERATOR AGENT EXAMPLES")
    print("=" * 70)

    example_generate_discovery_skills()
    example_evaluate_skills()
    example_list_skills()
    example_multi_phase_workflow()

    print("\n" + "=" * 70)
    print("Examples Complete!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
