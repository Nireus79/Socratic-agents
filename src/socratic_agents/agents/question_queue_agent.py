"""Question Queue Agent - Question queuing and prioritization."""

from typing import Any, Dict, Optional, List
from .base import BaseAgent


class QuestionQueueAgent(BaseAgent):
    """Agent that queues and prioritizes questions."""

    def __init__(self, llm_client: Optional[Any] = None):
        """Initialize the Question Queue Agent."""
        super().__init__(name="QuestionQueueAgent", llm_client=llm_client)
        self.queue: List[Dict[str, Any]] = []
        self.processed: List[Dict[str, Any]] = []

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process question queue requests."""
        action = request.get("action", "add")
        if action == "add":
            return self.add_question(request.get("question"), request.get("priority", "normal"))
        elif action == "next":
            return self.get_next_question()
        elif action == "process":
            return self.process_question(request.get("question_id"))
        elif action == "list":
            return self.list_queue()
        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    def add_question(self, question: str, priority: str = "normal") -> Dict[str, Any]:
        """Add a question to the queue."""
        if not question:
            return {"status": "error", "message": "Question required"}
        q_id = f"q_{len(self.queue) + 1}"
        q_obj = {"id": q_id, "question": question, "priority": priority, "status": "queued"}
        self.queue.append(q_obj)
        self.queue.sort(key=lambda x: {"high": 0, "normal": 1, "low": 2}.get(x["priority"], 1))
        return {
            "status": "success",
            "agent": self.name,
            "question_id": q_id,
            "queue_size": len(self.queue),
        }

    def get_next_question(self) -> Dict[str, Any]:
        """Get the next question to process."""
        if not self.queue:
            return {"status": "success", "agent": self.name, "message": "Queue is empty"}
        return {"status": "success", "agent": self.name, "next_question": self.queue[0]}

    def process_question(self, question_id: str) -> Dict[str, Any]:
        """Process a question."""
        if not question_id:
            return {"status": "error", "message": "Question ID required"}
        q_obj = next((q for q in self.queue if q["id"] == question_id), None)
        if not q_obj:
            return {"status": "error", "message": f"Question {question_id} not found"}
        self.queue.remove(q_obj)
        q_obj["status"] = "processed"
        self.processed.append(q_obj)
        return {
            "status": "success",
            "agent": self.name,
            "question_id": question_id,
            "processed": True,
        }

    def list_queue(self) -> Dict[str, Any]:
        """List the question queue."""
        return {
            "status": "success",
            "agent": self.name,
            "queued": len(self.queue),
            "processed": len(self.processed),
            "queue": self.queue,
        }
