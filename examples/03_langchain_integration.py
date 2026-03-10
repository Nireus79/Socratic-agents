"""Example: Using Socratic Agents with LangChain."""

from socratic_agents.integrations.langchain import SocraticAgentsTool, create_socratic_tools
from socrates_nexus import LLMClient


def main():
    """Run LangChain integration example."""
    print("LangChain Integration Example")
    print("=" * 50)
    
    # Create LLM client (optional)
    try:
        llm_client = LLMClient(provider="anthropic", model="claude-opus")
    except Exception as e:
        print(f"Note: LLMClient not configured ({e})")
        llm_client = None
    
    # Create Socratic Agents tool
    agents_tool = SocraticAgentsTool(llm_client=llm_client)
    
    # Example 1: Direct tool usage
    print("\n1. Direct Tool Usage:")
    
    # Guide learning
    guidance = agents_tool.guide_learning("List comprehensions in Python", level="intermediate")
    print("Socratic guidance:")
    print(guidance[:200] + "..." if len(guidance) > 200 else guidance)
    
    # Example 2: Generate code
    print("\n2. Code Generation:")
    code = agents_tool.generate_code("Create a list comprehension to square numbers 1-10")
    print("Generated:")
    print(code[:150] + "..." if len(code) > 150 else code)
    
    # Example 3: Validate code
    print("\n3. Code Validation:")
    result = agents_tool.validate_code("[x**2 for x in range(1, 11)]", language="python")
    print(f"Result: {result[:150]}...")
    
    # Example 4: Create tools for LangChain agent
    print("\n4. Creating LangChain Tools:")
    tools = create_socratic_tools(llm_client=llm_client)
    print(f"Created {len(tools)} tools:")
    for tool in tools:
        print(f"  • {tool['name']}: {tool['description']}")
    
    print("\n" + "=" * 50)
    print("✅ LangChain integration example complete!")
    print("\nTo use in LangChain:")
    print("  from langchain.agents import initialize_agent")
    print("  from socratic_agents.integrations.langchain import create_socratic_tools")
    print("  ")
    print("  tools = create_socratic_tools(llm_client)")
    print("  agent = initialize_agent(tools, llm, agent_type='zero-shot-react-description')")


if __name__ == "__main__":
    main()
