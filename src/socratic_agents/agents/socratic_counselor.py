"""Socratic Counselor Agent - Guided learning through questioning."""

from typing import Any, Dict, Optional

from .base import BaseAgent


class SocraticCounselor(BaseAgent):
    """
    Agent that guides learning through Socratic questioning.

    Helps users understand concepts by asking guiding questions
    rather than providing direct answers.
    """

    def __init__(self, llm_client: Optional[Any] = None):
        """Initialize the Socratic Counselor."""
        super().__init__(name="SocraticCounselor", llm_client=llm_client)

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a learning request through Socratic questioning."""
        topic = request.get("topic", "")
        level = request.get("level", "beginner")

        if not topic:
            return {"status": "error", "message": "Topic required"}

        # Generate questions to guide learning
        questions = self._generate_guiding_questions(topic, level)

        return {
            "status": "success",
            "agent": self.name,
            "topic": topic,
            "level": level,
            "questions": questions,
        }

    def guide(self, topic: str, level: str = "beginner") -> Dict[str, Any]:
        """
        Guide learning on a topic through questioning.

        Args:
            topic: The topic to learn about
            level: Learning level (beginner, intermediate, advanced)

        Returns:
            Dictionary with guiding questions
        """
        return self.process({"topic": topic, "level": level})

    def _generate_guiding_questions(self, topic: str, level: str) -> list[str]:
        """Generate Socratic questions for a topic using LLM if available."""
        # If an LLM client is available, use it to generate dynamic questions
        if self.llm_client:
            try:
                prompt = f"""Generate 3 Socratic questions to guide learning about "{topic}" at the {level} level.
Focus on asking questions that help the learner discover answers themselves rather than providing direct information.
Return only the questions, one per line."""

                response = self.llm_client.generate_response(prompt)
                if response:
                    questions = [q.strip() for q in response.split("\n") if q.strip()]
                    if questions:
                        return questions
            except Exception as e:
                self.logger.warning(f"Failed to generate questions using LLM: {e}")

        # Fallback to static questions if LLM is unavailable or fails
        default_questions: Dict[str, list[str]] = {
            "beginner": [
                f"What do you already know about {topic}?",
                f"What aspects of {topic} interest you most?",
                f"How would you explain {topic} to someone else?",
            ],
            "intermediate": [
                f"How does {topic} relate to what you already know?",
                f"What are the key principles behind {topic}?",
                f"What would happen if you applied {topic} to a different context?",
            ],
            "advanced": [
                f"What are the limitations of {topic}?",
                f"How could {topic} be improved or extended?",
                f"What are the connections between {topic} and related concepts?",
            ],
        }
        return default_questions.get(level, default_questions["beginner"])
