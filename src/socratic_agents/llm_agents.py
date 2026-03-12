"""
LLM-enhanced agent wrappers for advanced features.

These classes require Socrates Nexus LLM client and provide
intelligent, context-aware agent behavior with additional capabilities
beyond the base agents.

Usage:
    from socratic_agents import SocraticCounselor
    from socratic_agents.llm_agents import LLMPoweredCounselor
    from socrates_nexus import LLMClient

    llm = LLMClient(provider="anthropic", model="claude-sonnet")
    counselor = LLMPoweredCounselor(llm_client=llm)
    result = counselor.guide_with_context("machine learning", context="for beginners")
"""

from typing import Any, Dict, List, Optional

from .agents import (
    CodeGenerator,
    CodeValidator,
    ContextAnalyzer,
    KnowledgeManager,
    ProjectManager,
    QualityController,
    SocraticCounselor,
)


class LLMAgentError(Exception):
    """Raised when LLM client is required but not provided."""

    pass


class LLMPoweredCounselor:
    """
    Enhanced Socratic Counselor using LLM for intelligent questioning.

    Provides Socratic questioning with LLM-powered context awareness
    and personalization. Requires Socrates Nexus LLM client.

    Raises:
        LLMAgentError: If no LLM client is provided.

    Example:
        >>> from socrates_nexus import LLMClient
        >>> llm = LLMClient(provider="anthropic", model="claude-sonnet")
        >>> counselor = LLMPoweredCounselor(llm_client=llm)
        >>> result = counselor.guide_with_context(
        ...     topic="recursion",
        ...     level="beginner",
        ...     context="for someone new to programming"
        ... )
    """

    def __init__(self, llm_client: Any):
        """
        Initialize LLMPoweredCounselor.

        Args:
            llm_client: Socrates Nexus LLM client instance.

        Raises:
            LLMAgentError: If llm_client is None or not provided.
        """
        if not llm_client:
            raise LLMAgentError(
                "LLM client required for LLMPoweredCounselor. "
                "Install with: pip install socratic-agents[nexus]"
            )
        self.agent = SocraticCounselor(llm_client=llm_client)
        self.llm = llm_client

    def guide_with_context(
        self,
        topic: str,
        level: str = "beginner",
        context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate Socratic questions with additional context awareness.

        Uses LLM to create more nuanced and personalized questions
        based on the topic, level, and additional context provided.

        Args:
            topic: Subject to explore (e.g., "Python recursion")
            level: Difficulty level - "beginner", "intermediate", or "advanced"
            context: Additional context for tailored questions (optional)

        Returns:
            Dict containing:
                - questions: List of Socratic questions
                - llm_enhanced_questions: Additional LLM-generated questions
                - context_aware: True if context was used
                - llm_used: True to indicate LLM was used
                - level: The difficulty level used
                - topic: The topic explored
        """
        # Build enhanced prompt with context
        context_str = f"\nAdditional context: {context}" if context else ""
        prompt = (
            f"Generate Socratic questions for teaching {topic} at {level} level."
            f"{context_str}\n\n"
            f"Focus on:\n"
            f"1. Questions that build understanding progressively\n"
            f"2. Questions that reveal common misconceptions\n"
            f"3. Questions that connect to prior knowledge\n"
            f"4. Follow-up questions for deeper understanding"
        )

        try:
            response = self.llm.chat(prompt)
            llm_questions = (
                response.content if hasattr(response, "content") else str(response)
            )
        except Exception as e:
            llm_questions = f"[LLM generation failed: {e}]"

        # Get basic questions from agent
        basic_result = self.agent.process(
            {"action": "guide", "topic": topic, "level": level}
        )

        return {
            **basic_result,
            "llm_enhanced_questions": llm_questions,
            "context_aware": context is not None,
            "llm_used": True,
            "context": context,
        }

    def personalized_guide(
        self, topic: str, user_level: str, learning_style: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate questions personalized for learner's style and level.

        Args:
            topic: Subject to explore
            user_level: User's current understanding level
            learning_style: How user prefers to learn (e.g., "visual", "practical")

        Returns:
            Dict with personalized questions and guidance
        """
        style_context = (
            f"Learner style: {learning_style}"
            if learning_style
            else "Adapt to learner's needs"
        )
        return self.guide_with_context(topic, level=user_level, context=style_context)


class LLMPoweredCodeGenerator:
    """
    Enhanced Code Generator using LLM for production-quality code.

    Generates code with better error handling, testing considerations,
    and documentation. Requires Socrates Nexus LLM client.

    Raises:
        LLMAgentError: If no LLM client is provided.

    Example:
        >>> from socrates_nexus import LLMClient
        >>> llm = LLMClient(provider="anthropic", model="claude-sonnet")
        >>> generator = LLMPoweredCodeGenerator(llm_client=llm)
        >>> result = generator.generate_with_tests(
        ...     specification="Binary search tree with insert and search",
        ...     language="python"
        ... )
    """

    def __init__(self, llm_client: Any):
        """
        Initialize LLMPoweredCodeGenerator.

        Args:
            llm_client: Socrates Nexus LLM client instance.

        Raises:
            LLMAgentError: If llm_client is None or not provided.
        """
        if not llm_client:
            raise LLMAgentError(
                "LLM client required for LLMPoweredCodeGenerator. "
                "Install with: pip install socratic-agents[nexus]"
            )
        self.agent = CodeGenerator(llm_client=llm_client)
        self.llm = llm_client

    def generate_with_tests(
        self,
        specification: str,
        language: str = "python",
        include_docs: bool = True,
        include_error_handling: bool = True,
    ) -> Dict[str, Any]:
        """
        Generate code with tests and documentation.

        Creates production-ready code with comprehensive test coverage
        and documentation.

        Args:
            specification: What the code should do
            language: Programming language
            include_docs: Whether to include docstrings/comments
            include_error_handling: Whether to include error handling

        Returns:
            Dict containing:
                - code: Generated code
                - language: Programming language
                - has_tests: True
                - has_docs: Whether docs were included
                - has_error_handling: Whether error handling included
                - llm_generated: True
                - specification: Original specification
        """
        doc_instruction = (
            "\n- Include comprehensive docstrings and inline comments"
            if include_docs
            else ""
        )
        error_instruction = (
            "\n- Include proper error handling and edge case management"
            if include_error_handling
            else ""
        )

        prompt = (
            f"Generate {language} code for: {specification}\n\n"
            f"Requirements:\n"
            f"- Clean, readable code following best practices\n"
            f"- Include unit tests (at minimum 5 test cases)\n"
            f"{doc_instruction}"
            f"{error_instruction}"
            f"- Use type hints where applicable\n"
            f"- Make the code production-ready"
        )

        try:
            response = self.llm.chat(prompt)
            generated_code = (
                response.content if hasattr(response, "content") else str(response)
            )
        except Exception as e:
            generated_code = f"# Error generating code: {e}"

        return {
            "code": generated_code,
            "language": language,
            "has_tests": True,
            "has_docs": include_docs,
            "has_error_handling": include_error_handling,
            "llm_generated": True,
            "specification": specification,
        }

    def generate_with_explanation(
        self, specification: str, language: str = "python"
    ) -> Dict[str, Any]:
        """
        Generate code with detailed explanation of approach.

        Args:
            specification: What the code should do
            language: Programming language

        Returns:
            Dict with code and explanation
        """
        prompt = (
            f"Generate {language} code for: {specification}\n\n"
            f"Also provide:\n"
            f"1. A brief explanation of your approach\n"
            f"2. Key design decisions\n"
            f"3. Potential optimizations\n"
            f"4. Edge cases to consider"
        )

        try:
            response = self.llm.chat(prompt)
            response_text = (
                response.content if hasattr(response, "content") else str(response)
            )
        except Exception as e:
            response_text = f"Error: {e}"

        # Try to split code from explanation
        parts = response_text.split("\n\n")
        code = parts[0] if parts else response_text
        explanation = "\n\n".join(parts[1:]) if len(parts) > 1 else ""

        return {
            "code": code,
            "explanation": explanation,
            "language": language,
            "llm_generated": True,
            "specification": specification,
        }


class LLMPoweredCodeValidator:
    """
    Enhanced Code Validator using LLM for intelligent code review.

    Provides detailed code review with LLM insights beyond basic validation.
    Requires Socrates Nexus LLM client.

    Raises:
        LLMAgentError: If no LLM client is provided.
    """

    def __init__(self, llm_client: Any):
        """
        Initialize LLMPoweredCodeValidator.

        Args:
            llm_client: Socrates Nexus LLM client instance.

        Raises:
            LLMAgentError: If llm_client is None or not provided.
        """
        if not llm_client:
            raise LLMAgentError(
                "LLM client required for LLMPoweredCodeValidator. "
                "Install with: pip install socratic-agents[nexus]"
            )
        self.agent = CodeValidator(llm_client=llm_client)
        self.llm = llm_client

    def review_with_suggestions(
        self, code: str, language: str = "python", focus_areas: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive code review with improvement suggestions.

        Args:
            code: Code to review
            language: Programming language
            focus_areas: Specific areas to focus on (e.g., ["performance", "readability"])

        Returns:
            Dict with issues and improvement suggestions
        """
        focus_str = ""
        if focus_areas:
            focus_str = (
                f"\nFocus particularly on: {', '.join(focus_areas)}\n"
            )

        prompt = (
            f"Review this {language} code and provide:\n"
            f"1. List of issues found\n"
            f"2. Severity of each issue\n"
            f"3. Specific improvement suggestions\n"
            f"4. Refactoring recommendations\n"
            f"{focus_str}\n"
            f"Code:\n{code}"
        )

        try:
            response = self.llm.chat(prompt)
            review = response.content if hasattr(response, "content") else str(response)
        except Exception as e:
            review = f"Review failed: {e}"

        # Get basic validation
        basic_result = self.agent.process({"code": code, "language": language})

        return {
            **basic_result,
            "llm_review": review,
            "suggestions_provided": True,
            "focus_areas": focus_areas or [],
        }


class LLMPoweredProjectManager:
    """
    Enhanced Project Manager using LLM for intelligent planning.

    Provides project breakdown, task prioritization, risk assessment,
    and timeline estimation using LLM capabilities.

    Raises:
        LLMAgentError: If no LLM client is provided.
    """

    def __init__(self, llm_client: Any):
        """
        Initialize LLMPoweredProjectManager.

        Args:
            llm_client: Socrates Nexus LLM client instance.

        Raises:
            LLMAgentError: If llm_client is None or not provided.
        """
        if not llm_client:
            raise LLMAgentError(
                "LLM client required for LLMPoweredProjectManager. "
                "Install with: pip install socratic-agents[nexus]"
            )
        self.agent = ProjectManager(llm_client=llm_client)
        self.llm = llm_client

    def intelligent_project_breakdown(
        self,
        project_description: str,
        context: Optional[str] = None,
        include_timeline: bool = True,
    ) -> Dict[str, Any]:
        """
        Break down project into detailed tasks with dependencies.

        Args:
            project_description: High-level project description
            context: Additional context (team size, constraints, etc.)
            include_timeline: Whether to estimate timeline

        Returns:
            Dict with tasks, dependencies, milestones, and timeline
        """
        context_str = f"\nContext: {context}" if context else ""
        timeline_str = "\n- Estimated timeline for each task" if include_timeline else ""

        prompt = (
            f"Break down this project into detailed tasks:\n\n"
            f"{project_description}"
            f"{context_str}\n\n"
            f"Provide:\n"
            f"- List of specific, actionable tasks\n"
            f"- Dependencies between tasks\n"
            f"- Suggested priority/order\n"
            f"- Key milestones\n"
            f"{timeline_str}"
        )

        try:
            response = self.llm.chat(prompt)
            breakdown = (
                response.content if hasattr(response, "content") else str(response)
            )
        except Exception as e:
            breakdown = f"[Project breakdown failed: {e}]"

        return {
            "project_description": project_description,
            "task_breakdown": breakdown,
            "llm_generated": True,
            "includes_timeline": include_timeline,
        }

    def analyze_project_risks(
        self, project_id: str, tasks: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Analyze project for risks and challenges.

        Args:
            project_id: Project identifier
            tasks: List of tasks (optional, can load from project)

        Returns:
            Dict with identified risks, severity, and mitigation strategies
        """
        tasks_str = "\n".join(
            [f"- {task.get('description', task)}" for task in (tasks or [])]
        )

        prompt = (
            f"Analyze this project for risks and challenges:\n\n"
            f"Project ID: {project_id}\n"
            f"Tasks:\n{tasks_str}\n\n"
            f"Identify:\n"
            f"- Technical risks\n"
            f"- Resource constraints\n"
            f"- Dependency risks\n"
            f"- Timeline risks\n"
            f"- Mitigation strategies for each risk"
        )

        try:
            response = self.llm.chat(prompt)
            risk_analysis = (
                response.content if hasattr(response, "content") else str(response)
            )
        except Exception as e:
            risk_analysis = f"[Risk analysis failed: {e}]"

        return {
            "project_id": project_id,
            "risk_analysis": risk_analysis,
            "llm_generated": True,
        }


class LLMPoweredQualityController:
    """
    Enhanced Quality Controller using LLM for deep code review.

    Provides comprehensive code analysis, security assessment,
    and actionable improvement suggestions.

    Raises:
        LLMAgentError: If no LLM client is provided.
    """

    def __init__(self, llm_client: Any):
        """
        Initialize LLMPoweredQualityController.

        Args:
            llm_client: Socrates Nexus LLM client instance.

        Raises:
            LLMAgentError: If llm_client is None or not provided.
        """
        if not llm_client:
            raise LLMAgentError(
                "LLM client required for LLMPoweredQualityController. "
                "Install with: pip install socratic-agents[nexus]"
            )
        self.agent = QualityController(llm_client=llm_client)
        self.llm = llm_client

    def deep_code_review(
        self,
        code: str,
        language: str = "python",
        focus_areas: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Perform comprehensive code review with LLM insights.

        Args:
            code: Code to review
            language: Programming language
            focus_areas: Areas to focus on (e.g., ["performance", "security"])

        Returns:
            Dict with detailed review, issues, and suggestions
        """
        focus_str = ""
        if focus_areas:
            focus_str = f"\nFocus particularly on: {', '.join(focus_areas)}"

        prompt = (
            f"Perform a comprehensive code review of this {language} code:\n\n"
            f"```{language}\n{code}\n```\n\n"
            f"Analyze:\n"
            f"1. Code quality and readability\n"
            f"2. Potential bugs and edge cases\n"
            f"3. Performance considerations\n"
            f"4. Security vulnerabilities\n"
            f"5. Best practice violations\n"
            f"6. Specific improvement suggestions\n"
            f"{focus_str}"
        )

        try:
            response = self.llm.chat(prompt)
            review = response.content if hasattr(response, "content") else str(response)
        except Exception as e:
            review = f"[Review failed: {e}]"

        basic_result = self.agent.process(
            {"action": "detect_weak_areas", "code": code}
        )

        return {
            **basic_result,
            "deep_review": review,
            "focus_areas": focus_areas or [],
            "llm_enhanced": True,
        }

    def suggest_refactoring(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Suggest refactoring opportunities with examples.

        Args:
            code: Code to analyze
            language: Programming language

        Returns:
            Dict with refactoring suggestions and example code
        """
        prompt = (
            f"Analyze this {language} code for refactoring opportunities:\n\n"
            f"```{language}\n{code}\n```\n\n"
            f"Provide:\n"
            f"1. Specific refactoring opportunities\n"
            f"2. Expected benefits of each refactoring\n"
            f"3. Example code showing the refactored version\n"
            f"4. Priority/impact of each suggestion"
        )

        try:
            response = self.llm.chat(prompt)
            suggestions = (
                response.content if hasattr(response, "content") else str(response)
            )
        except Exception as e:
            suggestions = f"[Refactoring analysis failed: {e}]"

        return {
            "code": code,
            "language": language,
            "refactoring_suggestions": suggestions,
            "llm_generated": True,
        }


class LLMPoweredKnowledgeManager:
    """
    Enhanced Knowledge Manager using LLM for semantic search and extraction.

    Provides intelligent document search, summarization, question answering,
    and knowledge graph construction.

    Raises:
        LLMAgentError: If no LLM client is provided.
    """

    def __init__(self, llm_client: Any):
        """
        Initialize LLMPoweredKnowledgeManager.

        Args:
            llm_client: Socrates Nexus LLM client instance.

        Raises:
            LLMAgentError: If llm_client is None or not provided.
        """
        if not llm_client:
            raise LLMAgentError(
                "LLM client required for LLMPoweredKnowledgeManager. "
                "Install with: pip install socratic-agents[nexus]"
            )
        self.agent = KnowledgeManager(llm_client=llm_client)
        self.llm = llm_client

    def semantic_search(
        self, query: str, top_k: int = 5, context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search knowledge base using semantic understanding.

        Args:
            query: Search query
            top_k: Number of results to return
            context: Additional context for search

        Returns:
            Dict with semantically relevant documents
        """
        basic_results = self.agent.process({"action": "search", "query": query})

        documents = basic_results.get("documents", [])

        if not documents:
            return {
                "query": query,
                "documents": [],
                "semantic_results": "No documents found",
            }

        docs_str = "\n\n".join(
            [
                f"Document {i+1}:\n{doc.get('content', '')[:200]}..."
                for i, doc in enumerate(documents[:10])
            ]
        )

        context_str = f"\nContext: {context}" if context else ""

        prompt = (
            f"Rank these documents by relevance to the query: '{query}'"
            f"{context_str}\n\n"
            f"{docs_str}\n\n"
            f"Provide:\n"
            f"1. Top {top_k} most relevant documents\n"
            f"2. Relevance explanation for each\n"
            f"3. Key passages that match the query"
        )

        try:
            response = self.llm.chat(prompt)
            semantic_ranking = (
                response.content if hasattr(response, "content") else str(response)
            )
        except Exception as e:
            semantic_ranking = f"[Semantic search failed: {e}]"

        return {
            "query": query,
            "documents": documents[:top_k],
            "semantic_results": semantic_ranking,
            "llm_enhanced": True,
        }

    def answer_question(
        self, question: str, document_scope: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Answer question by synthesizing information from documents.

        Args:
            question: Question to answer
            document_scope: Specific document IDs to search (optional)

        Returns:
            Dict with answer, sources, and confidence
        """
        search_results = self.semantic_search(query=question, top_k=5)
        documents = search_results.get("documents", [])

        if not documents:
            return {
                "question": question,
                "answer": "No relevant documents found to answer this question.",
                "sources": [],
                "confidence": "low",
            }

        context = "\n\n".join(
            [
                f"Source {i+1}:\n{doc.get('content', '')[:300]}..."
                for i, doc in enumerate(documents)
            ]
        )

        prompt = (
            f"Answer this question based on the provided sources:\n\n"
            f"Question: {question}\n\n"
            f"Sources:\n{context}\n\n"
            f"Provide:\n"
            f"1. A clear, concise answer\n"
            f"2. Which sources support the answer\n"
            f"3. Confidence level (high/medium/low)\n"
            f"4. Any caveats or limitations"
        )

        try:
            response = self.llm.chat(prompt)
            answer = response.content if hasattr(response, "content") else str(response)
        except Exception as e:
            answer = f"[Question answering failed: {e}]"

        return {
            "question": question,
            "answer": answer,
            "sources": [doc.get("metadata", {}) for doc in documents],
            "llm_generated": True,
        }


class LLMPoweredContextAnalyzer:
    """
    Enhanced Context Analyzer using LLM for deep understanding.

    Provides intent recognition, context enrichment, and
    intelligent recommendations based on context.

    Raises:
        LLMAgentError: If no LLM client is provided.
    """

    def __init__(self, llm_client: Any):
        """
        Initialize LLMPoweredContextAnalyzer.

        Args:
            llm_client: Socrates Nexus LLM client instance.

        Raises:
            LLMAgentError: If llm_client is None or not provided.
        """
        if not llm_client:
            raise LLMAgentError(
                "LLM client required for LLMPoweredContextAnalyzer. "
                "Install with: pip install socratic-agents[nexus]"
            )
        self.agent = ContextAnalyzer(llm_client=llm_client)
        self.llm = llm_client

    def deep_context_analysis(
        self,
        content: str,
        include_entities: bool = True,
        include_sentiment: bool = False,
    ) -> Dict[str, Any]:
        """
        Perform deep analysis of context.

        Args:
            content: Content to analyze
            include_entities: Extract entities (people, places, concepts)
            include_sentiment: Analyze sentiment/tone

        Returns:
            Dict with comprehensive context analysis
        """
        analysis_items = [
            "- Main topics and themes",
            "- Key concepts and terminology",
            "- Implied goals or objectives",
            "- Technical level and domain",
        ]

        if include_entities:
            analysis_items.append(
                "- Named entities (people, places, organizations, concepts)"
            )

        if include_sentiment:
            analysis_items.append("- Tone and sentiment")

        analysis_str = "\n".join(analysis_items)

        prompt = (
            f"Analyze this content in depth:\n\n"
            f"{content}\n\n"
            f"Provide:\n"
            f"{analysis_str}"
        )

        try:
            response = self.llm.chat(prompt)
            analysis = response.content if hasattr(response, "content") else str(response)
        except Exception as e:
            analysis = f"[Context analysis failed: {e}]"

        basic_result = self.agent.process({"action": "analyze", "content": content})

        return {
            **basic_result,
            "deep_analysis": analysis,
            "entities_extracted": include_entities,
            "sentiment_analyzed": include_sentiment,
            "llm_enhanced": True,
        }

    def detect_intent(
        self, content: str, user_history: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Detect user's intent from content and history.

        Args:
            content: Current user content
            user_history: Previous interactions (optional)

        Returns:
            Dict with detected intent, confidence, and suggested actions
        """
        history_str = ""
        if user_history:
            history_str = "\n\nPrevious interactions:\n" + "\n".join(
                [f"- {item.get('summary', str(item))}" for item in user_history[-5:]]
            )

        prompt = (
            f"Analyze the user's intent from this content:\n\n"
            f"{content}"
            f"{history_str}\n\n"
            f"Determine:\n"
            f"1. Primary intent (what does the user want to accomplish?)\n"
            f"2. Secondary intents or sub-goals\n"
            f"3. Confidence level in this assessment\n"
            f"4. Suggested actions to fulfill the intent"
        )

        try:
            response = self.llm.chat(prompt)
            intent_analysis = (
                response.content if hasattr(response, "content") else str(response)
            )
        except Exception as e:
            intent_analysis = f"[Intent detection failed: {e}]"

        return {
            "content": content,
            "intent_analysis": intent_analysis,
            "history_considered": user_history is not None,
            "llm_generated": True,
        }

    def recommend_next_actions(
        self,
        current_context: str,
        available_actions: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Recommend next actions based on context.

        Args:
            current_context: Current situation/context
            available_actions: List of possible actions (optional)

        Returns:
            Dict with recommended actions, reasoning, and priorities
        """
        actions_str = ""
        if available_actions:
            actions_str = "\n\nAvailable actions:\n" + "\n".join(
                [f"- {action}" for action in available_actions]
            )

        prompt = (
            f"Based on this context, recommend the best next actions:\n\n"
            f"Context: {current_context}"
            f"{actions_str}\n\n"
            f"Provide:\n"
            f"1. Top 3 recommended actions\n"
            f"2. Reasoning for each recommendation\n"
            f"3. Priority/urgency level\n"
            f"4. Expected outcomes"
        )

        try:
            response = self.llm.chat(prompt)
            recommendations = (
                response.content if hasattr(response, "content") else str(response)
            )
        except Exception as e:
            recommendations = f"[Recommendation generation failed: {e}]"

        return {
            "context": current_context,
            "recommendations": recommendations,
            "available_actions": available_actions or [],
            "llm_generated": True,
        }


# Export wrapper classes and error
__all__ = [
    "LLMPoweredCounselor",
    "LLMPoweredCodeGenerator",
    "LLMPoweredCodeValidator",
    "LLMPoweredProjectManager",
    "LLMPoweredQualityController",
    "LLMPoweredKnowledgeManager",
    "LLMPoweredContextAnalyzer",
    "LLMAgentError",
]
