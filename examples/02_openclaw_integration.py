"""Example: Using Socratic Agents with Openclaw."""

from socratic_agents.integrations.openclaw import SocraticAgentsSkill
from socrates_nexus import LLMClient


def main():
    """Run Openclaw integration example."""
    print("Openclaw Integration Example")
    print("=" * 50)
    
    # Create LLM client (optional - agents work without it)
    try:
        llm_client = LLMClient(provider="anthropic", model="claude-opus")
    except Exception as e:
        print(f"Note: LLMClient not configured ({e})")
        llm_client = None
    
    # Create Openclaw skill
    skill = SocraticAgentsSkill(llm_client=llm_client)
    
    # Example 1: List available agents
    print("\n1. Available Agents:")
    agents = skill.list_agents()
    for agent in agents:
        print(f"   - {agent}")
    
    # Example 2: Use Socratic Counselor agent
    print("\n2. Socratic Guidance:")
    guidance = skill.guide("Python recursion", level="beginner")
    print(f"Topic: {guidance['topic']}")
    print("Guiding questions:")
    for q in guidance.get('questions', []):
        print(f"  • {q}")
    
    # Example 3: Generate code
    print("\n3. Code Generation:")
    code = skill.generate_code("Create a function to calculate factorial")
    print("Generated code:")
    print(code[:200] + "..." if len(code) > 200 else code)
    
    # Example 4: Validate code
    print("\n4. Code Validation:")
    sample_code = "def add(a, b):\n    return a + b"
    validation = skill.validate_code(sample_code, language="python")
    print(f"Valid: {validation['valid']}")
    print(f"Issues found: {validation['issue_count']}")
    
    # Example 5: Multi-agent workflow
    print("\n5. Multi-Agent Workflow:")
    workflow = skill.execute_workflow(
        task="Create and validate a sorting function",
        agents=["code_generator", "code_validator"]
    )
    print(f"Agents executed: {workflow['agents_executed']}")
    
    print("\n" + "=" * 50)
    print("✅ Openclaw integration example complete!")


if __name__ == "__main__":
    main()
