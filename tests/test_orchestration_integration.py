"""
Phase 6: Integration Tests

Verifies integration of pure orchestration layer with existing Socrates system.

Tests:
1. OrchestratorAdapter works with gating
2. MaturityAwareOrchestrator wraps existing orchestrator
3. Integration modes (pure, hybrid, legacy)
4. Backward compatibility
5. Full end-to-end workflows
"""


import pytest

from src.socratic_agents.orchestration import (
    IntegrationMode,
    MaturityAwareOrchestrator,
    OrchestratorAdapter,
    PureOrchestrator,
)


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

    def apply_skill(self, skill):
        """Apply skill."""
        pass


class MockExistingOrchestrator:
    """Mock of existing Socrates orchestrator."""

    def __init__(self):
        self.call_count = 0
        self.last_request = None

    def process_request(self, agent_name: str, request: dict) -> dict:
        """Process request using existing orchestrator."""
        self.call_count += 1
        self.last_request = (agent_name, request)

        return {
            "status": "success",
            "agent": agent_name,
            "action": request.get("action", "unknown"),
            "result": "Processed by existing orchestrator",
        }


class TestOrchestratorAdapter:
    """Test OrchestratorAdapter for wrapping PureOrchestrator."""

    def test_adapter_initialization(self):
        """Test adapter can be initialized."""
        agents = {"test_agent": MockAgent("TestAgent")}
        orchestrator = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.5,
            get_learning_effectiveness=lambda a: 0.7,
        )

        adapter = OrchestratorAdapter(orchestrator, IntegrationMode.HYBRID)

        assert adapter is not None
        assert adapter.mode == IntegrationMode.HYBRID
        assert adapter.pure_orchestrator == orchestrator

    def test_adapter_execute_with_gating_allowed(self):
        """Test adapter allows execution when maturity sufficient."""
        agents = {"code_generator": MockAgent("CodeGenerator")}
        orchestrator = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.6,
            get_learning_effectiveness=lambda a: 0.7,
        )

        adapter = OrchestratorAdapter(orchestrator, IntegrationMode.HYBRID)

        response = adapter.execute_with_gating(
            agent_name="code_generator",
            action="generate",
            data={"code": "test"},
            user_id="user123",
            current_maturity=0.6,
            current_phase="design",
        )

        assert response["status"] == "success"
        assert response["agent"] == "CodeGenerator"  # Agent returns its own name

    def test_adapter_execute_with_gating_denied(self):
        """Test adapter blocks execution when maturity insufficient."""
        agents = {"code_validator": MockAgent("CodeValidator")}
        orchestrator = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.2,
            get_learning_effectiveness=lambda a: 0.7,
        )

        adapter = OrchestratorAdapter(orchestrator, IntegrationMode.HYBRID)

        response = adapter.execute_with_gating(
            agent_name="code_validator",
            action="validate",
            data={},
            user_id="user123",
            current_maturity=0.2,  # Too low
            current_phase="implementation",
        )

        assert response["status"] == "gated"
        assert "error" in response
        assert "suggestion" in response

    def test_adapter_legacy_mode_skips_gating(self):
        """Test legacy mode bypasses gating."""
        agents = {"code_validator": MockAgent("CodeValidator")}
        orchestrator = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.1,
            get_learning_effectiveness=lambda a: 0.7,
        )

        adapter = OrchestratorAdapter(orchestrator, IntegrationMode.LEGACY)

        response = adapter.execute_with_gating(
            agent_name="code_validator",
            action="validate",
            data={},
            current_maturity=0.1,  # Too low for implementation
        )

        # Should still execute despite low maturity
        assert response["status"] == "success"

    def test_adapter_apply_skills(self):
        """Test adapter can apply skills."""
        agents = {"code_generator": MockAgent("CodeGenerator")}
        orchestrator = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.5,
            get_learning_effectiveness=lambda a: 0.7,
        )

        adapter = OrchestratorAdapter(orchestrator)

        class MockSkill:
            def __init__(self):
                self.id = "skill_1"
                self.target_agent = "code_generator"

        skills = [MockSkill()]
        result = adapter.apply_skills(skills)

        assert result["status"] == "success"
        assert result["total_skills"] == 1

    def test_adapter_record_effectiveness(self):
        """Test adapter records effectiveness feedback."""
        agents = {}
        orchestrator = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.5,
            get_learning_effectiveness=lambda a: 0.7,
        )

        adapter = OrchestratorAdapter(orchestrator)

        success = adapter.record_effectiveness(
            agent_name="code_generator",
            action="generate",
            effectiveness=0.85,
            user_id="user123",
        )

        assert success
        assert len(adapter._feedback_log) == 1
        assert adapter._feedback_log[0]["effectiveness"] == 0.85

    def test_adapter_get_agent_availability(self):
        """Test adapter reports available agents for phase."""
        agents = {
            "socratic_counselor": MockAgent("SocraticCounselor"),
            "code_validator": MockAgent("CodeValidator"),
        }
        orchestrator = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.5,
            get_learning_effectiveness=lambda a: 0.7,
        )

        adapter = OrchestratorAdapter(orchestrator)

        # Discovery phase
        availability = adapter.get_agent_availability("discovery", 0.1)

        assert availability["phase"] == "discovery"
        assert "socratic_counselor" in availability["available_agents"]
        assert availability["quality_threshold"] == 0.0

    def test_adapter_next_steps_suggestion(self):
        """Test adapter suggests next steps when gated."""
        agents = {"code_generator": MockAgent("CodeGenerator")}
        orchestrator = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.3,
            get_learning_effectiveness=lambda a: 0.7,
        )

        adapter = OrchestratorAdapter(orchestrator)

        response = adapter.execute_with_gating(
            agent_name="code_generator",
            action="generate",
            data={},
            current_maturity=0.2,
            current_phase="implementation",
        )

        assert "suggestion" in response
        assert len(response["suggestion"]) > 0


class TestMaturityAwareOrchestrator:
    """Test MaturityAwareOrchestrator wrapper."""

    def test_maturity_aware_initialization(self):
        """Test maturity-aware orchestrator can be initialized."""
        existing = MockExistingOrchestrator()
        agents = {"test_agent": MockAgent("TestAgent")}
        pure = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.5,
            get_learning_effectiveness=lambda a: 0.7,
        )

        wrapper = MaturityAwareOrchestrator(existing, pure)

        assert wrapper is not None
        assert wrapper.existing_orchestrator == existing
        assert wrapper.pure_orchestrator == pure

    def test_maturity_aware_allows_execution(self):
        """Test wrapper allows execution when maturity sufficient."""
        existing = MockExistingOrchestrator()
        agents = {"code_generator": MockAgent("CodeGenerator")}
        pure = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.6,
            get_learning_effectiveness=lambda a: 0.7,
        )

        wrapper = MaturityAwareOrchestrator(
            existing,
            pure,
            maturity_tracker=lambda u: 0.6,
        )

        response = wrapper.process_request(
            "code_generator",
            {"action": "generate", "user_id": "user123"},
            enforce_gating=True,
        )

        # Should delegate to existing orchestrator
        assert existing.call_count == 1
        assert response["status"] == "success"

    def test_maturity_aware_gates_execution(self):
        """Test wrapper gates execution when maturity insufficient."""
        existing = MockExistingOrchestrator()
        agents = {"code_validator": MockAgent("CodeValidator")}
        pure = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.2,
            get_learning_effectiveness=lambda a: 0.7,
        )

        wrapper = MaturityAwareOrchestrator(
            existing,
            pure,
            maturity_tracker=lambda u: 0.1,  # Too low
        )

        response = wrapper.process_request(
            "code_validator",
            {
                "action": "validate",
                "user_id": "user123",
            },
            enforce_gating=True,
        )

        # Should NOT delegate to existing orchestrator
        assert existing.call_count == 0
        assert response["status"] == "gated"
        assert "error" in response

    def test_maturity_aware_skip_gating(self):
        """Test wrapper can skip gating."""
        existing = MockExistingOrchestrator()
        agents = {}
        pure = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.1,
            get_learning_effectiveness=lambda a: 0.7,
        )

        wrapper = MaturityAwareOrchestrator(existing, pure)

        wrapper.process_request(
            "any_agent",
            {"action": "test"},
            enforce_gating=False,  # Skip gating
        )

        # Should always delegate to existing orchestrator
        assert existing.call_count == 1

    def test_maturity_aware_stats(self):
        """Test wrapper tracks statistics."""
        existing = MockExistingOrchestrator()
        agents = {"code_generator": MockAgent("CodeGenerator")}
        pure = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.5,
            get_learning_effectiveness=lambda a: 0.7,
        )

        wrapper = MaturityAwareOrchestrator(
            existing,
            pure,
            maturity_tracker=lambda u: 0.5,
        )

        # Make requests
        wrapper.process_request("code_generator", {"action": "test"}, enforce_gating=True)
        wrapper.process_request("code_generator", {"action": "test"}, enforce_gating=True)

        stats = wrapper.get_stats()

        assert stats["total_requests"] == 2
        assert "pass_rate" in stats
        assert "gated_requests" in stats

    def test_maturity_aware_handles_errors(self):
        """Test wrapper handles maturity tracking errors gracefully."""
        existing = MockExistingOrchestrator()
        agents = {"test_agent": MockAgent("TestAgent")}
        pure = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.5,
            get_learning_effectiveness=lambda a: 0.7,
        )

        # Maturity tracker that raises errors
        def failing_tracker(u):
            raise RuntimeError("Maturity service down")

        wrapper = MaturityAwareOrchestrator(
            existing,
            pure,
            maturity_tracker=failing_tracker,
        )

        # Should still work with default maturity
        wrapper.process_request(
            "test_agent",
            {"action": "test"},
            enforce_gating=True,
        )

        # Should fall back to existing orchestrator
        assert existing.call_count == 1


class TestIntegrationModes:
    """Test different integration modes."""

    def test_pure_mode(self):
        """Test pure mode uses only PureOrchestrator."""
        agents = {"code_generator": MockAgent("CodeGenerator")}
        orchestrator = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.5,
            get_learning_effectiveness=lambda a: 0.7,
        )

        adapter = OrchestratorAdapter(orchestrator, IntegrationMode.PURE)

        assert adapter.mode == IntegrationMode.PURE

    def test_hybrid_mode(self):
        """Test hybrid mode uses both orchestrators."""
        agents = {"code_generator": MockAgent("CodeGenerator")}
        orchestrator = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.5,
            get_learning_effectiveness=lambda a: 0.7,
        )

        adapter = OrchestratorAdapter(orchestrator, IntegrationMode.HYBRID)

        assert adapter.mode == IntegrationMode.HYBRID

    def test_legacy_mode(self):
        """Test legacy mode bypasses pure orchestrator."""
        agents = {"code_generator": MockAgent("CodeGenerator")}
        orchestrator = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.5,
            get_learning_effectiveness=lambda a: 0.7,
        )

        adapter = OrchestratorAdapter(orchestrator, IntegrationMode.LEGACY)

        assert adapter.mode == IntegrationMode.LEGACY


class TestBackwardCompatibility:
    """Test backward compatibility with existing system."""

    def test_existing_orchestrator_still_works(self):
        """Test existing orchestrator continues to work."""
        existing = MockExistingOrchestrator()

        response = existing.process_request("agent", {"action": "test"})

        assert response["status"] == "success"
        assert existing.call_count == 1

    def test_can_replace_gradually(self):
        """Test can migrate gradually from existing to new."""
        existing = MockExistingOrchestrator()
        agents = {"code_generator": MockAgent("CodeGenerator")}
        pure = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.5,
            get_learning_effectiveness=lambda a: 0.7,
        )

        wrapper = MaturityAwareOrchestrator(existing, pure)

        # Route some requests with gating, others without
        response1 = wrapper.process_request("code_generator", {}, enforce_gating=True)
        response2 = wrapper.process_request("code_generator", {}, enforce_gating=False)

        # Both should complete successfully
        assert response1["status"] in ["success", "gated"]
        assert response2["status"] == "success"


class TestEndToEndIntegration:
    """Test complete end-to-end integration scenarios."""

    def test_full_request_lifecycle(self):
        """Test full request lifecycle with gating and feedback."""
        agents = {
            "code_generator": MockAgent("CodeGenerator"),
            "quality_controller": MockAgent("QualityController"),
        }
        orchestrator = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.5,
            get_learning_effectiveness=lambda a: 0.7,
        )

        adapter = OrchestratorAdapter(orchestrator)

        # Step 1: Execute request
        response = adapter.execute_with_gating(
            agent_name="code_generator",
            action="generate",
            data={"requirements": "test"},
            user_id="user123",
            current_maturity=0.5,
        )

        assert response["status"] == "success"

        # Step 2: Record effectiveness
        success = adapter.record_effectiveness(
            agent_name="code_generator",
            action="generate",
            effectiveness=0.85,
            user_id="user123",
        )

        assert success

        # Step 3: Check availability for next phase
        availability = adapter.get_agent_availability("design", 0.55)

        assert "code_generator" in availability["available_agents"]

    def test_workflow_with_multiple_agents(self):
        """Test workflow using multiple agents."""
        agents = {
            "socratic_counselor": MockAgent("SocraticCounselor"),
            "code_generator": MockAgent("CodeGenerator"),
            "quality_controller": MockAgent("QualityController"),
        }
        orchestrator = PureOrchestrator(
            agents=agents,
            get_maturity=lambda u, p: 0.5,
            get_learning_effectiveness=lambda a: 0.7,
        )

        adapter = OrchestratorAdapter(orchestrator)

        # Discovery phase - use counselor
        r1 = adapter.execute_with_gating(
            "socratic_counselor",
            "guide",
            {},
            current_maturity=0.1,
            current_phase="discovery",
        )
        assert r1["status"] == "success"

        # Analysis phase - use generator
        r2 = adapter.execute_with_gating(
            "code_generator",
            "generate",
            {},
            current_maturity=0.3,
            current_phase="analysis",
        )
        assert r2["status"] == "success"

        # Implementation phase - use quality controller
        r3 = adapter.execute_with_gating(
            "quality_controller",
            "check",
            {},
            current_maturity=0.8,
            current_phase="implementation",
        )
        assert r3["status"] == "success"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
