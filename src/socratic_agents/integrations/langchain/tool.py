"""LangChain tool for Socratic Agents orchestration."""

from typing import Dict, Any, Optional, List, Union
from socratic_agents import BaseAgent, SocraticCounselor, CodeGenerator, CodeValidator


class SocraticAgentsTool:
    """
    LangChain tool for using Socratic Agents within LangChain workflows.
    
    Can be used in LangChain chains and agents to leverage multi-agent orchestration.
    """

    def __init__(self, llm_client: Optional[Any] = None, **kwargs):
        """
        Initialize the Socratic Agents tool.
        
        Args:
            llm_client: Optional LLMClient from Socrates Nexus
            **kwargs: Additional configuration
        """
        self.llm_client = llm_client
        self.config = kwargs
        
        # Initialize key agents
        self.counselor = SocraticCounselor(llm_client=llm_client)
        self.code_generator = CodeGenerator(llm_client=llm_client)
        self.code_validator = CodeValidator(llm_client=llm_client)

    def _run(
        self,
        agent_type: str = "counselor",
        task: str = "",
        **kwargs
    ) -> str:
        """
        Execute an agent synchronously.
        
        Args:
            agent_type: Type of agent to use (counselor, code_generator, code_validator)
            task: Task description or prompt
            **kwargs: Additional parameters
            
        Returns:
            String result from the agent
        """
        try:
            if agent_type == "counselor":
                topic = kwargs.get("topic", task)
                level = kwargs.get("level", "beginner")
                result = self.counselor.guide(topic, level)
                questions = result.get("questions", [])
                return "\n".join(questions)
            
            elif agent_type == "code_generator":
                prompt = kwargs.get("prompt", task)
                language = kwargs.get("language", "python")
                result = self.code_generator.process({
                    "prompt": prompt,
                    "language": language
                })
                return result.get("code", "")
            
            elif agent_type == "code_validator":
                code = kwargs.get("code", task)
                language = kwargs.get("language", "python")
                result = self.code_validator.validate(code, language)
                if result["valid"]:
                    return "Code is valid ✓"
                else:
                    issues = result.get("issues", [])
                    return f"Found {len(issues)} issues:\n" + "\n".join(
                        str(issue) for issue in issues
                    )
            
            else:
                return f"Unknown agent type: {agent_type}"
        
        except Exception as e:
            return f"Error: {str(e)}"

    async def _arun(
        self,
        agent_type: str = "counselor",
        task: str = "",
        **kwargs
    ) -> str:
        """
        Execute an agent asynchronously.
        
        Args:
            agent_type: Type of agent to use
            task: Task description or prompt
            **kwargs: Additional parameters
            
        Returns:
            String result from the agent
        """
        # For now, wrap the sync version
        # In the future, could use true async
        return self._run(agent_type, task, **kwargs)

    def guide_learning(self, topic: str, level: str = "beginner") -> str:
        """
        Get Socratic guidance on a topic.
        
        Args:
            topic: Topic to learn about
            level: Learning level
            
        Returns:
            Guiding questions
        """
        return self._run("counselor", topic=topic, level=level)

    def generate_code(self, prompt: str, language: str = "python") -> str:
        """
        Generate code using the code generator agent.
        
        Args:
            prompt: Description of code to generate
            language: Programming language
            
        Returns:
            Generated code
        """
        return self._run("code_generator", prompt=prompt, language=language)

    def validate_code(self, code: str, language: str = "python") -> str:
        """
        Validate code using the code validator agent.
        
        Args:
            code: Code to validate
            language: Programming language
            
        Returns:
            Validation result
        """
        return self._run("code_validator", code=code, language=language)


# LangChain integration helper
def create_socratic_tools(llm_client: Optional[Any] = None) -> List[Dict[str, Any]]:
    """
    Create a list of LangChain-compatible tools from Socratic Agents.
    
    Args:
        llm_client: Optional LLMClient from Socrates Nexus
        
    Returns:
        List of tool dictionaries for LangChain agents
    """
    agents_tool = SocraticAgentsTool(llm_client=llm_client)
    
    return [
        {
            "name": "socratic_guide",
            "description": "Get Socratic guidance on a topic through questioning",
            "func": agents_tool.guide_learning,
        },
        {
            "name": "code_generator",
            "description": "Generate code based on a description",
            "func": agents_tool.generate_code,
        },
        {
            "name": "code_validator",
            "description": "Validate code for errors and issues",
            "func": agents_tool.validate_code,
        },
    ]
