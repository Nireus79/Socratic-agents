"""Socratic Counselor Agent - Guided learning through questioning."""

from typing import Any, Dict, Optional

from .base import BaseAgent


class SocraticCounselor(BaseAgent):
    """
    Agent that guides learning through Socratic questioning.

    Helps users understand concepts by asking guiding questions
    rather than providing direct answers.

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
        Process a learning request through Socratic questioning.

        Args:
            request: Dictionary with 'topic', 'level', and optional 'batch_size'

        Returns:
            Dictionary with status, topic, level, and generated questions
        """
        topic = request.get("topic", "")
        level = request.get("level", "beginner")
        batch_size = request.get("batch_size", self.batch_size)

        if not topic:
            return {"status": "error", "message": "Topic required"}

        # Generate questions to guide learning
        questions = self._generate_guiding_questions(topic, level, batch_size)

        return {
            "status": "success",
            "agent": self.name,
            "topic": topic,
            "level": level,
            "batch_size": batch_size,
            "questions": questions,
        }

    def guide(
        self, topic: str, level: str = "beginner", batch_size: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Guide learning on a topic through questioning.

        Args:
            topic: The topic to learn about
            level: Learning level (beginner, intermediate, advanced)
            batch_size: Number of questions to generate (optional, uses instance default)

        Returns:
            Dictionary with guiding questions
        """
        if batch_size is None:
            batch_size = self.batch_size

        return self.process({"topic": topic, "level": level, "batch_size": batch_size})

    def _generate_guiding_questions(self, topic: str, level: str, batch_size: int = 1) -> list[str]:
        """
        Generate Socratic questions for a topic using LLM if available.

        Args:
            topic: The topic to generate questions about
            level: Learning level (beginner, intermediate, advanced)
            batch_size: Number of questions to generate

        Returns:
            List of Socratic questions
        """
        # Ensure batch_size is at least 1
        batch_size = max(1, batch_size)

        # If an LLM client is available, use it to generate dynamic questions
        if self.llm_client:
            try:
                # Use grammatically correct singular/plural
                question_word = "question" if batch_size == 1 else "questions"
                prompt = f"""Generate {batch_size} Socratic {question_word} to guide learning about "{topic}" at the {level} level.
Focus on asking questions that help the learner discover answers themselves rather than providing direct information.
Return only the questions, one per line."""

                response = self.llm_client.generate_response(prompt)
                if response:
                    questions = [q.strip() for q in response.split("\n") if q.strip()]
                    if questions:
                        # Return requested batch size (truncate if LLM generated too many)
                        return questions[:batch_size]
            except Exception as e:
                self.logger.warning(f"Failed to generate questions using LLM: {e}")

        # Fallback to static questions if LLM is unavailable or fails
        default_questions: Dict[str, list[str]] = {
            "beginner": [
                f"What do you already know about {topic}?",
                f"What aspects of {topic} interest you most?",
                f"How would you explain {topic} to someone else?",
                f"Why do you think {topic} is important?",
                f"Can you think of a real-world example of {topic}?",
            ],
            "intermediate": [
                f"How does {topic} relate to what you already know?",
                f"What are the key principles behind {topic}?",
                f"What would happen if you applied {topic} to a different context?",
                f"Can you identify the strengths and weaknesses of {topic}?",
                f"How has your understanding of {topic} evolved?",
            ],
            "advanced": [
                f"What are the limitations of {topic}?",
                f"How could {topic} be improved or extended?",
                f"What are the connections between {topic} and related concepts?",
                f"What are the underlying assumptions in {topic}?",
                f"How would you critically evaluate {topic} in practice?",
            ],
        }

        # Get default questions for the level
        level_questions = default_questions.get(level, default_questions["beginner"])

        # Return requested batch size
        return level_questions[:batch_size]
