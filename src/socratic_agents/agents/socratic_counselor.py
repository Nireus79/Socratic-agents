"""Socratic Counselor Agent - Guided learning through questioning with knowledge base awareness."""

from typing import Any, Dict, List, Optional

from .base import BaseAgent


class SocraticCounselor(BaseAgent):
    """
    Agent that guides learning through Socratic questioning.

    Helps users understand concepts by asking guiding questions
    rather than providing direct answers.

    Enhanced with knowledge base awareness:
    - Uses document chunks to ground questions in project context
    - Addresses identified knowledge gaps
    - Avoids repeating previously asked questions
    - Incorporates document understanding and project phase information
    - Generates context-aware, specific questions instead of generic ones

    Supports configurable batch sizes for question generation,
    allowing single questions (batch_size=1) or multiple questions
    (batch_size=3, 5, etc.) per request.
    """

    def __init__(self, llm_client: Optional[Any] = None, batch_size: int = 1):
        """
        Initialize the Socratic Counselor.

        Args:
            llm_client: Optional LLM client for dynamic question generation
            batch_size: Number of questions to generate per request (default: 1)
                       Set to 3 for legacy behavior (3 questions per call)
        """
        super().__init__(name="SocraticCounselor", llm_client=llm_client)
        self.batch_size = max(1, batch_size)  # Ensure batch_size is at least 1

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a learning request through Socratic questioning with KB awareness.

        Args:
            request: Dictionary with:
                - 'topic': Learning topic (required)
                - 'level': Learning level (optional, default: beginner)
                - 'batch_size': Number of questions (optional, uses instance default)
                - 'phase': Project phase (optional: discovery, analysis, design, implementation)
                - 'knowledge_base': KB context dict with chunks, gaps, coverage (optional)
                - 'document_understanding': Document analysis data (optional)
                - 'context': Conversation context (optional)
                - 'recently_asked': Previously asked questions to avoid repetition (optional)
                - 'conversation_history': Full conversation history (optional)

        Returns:
            Dictionary with status, topic, and generated question(s)
        """
        topic = request.get("topic", "")
        level = request.get("level", "beginner")
        batch_size = request.get("batch_size", self.batch_size)
        phase = request.get("phase", "discovery")
        kb_context = request.get("knowledge_base", {})
        doc_understanding = request.get("document_understanding", {})
        conversation_context = request.get("context", "")
        recently_asked = request.get("recently_asked", [])
        conversation_history = request.get("conversation_history", [])

        if not topic:
            return {"status": "error", "message": "Topic required"}

        # Generate questions to guide learning (now KB-aware)
        question = self._generate_guiding_question(
            topic=topic,
            level=level,
            phase=phase,
            kb_context=kb_context,
            doc_understanding=doc_understanding,
            conversation_context=conversation_context,
            recently_asked=recently_asked,
            conversation_history=conversation_history,
        )

        return {
            "status": "success",
            "agent": self.name,
            "topic": topic,
            "level": level,
            "phase": phase,
            "question": question,  # Single question as primary response
            "kb_coverage": kb_context.get("coverage", 0) if kb_context else 0,
        }

    def guide(
        self,
        topic: str,
        level: str = "beginner",
        batch_size: Optional[int] = None,
        phase: Optional[str] = None,
        kb_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Guide learning on a topic through questioning with optional KB context.

        Args:
            topic: The topic to learn about
            level: Learning level (beginner, intermediate, advanced)
            batch_size: Number of questions to generate (optional, uses instance default)
            phase: Project phase (discovery, analysis, design, implementation)
            kb_context: Knowledge base context with chunks and gaps

        Returns:
            Dictionary with guiding question(s)
        """
        if batch_size is None:
            batch_size = self.batch_size

        request = {
            "topic": topic,
            "level": level,
            "batch_size": batch_size,
        }

        if phase:
            request["phase"] = phase
        if kb_context:
            request["knowledge_base"] = kb_context

        return self.process(request)

    def _generate_guiding_question(
        self,
        topic: str,
        level: str,
        phase: str = "discovery",
        kb_context: Optional[Dict[str, Any]] = None,
        doc_understanding: Optional[Dict[str, Any]] = None,
        conversation_context: str = "",
        recently_asked: Optional[List[str]] = None,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """
        Generate a Socratic question for a topic using KB-aware context.

        Prioritizes using KB context to ground questions in the project,
        falling back to generic questions if KB context unavailable.

        Args:
            topic: The topic to generate a question about
            level: Learning level (beginner, intermediate, advanced)
            phase: Project phase (discovery, analysis, design, implementation)
            kb_context: Dict with chunks, gaps, coverage from knowledge base
            doc_understanding: Document analysis data
            conversation_context: Summary of conversation so far
            recently_asked: List of previously asked questions to avoid
            conversation_history: Full conversation history

        Returns:
            A single Socratic question string
        """
        recently_asked = recently_asked or []

        # If knowledge base context is available, use it to generate KB-aware questions
        if kb_context and kb_context.get("chunks"):
            kb_aware_question = self._generate_kb_aware_question(
                topic=topic,
                level=level,
                phase=phase,
                kb_context=kb_context,
                doc_understanding=doc_understanding,
                conversation_context=conversation_context,
                recently_asked=recently_asked,
            )
            if kb_aware_question:
                return kb_aware_question

        # Fallback to LLM or static questions if KB not available
        if self.llm_client:
            return self._generate_llm_question(topic, level, phase, recently_asked)

        # Fallback to static questions
        return self._get_fallback_question(topic, level, phase)

    def _generate_kb_aware_question(
        self,
        topic: str,
        level: str,
        phase: str,
        kb_context: Dict[str, Any],
        doc_understanding: Optional[Dict[str, Any]] = None,
        conversation_context: str = "",
        recently_asked: Optional[List[str]] = None,
    ) -> Optional[str]:
        """
        Generate a question that leverages KB chunks and gaps.

        Uses document chunks to ground the question in project-specific context,
        and prioritizes gaps that need to be filled.

        Args:
            topic: Main topic
            level: Learning level
            phase: Project phase
            kb_context: KB context with chunks, gaps, coverage
            doc_understanding: Document analysis
            conversation_context: Conversation summary
            recently_asked: Questions to avoid

        Returns:
            A KB-aware question string, or None to fall back
        """
        recently_asked = recently_asked or []

        if not self.llm_client:
            return None

        try:
            # Build KB context for the prompt
            chunks = kb_context.get("chunks", [])
            gaps = kb_context.get("gaps", [])
            coverage = kb_context.get("coverage", 0)

            # Get snippets from chunks for context
            chunk_snippets = []
            if chunks:
                for chunk in chunks[:3]:  # Use top 3 chunks
                    if isinstance(chunk, dict):
                        chunk_snippets.append(chunk.get("content", str(chunk))[:200])
                    else:
                        chunk_snippets.append(str(chunk)[:200])

            # Build the enhanced prompt
            chunks_context = "\n".join(
                [f"- {s}" for s in chunk_snippets]
            ) if chunk_snippets else "No document context available"

            gaps_context = ""
            if gaps:
                gap_list = []
                for gap in gaps[:3]:
                    if isinstance(gap, dict):
                        gap_list.append(gap.get("topic", str(gap)))
                    else:
                        gap_list.append(str(gap))
                gaps_context = f"\nIdentified knowledge gaps to address: {', '.join(gap_list)}"

            # Phase-specific guidance
            phase_guidance = {
                "discovery": "Focus on understanding the overall project scope and goals",
                "analysis": "Focus on analyzing requirements and system design",
                "design": "Focus on architectural decisions and design patterns",
                "implementation": "Focus on implementation details and technical challenges",
            }
            phase_hint = phase_guidance.get(phase, "")

            prompt = f"""Generate ONE Socratic question to guide learning about "{topic}" at the {level} level.

Project Phase: {phase}
{phase_hint}

Available Project Context:
{chunks_context}
{gaps_context}

Conversation Context: {conversation_context if conversation_context else "Starting fresh"}

Question Guidelines:
- Ground the question in the specific project context provided above
- Help the learner discover insights themselves rather than providing answers
- Consider the current project phase when asking
- Make it specific to the project, not generic
- If gaps were identified, consider questions that help close them

Generate ONE question only. Return only the question text, nothing else."""

            # Add recently asked avoidance if available
            if recently_asked:
                prompt += f"\n\nDo NOT ask these previously asked questions:\n" + "\n".join(
                    [f"- {q}" for q in recently_asked[:5]]
                )

            response = self.llm_client.generate_response(prompt)
            if response:
                question = response.strip()
                if question and not any(q.strip().lower() == question.lower() for q in recently_asked):
                    return question

        except Exception as e:
            self.logger.warning(f"Failed to generate KB-aware question: {e}")

        return None

    def _generate_llm_question(
        self, topic: str, level: str, phase: str, recently_asked: Optional[List[str]] = None
    ) -> str:
        """
        Generate a phase-aware question using LLM.

        Args:
            topic: The topic
            level: Learning level
            phase: Project phase
            recently_asked: Questions to avoid

        Returns:
            A question string
        """
        recently_asked = recently_asked or []

        try:
            prompt = f"""Generate ONE Socratic question about "{topic}" at the {level} level for the {phase} phase.
Focus on asking questions that help the learner discover answers themselves.
Return only the question text, nothing else."""

            if recently_asked:
                prompt += f"\n\nDo NOT ask:\n" + "\n".join([f"- {q}" for q in recently_asked[:3]])

            response = self.llm_client.generate_response(prompt)
            if response:
                question = response.strip()
                if question:
                    return question
        except Exception as e:
            self.logger.warning(f"Failed to generate LLM question: {e}")

        # Fallback
        return self._get_fallback_question(topic, level, phase)

    def _get_fallback_question(self, topic: str, level: str, phase: str) -> str:
        """
        Get a fallback question when LLM unavailable.

        Args:
            topic: The topic
            level: Learning level
            phase: Project phase

        Returns:
            A generic but appropriate question
        """
        # Phase-specific fallback questions
        phase_questions: Dict[str, Dict[str, List[str]]] = {
            "discovery": {
                "beginner": [
                    f"What is the main purpose of {topic} in your project?",
                    f"Who are the primary users of {topic}?",
                    f"What problem does {topic} solve?",
                ],
                "intermediate": [
                    f"How does {topic} fit into the overall project scope?",
                    f"What are the key stakeholders for {topic}?",
                    f"What success criteria would define {topic}?",
                ],
                "advanced": [
                    f"What are the strategic implications of {topic}?",
                    f"How does {topic} differentiate this project?",
                    f"What market needs drive {topic}?",
                ],
            },
            "analysis": {
                "beginner": [
                    f"What are the main requirements for {topic}?",
                    f"What constraints apply to {topic}?",
                    f"How should {topic} be measured or evaluated?",
                ],
                "intermediate": [
                    f"How do the requirements for {topic} interact?",
                    f"What trade-offs exist in {topic}?",
                    f"What dependencies affect {topic}?",
                ],
                "advanced": [
                    f"What risks should be analyzed for {topic}?",
                    f"How scalable is {topic} for future growth?",
                    f"What are the failure modes of {topic}?",
                ],
            },
            "design": {
                "beginner": [
                    f"How would you structure {topic}?",
                    f"What components does {topic} need?",
                    f"What interfaces should {topic} expose?",
                ],
                "intermediate": [
                    f"What design patterns apply to {topic}?",
                    f"How would {topic} handle concurrency?",
                    f"What data structures would {topic} use?",
                ],
                "advanced": [
                    f"What architectural patterns suit {topic}?",
                    f"How would {topic} scale horizontally?",
                    f"What are the performance constraints on {topic}?",
                ],
            },
            "implementation": {
                "beginner": [
                    f"What's the first step to implement {topic}?",
                    f"What tools would you use for {topic}?",
                    f"How would you test {topic}?",
                ],
                "intermediate": [
                    f"What edge cases must {topic} handle?",
                    f"How would you optimize {topic}?",
                    f"What error handling does {topic} need?",
                ],
                "advanced": [
                    f"How would you monitor {topic} in production?",
                    f"What refactoring opportunities exist in {topic}?",
                    f"How would you version and deprecate {topic}?",
                ],
            },
        }

        # Get phase-level questions
        phase_q = phase_questions.get(phase, phase_questions["discovery"])
        level_questions = phase_q.get(level, phase_q.get("beginner", []))

        return level_questions[0] if level_questions else f"Tell me more about {topic}."
