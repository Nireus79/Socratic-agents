"""Question Queue Agent - Question queuing, prioritization, and distribution.

This agent:
1. Manages question queue for Socratic dialogue
2. Prioritizes questions by importance and urgency
3. Routes questions to appropriate agents
4. Tracks question status and lifecycle
5. Manages question dependencies and sequencing
6. Handles question batching and distribution
7. Provides queue analytics and reporting
8. Supports question filtering and search
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, cast

from .base import BaseAgent


class QuestionPriority(Enum):
    """Question priority levels."""

    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3


class QuestionStatus(Enum):
    """Question lifecycle status."""

    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    ANSWERED = "answered"
    REVIEWED = "reviewed"
    ARCHIVED = "archived"


class Question:
    """Represents a question in the queue."""

    def __init__(self, text: str, priority: str = "normal", category: str = "general"):
        self.id = f"q_{datetime.utcnow().timestamp()}"
        self.text = text
        self.priority = self._parse_priority(priority)
        self.category = category
        self.status = QuestionStatus.PENDING
        self.created_at = datetime.utcnow()
        self.assigned_to: Optional[str] = None
        self.answer: Optional[str] = None
        self.answered_at: Optional[datetime] = None
        self.dependencies: Set[str] = set()
        self.related_questions: Set[str] = set()
        self.attempts = 0
        self.max_attempts = 3

    def _parse_priority(self, priority: str) -> QuestionPriority:
        """Parse priority string to enum."""
        priority_map = {
            "critical": QuestionPriority.CRITICAL,
            "high": QuestionPriority.HIGH,
            "normal": QuestionPriority.NORMAL,
            "low": QuestionPriority.LOW,
        }
        return priority_map.get(priority.lower(), QuestionPriority.NORMAL)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "text": self.text,
            "priority": self.priority.name.lower(),
            "category": self.category,
            "status": self.status.value,
            "assigned_to": self.assigned_to,
            "created_at": self.created_at.isoformat(),
            "answered_at": self.answered_at.isoformat() if self.answered_at else None,
        }


class QuestionQueueAgent(BaseAgent):
    """
    Agent that manages question queues for Socratic dialogue.

    Provides:
    - Question queue management (FIFO with priority)
    - Priority-based ordering and assignment
    - Question status tracking and lifecycle
    - Question dependency management
    - Queue routing and distribution
    - Analytics and reporting
    - Batch processing support
    - Question filtering and search
    """

    def __init__(self, llm_client: Optional[Any] = None):
        """Initialize the Question Queue Agent."""
        super().__init__(name="QuestionQueueAgent", llm_client=llm_client)
        self.queue: List[Question] = []
        self.processed: List[Question] = []
        self.category_queues: Dict[str, List[Question]] = {}
        self.assigned_questions: Dict[str, Set[str]] = {}  # agent -> question ids
        self.question_index: Dict[str, Question] = {}
        self.queue_stats = {
            "total_queued": 0,
            "total_processed": 0,
            "avg_wait_time": 0.0,
        }

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process question queue requests."""
        action = request.get("action", "add")

        if action == "add":
            return self.add_question(
                cast(str, request.get("question")),
                cast(str, request.get("priority", "normal")),
                cast(str, request.get("category", "general")),
            )
        elif action == "next":
            return self.get_next_question(cast(Optional[str], request.get("category")))
        elif action == "assign":
            return self.assign_question(
                cast(str, request.get("question_id")), cast(str, request.get("agent"))
            )
        elif action == "answer":
            return self.answer_question(
                cast(str, request.get("question_id")), cast(str, request.get("answer"))
            )
        elif action == "get":
            return self.get_question(cast(str, request.get("question_id")))
        elif action == "list":
            return self.list_queue(
                cast(Optional[str], request.get("status")),
                cast(Optional[str], request.get("category")),
            )
        elif action == "remove":
            return self.remove_question(cast(str, request.get("question_id")))
        elif action == "requeue":
            return self.requeue_question(cast(str, request.get("question_id")))
        elif action == "set_dependency":
            return self.set_dependency(
                cast(str, request.get("question_id")), cast(str, request.get("depends_on"))
            )
        elif action == "relate":
            return self.relate_questions(
                cast(str, request.get("question_id")), cast(str, request.get("related_id"))
            )
        elif action == "batch_process":
            return self.batch_process(cast(int, request.get("limit", 10)))
        elif action == "stats":
            return self.get_queue_stats()
        elif action == "health":
            return self.get_queue_health()
        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    def add_question(
        self, text: str, priority: str = "normal", category: str = "general"
    ) -> Dict[str, Any]:
        """Add question to queue."""
        if not text:
            return {"status": "error", "message": "Question text required"}

        question = Question(text, priority, category)
        self.queue.append(question)
        self.question_index[question.id] = question
        self.queue_stats["total_queued"] += 1

        # Add to category queue
        if category not in self.category_queues:
            self.category_queues[category] = []
        self.category_queues[category].append(question)

        # Sort queue by priority and creation time
        self._sort_queue()

        return {
            "status": "success",
            "agent": self.name,
            "question_id": question.id,
            "priority": priority,
            "queue_position": self.queue.index(question) + 1,
            "queue_size": len(self.queue),
        }

    def get_next_question(self, category: Optional[str] = None) -> Dict[str, Any]:
        """Get next question from queue."""
        if not self.queue:
            return {"status": "success", "agent": self.name, "message": "Queue is empty"}

        # Filter by category if specified
        candidates = self.queue
        if category:
            candidates = [q for q in self.queue if q.category == category]

        if not candidates:
            return {
                "status": "success",
                "agent": self.name,
                "message": f"No questions in {category} category",
            }

        question = candidates[0]

        return {
            "status": "success",
            "agent": self.name,
            "question": question.to_dict(),
            "queue_position": self.queue.index(question) + 1,
            "remaining_in_queue": len(self.queue) - 1,
        }

    def assign_question(self, question_id: str, agent: str) -> Dict[str, Any]:
        """Assign question to an agent."""
        if not question_id or not agent:
            return {"status": "error", "message": "Question ID and agent required"}

        if question_id not in self.question_index:
            return {"status": "error", "message": f"Question {question_id} not found"}

        question = self.question_index[question_id]
        question.assigned_to = agent
        question.status = QuestionStatus.ASSIGNED

        # Track assignment
        if agent not in self.assigned_questions:
            self.assigned_questions[agent] = set()
        self.assigned_questions[agent].add(question_id)

        return {
            "status": "success",
            "agent": self.name,
            "question_id": question_id,
            "assigned_to": agent,
        }

    def answer_question(self, question_id: str, answer: str) -> Dict[str, Any]:
        """Mark question as answered."""
        if not question_id:
            return {"status": "error", "message": "Question ID required"}

        if question_id not in self.question_index:
            return {"status": "error", "message": f"Question {question_id} not found"}

        question = self.question_index[question_id]
        question.answer = answer
        question.answered_at = datetime.utcnow()
        question.status = QuestionStatus.ANSWERED

        # Move to processed
        if question in self.queue:
            self.queue.remove(question)
        self.processed.append(question)
        self.queue_stats["total_processed"] += 1

        return {
            "status": "success",
            "agent": self.name,
            "question_id": question_id,
            "answered": True,
            "remaining_in_queue": len(self.queue),
        }

    def get_question(self, question_id: str) -> Dict[str, Any]:
        """Get question details."""
        if not question_id:
            return {"status": "error", "message": "Question ID required"}

        if question_id not in self.question_index:
            return {"status": "error", "message": f"Question {question_id} not found"}

        question = self.question_index[question_id]

        return {
            "status": "success",
            "agent": self.name,
            "question": question.to_dict(),
            "answer": question.answer,
        }

    def list_queue(
        self, status: Optional[str] = None, category: Optional[str] = None
    ) -> Dict[str, Any]:
        """List questions in queue."""
        questions = list(self.queue)

        if status:
            questions = [q for q in questions if q.status.value == status]

        if category:
            questions = [q for q in questions if q.category == category]

        return {
            "status": "success",
            "agent": self.name,
            "queued_count": len(self.queue),
            "returned_count": len(questions),
            "questions": [q.to_dict() for q in questions],
        }

    def remove_question(self, question_id: str) -> Dict[str, Any]:
        """Remove question from queue."""
        if not question_id:
            return {"status": "error", "message": "Question ID required"}

        if question_id not in self.question_index:
            return {"status": "error", "message": f"Question {question_id} not found"}

        question = self.question_index[question_id]
        if question in self.queue:
            self.queue.remove(question)

        return {
            "status": "success",
            "agent": self.name,
            "question_id": question_id,
            "removed": True,
            "queue_size": len(self.queue),
        }

    def requeue_question(self, question_id: str) -> Dict[str, Any]:
        """Move question back to queue."""
        if not question_id:
            return {"status": "error", "message": "Question ID required"}

        if question_id not in self.question_index:
            return {"status": "error", "message": f"Question {question_id} not found"}

        question = self.question_index[question_id]

        if question.attempts >= question.max_attempts:
            return {"status": "error", "message": "Question exceeded max attempts"}

        question.attempts += 1
        question.status = QuestionStatus.PENDING
        question.assigned_to = None
        question.answer = None

        if question not in self.queue:
            self.queue.append(question)
            self._sort_queue()

        return {
            "status": "success",
            "agent": self.name,
            "question_id": question_id,
            "requeued": True,
            "attempts": question.attempts,
        }

    def set_dependency(self, question_id: str, depends_on: str) -> Dict[str, Any]:
        """Set question dependency."""
        if not question_id or not depends_on:
            return {"status": "error", "message": "Question IDs required"}

        if question_id not in self.question_index:
            return {"status": "error", "message": f"Question {question_id} not found"}

        self.question_index[question_id].dependencies.add(depends_on)

        return {
            "status": "success",
            "agent": self.name,
            "question_id": question_id,
            "depends_on": depends_on,
        }

    def relate_questions(self, question_id: str, related_id: str) -> Dict[str, Any]:
        """Relate two questions."""
        if not question_id or not related_id:
            return {"status": "error", "message": "Question IDs required"}

        if question_id not in self.question_index:
            return {"status": "error", "message": f"Question {question_id} not found"}

        self.question_index[question_id].related_questions.add(related_id)

        return {
            "status": "success",
            "agent": self.name,
            "question_id": question_id,
            "related_to": related_id,
        }

    def batch_process(self, limit: int = 10) -> Dict[str, Any]:
        """Process batch of questions."""
        batch = self.queue[:limit]
        processed_count = 0

        for question in batch:
            if question.status == QuestionStatus.ANSWERED:
                self.queue.remove(question)
                processed_count += 1

        return {
            "status": "success",
            "agent": self.name,
            "processed_count": processed_count,
            "remaining_in_queue": len(self.queue),
        }

    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        wait_times = []
        for q in self.processed:
            if q.answered_at:
                wait_time = (q.answered_at - q.created_at).total_seconds() / 60
                wait_times.append(wait_time)

        avg_wait = sum(wait_times) / len(wait_times) if wait_times else 0

        return {
            "status": "success",
            "agent": self.name,
            "queue_size": len(self.queue),
            "processed_count": len(self.processed),
            "total_queued": self.queue_stats["total_queued"],
            "avg_wait_time_minutes": round(avg_wait, 2),
            "categories": len(self.category_queues),
        }

    def get_queue_health(self) -> Dict[str, Any]:
        """Get queue health status."""
        health_score = 100.0

        # Deduct for queue size
        if len(self.queue) > 100:
            health_score -= 20
        elif len(self.queue) > 50:
            health_score -= 10

        # Deduct for old questions
        old_questions = [
            q for q in self.queue if datetime.utcnow() - q.created_at > timedelta(hours=24)
        ]
        if old_questions:
            health_score -= min(len(old_questions), 20)

        return {
            "status": "success",
            "agent": self.name,
            "health_score": max(health_score, 0),
            "queue_size": len(self.queue),
            "old_questions": len(old_questions),
            "assessment": "healthy" if health_score > 80 else "degraded",
        }

    # Helper methods
    def _sort_queue(self) -> None:
        """Sort queue by priority and creation time."""
        self.queue.sort(key=lambda q: (q.priority.value, q.created_at))
