"""Unit tests for SocraticCounselor orchestration methods."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from src.socratic_agents.agents.socratic_counselor import SocraticCounselor


class MockProject:
    """Mock ProjectContext for testing."""

    def __init__(self):
        self.name = "Test Project"
        self.phase = "discovery"
        self.description = "A test project"
        self.pending_questions = []
        self.conversation_history = []
        self.maturity_scores = {}
        self.question_effectiveness = []


class MockUser:
    """Mock User for testing."""

    def __init__(self, user_id="test_user", tier="pro"):
        self.username = user_id
        self.email = f"{user_id}@test.com"
        self.subscription_tier = tier
        self.questions_today = 0
        self.questions_total = 0

    def increment_question_usage(self):
        self.questions_today += 1
        self.questions_total += 1


class TestSocraticCounselorInstantiation:
    """Test SocraticCounselor instantiation."""

    def test_create_counselor_minimal(self):
        """Test creating counselor with minimal parameters."""
        counselor = SocraticCounselor()
        assert counselor is not None
        assert counselor.name == "SocraticCounselor"
        assert counselor.batch_size == 1

    def test_create_counselor_with_params(self):
        """Test creating counselor with custom parameters."""
        mock_llm = Mock()
        mock_db = Mock()

        counselor = SocraticCounselor(llm_client=mock_llm, batch_size=3, database=mock_db)

        assert counselor.llm_client == mock_llm
        assert counselor.batch_size == 3
        assert counselor.database == mock_db


class TestGenerateQuestion:
    """Test _generate_question orchestration method."""

    def test_generate_question_returns_existing_unanswered(self):
        """Test that existing unanswered question is returned instead of generating new."""
        counselor = SocraticCounselor()
        project = MockProject()

        # Add an unanswered question
        project.pending_questions = [
            {
                "id": "q_existing",
                "question": "Existing question?",
                "phase": "discovery",
                "status": "unanswered",
            }
        ]

        result = counselor._generate_question(
            {
                "project": project,
                "user_id": "test_user",
            }
        )

        assert result["status"] == "success"
        assert result["question"] == "Existing question?"
        assert result["existing"] == True

    def test_generate_question_creates_new_when_none_unanswered(self):
        """Test that new question is generated when no unanswered questions exist."""
        counselor = SocraticCounselor()
        project = MockProject()

        result = counselor._generate_question(
            {
                "project": project,
                "user_id": "test_user",
            }
        )

        assert result["status"] == "success"
        assert result["question"] is not None
        assert len(project.pending_questions) == 1
        assert project.pending_questions[0]["status"] == "unanswered"

    def test_generate_question_stores_in_both_places(self):
        """Test that question is stored in conversation_history AND pending_questions."""
        counselor = SocraticCounselor()
        project = MockProject()

        counselor._generate_question(
            {
                "project": project,
                "user_id": "test_user",
            }
        )

        # Check pending_questions
        assert len(project.pending_questions) == 1
        assert project.pending_questions[0]["status"] == "unanswered"

        # Check conversation_history
        assert len(project.conversation_history) == 1
        assert project.conversation_history[0]["type"] == "assistant"

    def test_generate_question_auto_creates_user(self):
        """Test that user is auto-created if doesn't exist."""
        counselor = SocraticCounselor()
        project = MockProject()
        mock_db = Mock()
        mock_db.load_user.return_value = None
        counselor.database = mock_db

        result = counselor._generate_question(
            {
                "project": project,
                "user_id": "new_user",
            }
        )

        assert result["status"] == "success"
        assert mock_db.save_user.called

    def test_generate_question_requires_project(self):
        """Test that project is required."""
        counselor = SocraticCounselor()

        result = counselor._generate_question(
            {
                "user_id": "test_user",
                # No project
            }
        )

        assert result["status"] == "error"
        assert "required" in result["message"].lower()


class TestProcessResponse:
    """Test _process_response orchestration method."""

    def test_process_response_adds_to_history(self):
        """Test that response is added to conversation_history."""
        counselor = SocraticCounselor()
        project = MockProject()
        project.pending_questions = [
            {
                "id": "q_1",
                "question": "Test question?",
                "status": "unanswered",
            }
        ]

        result = counselor._process_response(
            {
                "project": project,
                "user_id": "test_user",
                "response": "User's answer",
            }
        )

        assert result["status"] == "success"

        # Check that response was added
        user_messages = [m for m in project.conversation_history if m["type"] == "user"]
        assert len(user_messages) == 1
        assert user_messages[0]["content"] == "User's answer"

    def test_process_response_marks_question_answered(self):
        """Test that question is marked as answered."""
        counselor = SocraticCounselor()
        project = MockProject()
        project.pending_questions = [
            {
                "id": "q_1",
                "question": "Test question?",
                "status": "unanswered",
                "answer": None,
            }
        ]

        result = counselor._process_response(
            {
                "project": project,
                "user_id": "test_user",
                "response": "User's answer",
            }
        )

        # Check that question is marked answered
        assert project.pending_questions[0]["status"] == "answered"
        assert project.pending_questions[0]["answer"] == "User's answer"

    def test_process_response_generates_next_question(self):
        """Test that next question is generated and returned."""
        counselor = SocraticCounselor()
        project = MockProject()
        project.pending_questions = [
            {
                "id": "q_1",
                "question": "First question?",
                "status": "unanswered",
            }
        ]

        result = counselor._process_response(
            {
                "project": project,
                "user_id": "test_user",
                "response": "User's answer",
            }
        )

        assert result["status"] == "success"
        assert "next_question" in result
        assert result["next_question"] is not None

        # Verify next question was added to pending_questions
        assert len(project.pending_questions) == 2

    def test_process_response_requires_project_and_response(self):
        """Test that project and response are both required."""
        counselor = SocraticCounselor()

        result = counselor._process_response(
            {
                "user_id": "test_user",
                # Missing project and response
            }
        )

        assert result["status"] == "error"


class TestFullDialogueFlow:
    """Test complete dialogue flow: Q -> A -> Q -> A."""

    def test_full_dialogue_three_turns(self):
        """Test complete dialogue with three question-answer turns."""
        counselor = SocraticCounselor()
        project = MockProject()

        # Turn 1: Generate first question
        q1_result = counselor._generate_question(
            {
                "project": project,
                "user_id": "user_1",
            }
        )
        assert q1_result["status"] == "success"
        q1_text = q1_result["question"]

        # Turn 1: Answer first question
        a1_result = counselor._process_response(
            {
                "project": project,
                "user_id": "user_1",
                "response": "First answer to the question",
            }
        )
        assert a1_result["status"] == "success"
        assert "next_question" in a1_result
        q2_text = a1_result["next_question"]

        # Verify conversation has 3 messages (Q1, A1, Q2) because next question is generated
        assert len(project.conversation_history) == 3

        # Turn 2: Answer second question
        a2_result = counselor._process_response(
            {
                "project": project,
                "user_id": "user_1",
                "response": "Second answer",
            }
        )
        assert a2_result["status"] == "success"
        assert "next_question" in a2_result
        q3_text = a2_result["next_question"]

        # Verify conversation grew (each turn generates next Q)
        assert len(project.conversation_history) == 5  # Q1, A1, Q2, A2, Q3

        # Verify all questions were tracked
        assert len(project.pending_questions) >= 3

    def test_questions_dont_repeat(self):
        """Test that the same question isn't asked twice."""
        counselor = SocraticCounselor()
        project = MockProject()

        # Generate first question
        q1_result = counselor._generate_question(
            {
                "project": project,
                "user_id": "user_1",
            }
        )
        q1_text = q1_result["question"]

        # Try to generate again without answering (should return existing)
        q2_result = counselor._generate_question(
            {
                "project": project,
                "user_id": "user_1",
            }
        )

        # Should return existing question
        assert q2_result.get("existing") == True
        assert q2_result["question"] == q1_text


class TestExtractInsights:
    """Test insight extraction."""

    def test_extract_insights_handles_empty_response(self):
        """Test insight extraction with empty response."""
        counselor = SocraticCounselor()

        result = counselor._extract_insights_only(
            {
                "response": "",
            }
        )

        assert result["status"] == "error"

    def test_extract_insights_with_response(self):
        """Test insight extraction with valid response."""
        counselor = SocraticCounselor()

        result = counselor._extract_insights_only(
            {
                "response": "This is a detailed response about the requirements.",
            }
        )

        assert result["status"] == "success"
        assert "insights" in result


class TestSubscriptionValidation:
    """Test subscription limit validation."""

    def test_subscription_pro_tier_unlimited(self):
        """Test that pro tier users have high limit."""
        counselor = SocraticCounselor()
        user = MockUser("test", tier="pro")
        user.questions_today = 50

        can_ask, error = counselor._check_subscription_limit(user)

        assert can_ask == True
        assert error is None

    def test_subscription_free_tier_limited(self):
        """Test that free tier users have daily limit."""
        counselor = SocraticCounselor()
        user = MockUser("test", tier="free")
        user.questions_today = 5  # At limit

        can_ask, error = counselor._check_subscription_limit(user)

        assert can_ask == False
        assert "limit" in error.lower()


class TestPhasedQuestions:
    """Test that questions are phase-appropriate."""

    def test_discovery_phase_question(self):
        """Test question generation for discovery phase."""
        counselor = SocraticCounselor()
        project = MockProject()
        project.phase = "discovery"

        result = counselor._generate_question(
            {
                "project": project,
                "user_id": "user_1",
            }
        )

        assert result["status"] == "success"
        question = result["question"]
        assert question is not None
        assert len(question) > 0

    def test_different_phases_generate_different_questions(self):
        """Test that different phases generate appropriately different questions."""
        counselor = SocraticCounselor()

        # Discovery phase
        project1 = MockProject()
        project1.phase = "discovery"
        q1 = counselor._get_fallback_question("API", "beginner", "discovery")

        # Implementation phase
        project2 = MockProject()
        project2.phase = "implementation"
        q2 = counselor._get_fallback_question("API", "beginner", "implementation")

        # Questions should be different
        assert q1 != q2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
