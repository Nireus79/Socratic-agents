"""
Phase 7: Complete System Integration Tests

Tests end-to-end integration of:
1. SocratesIntegration with database
2. WorkflowManager with multi-agent workflows
3. Complete user journeys through all phases
4. Maturity progression and tracking
5. Skill application in real scenarios
6. Full system coordination
"""

import pytest
from unittest.mock import Mock, MagicMock
from typing import Any, Dict

from src.socratic_agents.orchestration import (
    PureOrchestrator,
    MaturityAwareOrchestrator,
)
from src.socratic_agents.orchestration.socrates_integration import (
    SocratesIntegration,
    WorkflowManager,
)


class MockDatabase:
    """Mock Socrates database."""

    def __init__(self):
        self.users = {}

    def load_user(self, user_id: str) -> Any:
        """Load user from database."""
        if user_id not in self.users:
            user = Mock()
            user.user_id = user_id
            user.maturity_scores = {
                "discovery": 0.0,
                "analysis": 0.0,
                "design": 0.0,
                "implementation": 0.0,
            }
            self.users[user_id] = user
        return self.users[user_id]

    def save_user(self, user: Any) -> bool:
        """Save user to database."""
        self.users[user.user_id] = user
        return True


class MockAgent:
    """Mock agent for testing."""

    def __init__(self, name: str):
        self.name = name

    def process(self, request: dict) -> dict:
        """Process request."""
        return {
            "status": "success",
            "agent": self.name,
            "action": request.get("action", "unknown"),
            "result": f"Processed by {self.name}",
        }


class MockExistingOrchestrator:
    """Mock of existing Socrates orchestrator."""

    def process_request(self, agent_name: str, request: dict) -> dict:
        """Process request."""
        return {
            "status": "success",
            "agent": agent_name,
            "action": request.get("action", "unknown"),
            "result": "Processed",
        }


class TestSocratesIntegration:
    """Test SocratesIntegration class."""

    def test_integration_initialization(self):
        """Test integration can be initialized."""
        db = MockDatabase()
        integration = SocratesIntegration(db)

        assert integration is not None
        assert integration.database == db

    def test_get_user_maturity_default(self):
        """Test getting default user maturity."""
        db = MockDatabase()
        integration = SocratesIntegration(db)

        maturity = integration.get_user_maturity("user123")

        assert 0.0 <= maturity <= 1.0

    def test_get_user_maturity_cached(self):
        """Test maturity is cached."""
        db = MockDatabase()
        integration = SocratesIntegration(db)

        # Set maturity
        integration._user_maturity_cache["user123"] = {
            "discovery": 0.8,
            "analysis": 0.6,
        }

        # Get overall maturity (should use cache)
        maturity = integration.get_user_maturity("user123")

        assert maturity > 0.0

    def test_get_user_phase(self):
        """Test getting user's current phase."""
        db = MockDatabase()
        integration = SocratesIntegration(db)

        # Low maturity -> discovery
        phase = integration.get_user_phase("user123")
        assert phase == "discovery"

        # High maturity -> implementation
        integration._user_maturity_cache["user456"] = {
            "discovery": 1.0,
            "analysis": 1.0,
            "design": 1.0,
            "implementation": 1.0,
        }
        phase = integration.get_user_phase("user456")
        assert phase == "implementation"

    def test_record_agent_execution(self):
        """Test recording agent execution."""
        db = MockDatabase()
        integration = SocratesIntegration(db)

        success = integration.record_agent_execution(
            user_id="user123",
            agent_name="code_generator",
            action="generate",
            input_data={"code": "test"},
            output_data={"result": "generated"},
            effectiveness=0.85,
        )

        assert success

    def test_update_user_maturity(self):
        """Test updating user maturity."""
        db = MockDatabase()
        integration = SocratesIntegration(db)

        success = integration.update_user_maturity(
            user_id="user123",
            phase_scores={
                "discovery": 1.0,
                "analysis": 0.8,
                "design": 0.6,
                "implementation": 0.4,
            },
        )

        assert success
        assert "user123" in integration._user_maturity_cache

    def test_create_maturity_aware_orchestrator(self):
        """Test creating maturity-aware orchestrator."""
        db = MockDatabase()
        integration = SocratesIntegration(db)

        existing = MockExistingOrchestrator()
        agents = {"test_agent": MockAgent("TestAgent")}
        pure = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.5,
            get_learning_effectiveness=lambda a: 0.7,
        )

        wrapper = integration.create_maturity_aware_orchestrator(existing, pure)

        assert wrapper is not None
        assert isinstance(wrapper, MaturityAwareOrchestrator)

    def test_get_recommended_next_steps(self):
        """Test getting recommendations."""
        db = MockDatabase()
        integration = SocratesIntegration(db)

        recommendations = integration.get_recommended_next_steps("user123")

        assert "current_phase" in recommendations
        assert "next_phase" in recommendations
        assert "available_agents" in recommendations


class TestWorkflowManager:
    """Test WorkflowManager class."""

    def test_workflow_manager_initialization(self):
        """Test workflow manager can be initialized."""
        existing = MockExistingOrchestrator()
        agents = {"test_agent": MockAgent("TestAgent")}
        pure = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.5,
            get_learning_effectiveness=lambda a: 0.7,
        )
        orchestrator = MaturityAwareOrchestrator(existing, pure)

        db = MockDatabase()
        integration = SocratesIntegration(db)

        manager = WorkflowManager(orchestrator, integration)

        assert manager is not None

    def test_start_discovery_workflow(self):
        """Test starting a discovery workflow."""
        existing = MockExistingOrchestrator()
        agents = {
            "socratic_counselor": MockAgent("SocraticCounselor"),
            "context_analyzer": MockAgent("ContextAnalyzer"),
        }
        pure = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.1,
            get_learning_effectiveness=lambda a: 0.7,
        )
        orchestrator = MaturityAwareOrchestrator(existing, pure)

        db = MockDatabase()
        integration = SocratesIntegration(db)
        manager = WorkflowManager(orchestrator, integration)

        workflow_id = manager.start_discovery_workflow(
            user_id="user123",
            project_id="proj456",
            project_description="A test project",
        )

        assert workflow_id is not None
        assert "discovery" in workflow_id

    def test_start_analysis_workflow(self):
        """Test starting an analysis workflow."""
        existing = MockExistingOrchestrator()
        agents = {
            "quality_controller": MockAgent("QualityController"),
            "code_generator": MockAgent("CodeGenerator"),
        }
        pure = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.3,
            get_learning_effectiveness=lambda a: 0.7,
        )
        orchestrator = MaturityAwareOrchestrator(existing, pure)

        db = MockDatabase()
        integration = SocratesIntegration(db)
        manager = WorkflowManager(orchestrator, integration)

        workflow_id = manager.start_analysis_workflow(
            user_id="user123",
            project_id="proj456",
            code="def hello(): pass",
        )

        assert workflow_id is not None
        assert "analysis" in workflow_id

    def test_execute_workflow_step(self):
        """Test executing a workflow step."""
        existing = MockExistingOrchestrator()
        agents = {
            "socratic_counselor": MockAgent("SocraticCounselor"),
            "context_analyzer": MockAgent("ContextAnalyzer"),
        }
        pure = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.1,
            get_learning_effectiveness=lambda a: 0.7,
        )
        orchestrator = MaturityAwareOrchestrator(existing, pure)

        db = MockDatabase()
        integration = SocratesIntegration(db)
        manager = WorkflowManager(orchestrator, integration)

        workflow_id = manager.start_discovery_workflow("user123", "proj456", "A test project")

        # Execute first step
        success = manager.execute_workflow_step(workflow_id)

        assert success

    def test_complete_workflow(self):
        """Test completing a workflow."""
        existing = MockExistingOrchestrator()
        agents = {
            "socratic_counselor": MockAgent("SocraticCounselor"),
            "context_analyzer": MockAgent("ContextAnalyzer"),
        }
        pure = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.1,
            get_learning_effectiveness=lambda a: 0.7,
        )
        orchestrator = MaturityAwareOrchestrator(existing, pure)

        db = MockDatabase()
        integration = SocratesIntegration(db)
        manager = WorkflowManager(orchestrator, integration)

        workflow_id = manager.start_discovery_workflow("user123", "proj456", "A test project")

        # Execute all steps
        for _ in range(2):
            manager.execute_workflow_step(workflow_id)

        # Complete workflow
        result = manager.complete_workflow(workflow_id)

        assert result["workflow_id"] == workflow_id
        assert "phase" in result
        assert "results" in result


class TestEndToEndUserJourney:
    """Test complete user journeys through all phases."""

    def test_discovery_phase_journey(self):
        """Test user journey through discovery phase."""
        # Setup
        existing = MockExistingOrchestrator()
        agents = {
            "socratic_counselor": MockAgent("SocraticCounselor"),
            "context_analyzer": MockAgent("ContextAnalyzer"),
            "knowledge_manager": MockAgent("KnowledgeManager"),
        }
        pure = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.1,
            get_learning_effectiveness=lambda a: 0.7,
        )
        orchestrator = MaturityAwareOrchestrator(existing, pure)

        db = MockDatabase()
        integration = SocratesIntegration(db)
        manager = WorkflowManager(orchestrator, integration)

        user_id = "user_discovery"

        # Start in discovery phase
        phase = integration.get_user_phase(user_id)
        assert phase == "discovery"

        # Get recommendations
        recs = integration.get_recommended_next_steps(user_id)
        assert recs["current_phase"] == "discovery"

        # Start discovery workflow
        wf_id = manager.start_discovery_workflow(user_id, "proj1", "A project to build")
        assert wf_id is not None

        # Execute workflow steps
        manager.execute_workflow_step(wf_id)
        manager.execute_workflow_step(wf_id)

        # Complete workflow
        result = manager.complete_workflow(wf_id)
        assert result["phase"] == "discovery"

    def test_analysis_phase_journey(self):
        """Test user journey through analysis phase."""
        existing = MockExistingOrchestrator()
        agents = {
            "quality_controller": MockAgent("QualityController"),
            "code_generator": MockAgent("CodeGenerator"),
            "context_analyzer": MockAgent("ContextAnalyzer"),
        }
        pure = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.3,
            get_learning_effectiveness=lambda a: 0.7,
        )
        orchestrator = MaturityAwareOrchestrator(existing, pure)

        db = MockDatabase()
        integration = SocratesIntegration(db)
        manager = WorkflowManager(orchestrator, integration)

        user_id = "user_analysis"

        # Update maturity to analysis phase (30% overall = analysis phase)
        # With discovery at 0.6, analysis at 0.0: (0.6 + 0.0) / 1 = 0.6, but design is 0-75%
        # So use lower discovery to stay in analysis: (0.5) / 1 = 0.5 (boundary to design)
        integration.update_user_maturity(
            user_id,
            {
                "discovery": 0.5,
                "analysis": 0.2,
                "design": 0.0,
                "implementation": 0.0,
            },
        )

        phase = integration.get_user_phase(user_id)
        # (0.5 + 0.2) / 2 = 0.35, which is analysis
        assert phase == "analysis"

        # Start analysis workflow
        wf_id = manager.start_analysis_workflow(
            user_id, "proj1", "def hello(): pass\ndef world(): pass"
        )

        assert wf_id is not None
        manager.execute_workflow_step(wf_id)

    def test_maturity_progression(self):
        """Test maturity progression through all phases."""
        db = MockDatabase()
        integration = SocratesIntegration(db)

        user_id = "user_progression"

        # Start at discovery (0-25% overall maturity)
        maturity = integration.get_user_maturity(user_id)
        phase = integration.get_user_phase(user_id)
        assert phase == "discovery"

        # Progress to analysis (25-50% overall maturity)
        # (0.5 + 0.2) / 2 = 0.35 (analysis)
        integration.update_user_maturity(
            user_id,
            {
                "discovery": 0.5,
                "analysis": 0.2,
                "design": 0.0,
                "implementation": 0.0,
            },
        )
        phase = integration.get_user_phase(user_id)
        assert phase == "analysis"

        # Progress to design (50-75% overall maturity)
        # (0.9 + 0.3 + 0.2) / 3 = 0.47 (analysis), need higher
        # (1.0 + 0.6 + 0.2) / 3 = 0.6 (design)
        integration.update_user_maturity(
            user_id,
            {
                "discovery": 1.0,
                "analysis": 0.6,
                "design": 0.2,
                "implementation": 0.0,
            },
        )
        phase = integration.get_user_phase(user_id)
        assert phase == "design"

        # Progress to implementation (75-100% overall maturity)
        # (1.0 + 1.0 + 0.8 + 0.8) / 4 = 0.9 (implementation)
        integration.update_user_maturity(
            user_id,
            {
                "discovery": 1.0,
                "analysis": 1.0,
                "design": 0.8,
                "implementation": 0.8,
            },
        )
        phase = integration.get_user_phase(user_id)
        assert phase == "implementation"

    def test_full_system_workflow(self):
        """Test complete workflow from discovery to implementation."""
        existing = MockExistingOrchestrator()
        agents = {
            "socratic_counselor": MockAgent("SocraticCounselor"),
            "code_generator": MockAgent("CodeGenerator"),
            "quality_controller": MockAgent("QualityController"),
            "code_validator": MockAgent("CodeValidator"),
        }
        pure = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.5,
            get_learning_effectiveness=lambda a: 0.7,
        )
        orchestrator = MaturityAwareOrchestrator(existing, pure)

        db = MockDatabase()
        integration = SocratesIntegration(db)
        manager = WorkflowManager(orchestrator, integration)

        user_id = "user_full"
        project_id = "full_project"

        # Discovery phase
        disc_wf = manager.start_discovery_workflow(user_id, project_id, "Build a calculator")
        manager.execute_workflow_step(disc_wf)
        manager.complete_workflow(disc_wf)

        # Advance maturity
        integration.update_user_maturity(
            user_id,
            {
                "discovery": 1.0,
                "analysis": 0.1,
                "design": 0.0,
                "implementation": 0.0,
            },
        )

        # Analysis phase
        analysis_wf = manager.start_analysis_workflow(
            user_id, project_id, "def add(a,b): return a+b"
        )
        manager.execute_workflow_step(analysis_wf)
        manager.complete_workflow(analysis_wf)

        # Record improvements
        integration.record_agent_execution(
            user_id=user_id,
            agent_name="quality_controller",
            action="detect_weak_areas",
            input_data={"code": "def add(a,b): return a+b"},
            output_data={"weak_areas": ["testing"]},
            effectiveness=0.8,
        )


class TestSystemCoordination:
    """Test system-wide coordination."""

    def test_multiple_users_coordination(self):
        """Test coordination with multiple users at different phases."""
        existing = MockExistingOrchestrator()
        agents = {
            "socratic_counselor": MockAgent("SocraticCounselor"),
            "code_generator": MockAgent("CodeGenerator"),
            "quality_controller": MockAgent("QualityController"),
        }
        pure = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.5,
            get_learning_effectiveness=lambda a: 0.7,
        )
        orchestrator = MaturityAwareOrchestrator(existing, pure)

        db = MockDatabase()
        integration = SocratesIntegration(db)

        # User 1: Discovery phase (0-25% overall)
        integration.update_user_maturity(
            "user1",
            {
                "discovery": 0.1,
                "analysis": 0.0,
                "design": 0.0,
                "implementation": 0.0,
            },
        )
        phase1 = integration.get_user_phase("user1")
        assert phase1 == "discovery"

        # User 2: Analysis phase (25-50% overall)
        # (0.5 + 0.2) / 2 = 0.35 (analysis)
        integration.update_user_maturity(
            "user2",
            {
                "discovery": 0.5,
                "analysis": 0.2,
                "design": 0.0,
                "implementation": 0.0,
            },
        )
        phase2 = integration.get_user_phase("user2")
        assert phase2 == "analysis"

        # User 3: Implementation phase (75-100% overall)
        integration.update_user_maturity(
            "user3",
            {
                "discovery": 1.0,
                "analysis": 1.0,
                "design": 1.0,
                "implementation": 0.5,
            },
        )
        phase3 = integration.get_user_phase("user3")
        assert phase3 == "implementation"

        # Each user gets appropriate recommendations
        recs1 = integration.get_recommended_next_steps("user1")
        recs2 = integration.get_recommended_next_steps("user2")
        recs3 = integration.get_recommended_next_steps("user3")

        assert recs1["current_phase"] == "discovery"
        assert recs2["current_phase"] == "analysis"
        assert recs3["current_phase"] == "implementation"

    def test_agent_effectiveness_tracking(self):
        """Test tracking agent effectiveness across executions."""
        db = MockDatabase()
        integration = SocratesIntegration(db)

        # Record multiple executions
        for effectiveness in [0.8, 0.85, 0.90]:
            integration.record_agent_execution(
                user_id="user123",
                agent_name="code_generator",
                action="generate",
                input_data={},
                output_data={},
                effectiveness=effectiveness,
            )

        # Check effectiveness improved
        eff = integration.get_agent_effectiveness("code_generator")
        assert 0.8 <= eff <= 0.9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
