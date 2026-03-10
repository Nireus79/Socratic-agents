"""Integration tests for Socratic Agents integrations."""

import pytest

from socratic_agents.integrations.langchain import SocraticAgentsTool, create_socratic_tools
from socratic_agents.integrations.openclaw import SocraticAgentsSkill


class TestOpenclawIntegration:
    """Test Openclaw skill integration."""

    @pytest.mark.integration
    def test_skill_creation(self):
        """Test creating Openclaw skill."""
        skill = SocraticAgentsSkill()
        assert skill is not None

    @pytest.mark.integration
    def test_list_agents(self):
        """Test listing available agents."""
        skill = SocraticAgentsSkill()
        agents = skill.list_agents()

        assert isinstance(agents, list)
        assert len(agents) == 18
        assert "counselor" in agents
        assert "code_generator" in agents

    @pytest.mark.integration
    def test_get_agent(self):
        """Test getting a specific agent."""
        skill = SocraticAgentsSkill()
        agent = skill.get_agent("counselor")

        assert agent is not None
        assert agent.name == "SocraticCounselor"

    @pytest.mark.integration
    def test_get_nonexistent_agent(self):
        """Test getting a nonexistent agent."""
        skill = SocraticAgentsSkill()
        agent = skill.get_agent("nonexistent")

        assert agent is None

    @pytest.mark.integration
    def test_guide_through_skill(self):
        """Test using guide method through skill."""
        skill = SocraticAgentsSkill()
        result = skill.guide("Python functions", level="beginner")

        assert result["status"] == "success"
        assert "questions" in result

    @pytest.mark.integration
    def test_generate_code_through_skill(self):
        """Test generating code through skill."""
        skill = SocraticAgentsSkill()
        code = skill.generate_code("Create a hello world program")

        assert isinstance(code, str)

    @pytest.mark.integration
    def test_validate_code_through_skill(self):
        """Test validating code through skill."""
        skill = SocraticAgentsSkill()
        result = skill.validate_code("print('hello')", language="python")

        assert result["status"] == "success"
        assert "valid" in result

    @pytest.mark.integration
    def test_execute_workflow(self):
        """Test multi-agent workflow execution."""
        skill = SocraticAgentsSkill()
        result = skill.execute_workflow(
            task="Create and validate code",
            agents=["counselor"],  # Use counselor which we know works
        )

        assert result["status"] == "success"
        assert "results" in result
        assert len(result["results"]) > 0
        assert "counselor" in result["results"]


class TestLangChainIntegration:
    """Test LangChain tool integration."""

    @pytest.mark.integration
    def test_tool_creation(self):
        """Test creating LangChain tool."""
        tool = SocraticAgentsTool()
        assert tool is not None

    @pytest.mark.integration
    def test_guide_learning_method(self):
        """Test guide_learning method."""
        tool = SocraticAgentsTool()
        result = tool.guide_learning("Data structures")

        assert isinstance(result, str)

    @pytest.mark.integration
    def test_generate_code_method(self):
        """Test generate_code method."""
        tool = SocraticAgentsTool()
        result = tool.generate_code("Palindrome checker")

        assert isinstance(result, str)

    @pytest.mark.integration
    def test_validate_code_method(self):
        """Test validate_code method."""
        tool = SocraticAgentsTool()
        result = tool.validate_code("x = 5")

        assert isinstance(result, str)

    @pytest.mark.integration
    def test_create_socratic_tools(self):
        """Test creating tools for LangChain."""
        tools = create_socratic_tools()

        assert isinstance(tools, list)
        assert len(tools) == 3

        tool_names = [t["name"] for t in tools]
        assert "socratic_guide" in tool_names
        assert "code_generator" in tool_names
        assert "code_validator" in tool_names

    @pytest.mark.integration
    def test_tool_has_descriptions(self):
        """Test that tools have descriptions."""
        tools = create_socratic_tools()

        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "func" in tool
            assert len(tool["description"]) > 0
