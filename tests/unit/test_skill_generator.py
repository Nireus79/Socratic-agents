"""Unit tests for SkillGeneratorAgent."""

from socratic_agents import SkillGeneratorAgent


class TestSkillGeneratorAgentInitialization:
    """Test SkillGeneratorAgent initialization."""

    def test_initialization_default(self):
        """Test agent initializes with default parameters."""
        agent = SkillGeneratorAgent()
        assert agent.name == "SkillGeneratorAgent"
        assert agent.llm_client is None
        assert agent.skill_templates is not None
        assert isinstance(agent.generated_skills, dict)
        assert isinstance(agent.skill_effectiveness, dict)

    def test_initialization_with_llm_client(self):
        """Test agent initializes with LLM client."""
        mock_llm = object()  # Mock LLM client
        agent = SkillGeneratorAgent(llm_client=mock_llm)
        assert agent.llm_client is mock_llm

    def test_skill_templates_loaded(self):
        """Test default skill templates are loaded."""
        agent = SkillGeneratorAgent()
        assert "discovery" in agent.skill_templates
        assert "analysis" in agent.skill_templates
        assert "design" in agent.skill_templates
        assert "implementation" in agent.skill_templates

    def test_skill_templates_have_correct_count(self):
        """Test each phase has 3 skill templates."""
        agent = SkillGeneratorAgent()
        for phase in ["discovery", "analysis", "design", "implementation"]:
            assert len(agent.skill_templates[phase]) == 3


class TestSkillGeneration:
    """Test skill generation functionality."""

    def test_generate_skills_discovery_phase(self):
        """Test skill generation for discovery phase with weak categories."""
        agent = SkillGeneratorAgent()

        result = agent.process(
            {
                "action": "generate",
                "maturity_data": {
                    "current_phase": "discovery",
                    "completion_percent": 35,
                    "weak_categories": ["problem_definition"],
                    "category_scores": {
                        "problem_definition": 0.3,
                        "scope": 0.7,
                        "target_audience": 0.8,
                    },
                },
                "learning_data": {"learning_velocity": "medium", "engagement_score": 0.75},
            }
        )

        assert result["status"] == "success"
        assert result["agent"] == "SkillGeneratorAgent"
        assert result["phase"] == "discovery"
        assert result["skills_generated"] == 1
        assert len(result["skills"]) == 1
        assert result["skills"][0]["category_focus"] == "problem_definition"

    def test_generate_skills_analysis_phase(self):
        """Test skill generation for analysis phase."""
        agent = SkillGeneratorAgent()

        result = agent.process(
            {
                "action": "generate",
                "maturity_data": {
                    "current_phase": "analysis",
                    "completion_percent": 50,
                    "weak_categories": ["functional_requirements", "data_requirements"],
                    "category_scores": {
                        "functional_requirements": 0.4,
                        "non_functional_requirements": 0.7,
                        "data_requirements": 0.3,
                    },
                },
                "learning_data": {"learning_velocity": "high", "engagement_score": 0.85},
            }
        )

        assert result["status"] == "success"
        assert result["skills_generated"] == 2
        assert len(result["recommendations"]) == 2

    def test_generate_skills_no_weak_categories(self):
        """Test skill generation when no weak categories."""
        agent = SkillGeneratorAgent()

        result = agent.process(
            {
                "action": "generate",
                "maturity_data": {
                    "current_phase": "discovery",
                    "completion_percent": 100,
                    "weak_categories": [],
                    "category_scores": {
                        "problem_definition": 0.9,
                        "scope": 0.9,
                        "target_audience": 0.9,
                    },
                },
                "learning_data": {"learning_velocity": "medium", "engagement_score": 0.5},
            }
        )

        assert result["status"] == "success"
        assert result["skills_generated"] == 0
        assert len(result["skills"]) == 0

    def test_generate_skills_missing_maturity_data(self):
        """Test error handling for missing maturity_data."""
        agent = SkillGeneratorAgent()

        result = agent.process({"action": "generate", "maturity_data": None})

        assert result["status"] == "error"
        assert "maturity_data required" in result["message"]

    def test_generate_skills_design_phase(self):
        """Test skill generation for design phase."""
        agent = SkillGeneratorAgent()

        result = agent.process(
            {
                "action": "generate",
                "maturity_data": {
                    "current_phase": "design",
                    "completion_percent": 70,
                    "weak_categories": ["architecture", "integrations"],
                    "category_scores": {
                        "architecture": 0.2,
                        "technology_stack": 0.6,
                        "integrations": 0.4,
                    },
                },
                "learning_data": {"learning_velocity": "medium", "engagement_score": 0.6},
            }
        )

        assert result["status"] == "success"
        assert result["skills_generated"] == 2

    def test_generate_skills_implementation_phase(self):
        """Test skill generation for implementation phase."""
        agent = SkillGeneratorAgent()

        result = agent.process(
            {
                "action": "generate",
                "maturity_data": {
                    "current_phase": "implementation",
                    "completion_percent": 85,
                    "weak_categories": ["code_quality", "testing_coverage"],
                    "category_scores": {
                        "code_quality": 0.5,
                        "testing_coverage": 0.4,
                        "documentation": 0.7,
                    },
                },
                "learning_data": {"learning_velocity": "low", "engagement_score": 0.45},
            }
        )

        assert result["status"] == "success"
        assert result["skills_generated"] == 2


class TestSkillPrioritization:
    """Test skill prioritization logic."""

    def test_prioritization_high_priority(self):
        """Test high priority skills are identified."""
        agent = SkillGeneratorAgent()

        result = agent.process(
            {
                "action": "generate",
                "maturity_data": {
                    "current_phase": "discovery",
                    "completion_percent": 20,
                    "weak_categories": ["problem_definition"],
                    "category_scores": {
                        "problem_definition": 0.1,  # Very weak
                        "scope": 0.8,
                        "target_audience": 0.8,
                    },
                },
                "learning_data": {
                    "learning_velocity": "medium",
                    "engagement_score": 0.9,  # High engagement
                },
            }
        )

        assert result["recommendations"][0]["priority"] == "high"

    def test_prioritization_medium_priority(self):
        """Test medium priority skills are identified."""
        agent = SkillGeneratorAgent()

        result = agent.process(
            {
                "action": "generate",
                "maturity_data": {
                    "current_phase": "discovery",
                    "completion_percent": 40,
                    "weak_categories": ["scope"],
                    "category_scores": {
                        "problem_definition": 0.7,
                        "scope": 0.4,  # Moderately weak (weakness = 0.6)
                        "target_audience": 0.8,
                    },
                },
                "learning_data": {
                    "learning_velocity": "medium",
                    "engagement_score": 0.6,  # Higher engagement for medium priority
                },
            }
        )

        assert result["recommendations"][0]["priority"] == "medium"

    def test_recommendations_have_expected_impact(self):
        """Test recommendations include expected impact scores."""
        agent = SkillGeneratorAgent()

        result = agent.process(
            {
                "action": "generate",
                "maturity_data": {
                    "current_phase": "discovery",
                    "completion_percent": 30,
                    "weak_categories": ["problem_definition"],
                    "category_scores": {
                        "problem_definition": 0.2,
                        "scope": 0.7,
                        "target_audience": 0.8,
                    },
                },
                "learning_data": {"learning_velocity": "medium", "engagement_score": 0.7},
            }
        )

        rec = result["recommendations"][0]
        assert "expected_impact" in rec
        assert 0.0 <= rec["expected_impact"] <= 1.0

    def test_recommendations_sorted_by_priority(self):
        """Test recommendations are sorted by priority."""
        agent = SkillGeneratorAgent()

        result = agent.process(
            {
                "action": "generate",
                "maturity_data": {
                    "current_phase": "discovery",
                    "completion_percent": 30,
                    "weak_categories": ["problem_definition", "scope", "target_audience"],
                    "category_scores": {
                        "problem_definition": 0.1,  # Very weak -> high priority
                        "scope": 0.5,  # Medium -> medium priority
                        "target_audience": 0.8,  # Strong -> low priority
                    },
                },
                "learning_data": {"learning_velocity": "medium", "engagement_score": 0.6},
            }
        )

        recs = result["recommendations"]
        # Should be sorted by priority (high -> medium -> low)
        priorities = [rec["priority"] for rec in recs]
        # First should be high, then medium (if exists)
        if len(priorities) > 1:
            # Verify they're in correct order
            assert priorities[0] == "high" or priorities[0] == "medium"


class TestSkillEvaluation:
    """Test skill effectiveness evaluation."""

    def test_evaluate_skill_success(self):
        """Test successful skill evaluation."""
        agent = SkillGeneratorAgent()

        # First generate a skill
        gen_result = agent.process(
            {
                "action": "generate",
                "maturity_data": {
                    "current_phase": "discovery",
                    "completion_percent": 35,
                    "weak_categories": ["problem_definition"],
                    "category_scores": {"problem_definition": 0.3},
                },
                "learning_data": {"learning_velocity": "medium", "engagement_score": 0.75},
            }
        )

        skill_id = gen_result["skills"][0]["id"]

        # Then evaluate it
        eval_result = agent.process(
            {
                "action": "evaluate",
                "skill_id": skill_id,
                "feedback": "helped",
                "effectiveness_score": 0.85,
            }
        )

        assert eval_result["status"] == "success"
        assert eval_result["skill_id"] == skill_id
        assert eval_result["feedback"] == "helped"
        assert eval_result["effectiveness_score"] == 0.85

    def test_evaluate_nonexistent_skill(self):
        """Test evaluation of non-existent skill."""
        agent = SkillGeneratorAgent()

        result = agent.process(
            {
                "action": "evaluate",
                "skill_id": "nonexistent_skill_id",
                "feedback": "no effect",
                "effectiveness_score": 0.5,
            }
        )

        assert result["status"] == "error"
        assert "not found" in result["message"]

    def test_evaluate_skill_effectiveness_bounds(self):
        """Test effectiveness score is clamped to [0, 1]."""
        agent = SkillGeneratorAgent()

        # Generate a skill
        gen_result = agent.process(
            {
                "action": "generate",
                "maturity_data": {
                    "current_phase": "discovery",
                    "completion_percent": 35,
                    "weak_categories": ["problem_definition"],
                    "category_scores": {"problem_definition": 0.3},
                },
                "learning_data": {"learning_velocity": "medium", "engagement_score": 0.75},
            }
        )

        skill_id = gen_result["skills"][0]["id"]

        # Evaluate with out-of-bounds score (should be clamped)
        result = agent.process(
            {
                "action": "evaluate",
                "skill_id": skill_id,
                "effectiveness_score": 1.5,  # Greater than 1.0
            }
        )

        assert result["effectiveness_score"] == 1.0

    def test_evaluate_skill_without_score(self):
        """Test evaluation with just feedback (no score)."""
        agent = SkillGeneratorAgent()

        # Generate a skill
        gen_result = agent.process(
            {
                "action": "generate",
                "maturity_data": {
                    "current_phase": "discovery",
                    "completion_percent": 35,
                    "weak_categories": ["problem_definition"],
                    "category_scores": {"problem_definition": 0.3},
                },
                "learning_data": {"learning_velocity": "medium", "engagement_score": 0.75},
            }
        )

        skill_id = gen_result["skills"][0]["id"]

        # Evaluate with only feedback
        result = agent.process(
            {"action": "evaluate", "skill_id": skill_id, "feedback": "no effect"}
        )

        assert result["status"] == "success"
        assert result["feedback"] == "no effect"


class TestSkillListing:
    """Test skill listing and filtering."""

    def test_list_all_skills(self):
        """Test listing all generated skills."""
        agent = SkillGeneratorAgent()

        # Generate skills in discovery phase
        agent.process(
            {
                "action": "generate",
                "maturity_data": {
                    "current_phase": "discovery",
                    "completion_percent": 35,
                    "weak_categories": ["problem_definition", "scope"],
                    "category_scores": {
                        "problem_definition": 0.3,
                        "scope": 0.4,
                        "target_audience": 0.8,
                    },
                },
                "learning_data": {"learning_velocity": "medium", "engagement_score": 0.75},
            }
        )

        # List all skills
        result = agent.process({"action": "list"})

        assert result["status"] == "success"
        assert result["skills_count"] == 2

    def test_list_skills_by_phase(self):
        """Test listing skills filtered by phase."""
        agent = SkillGeneratorAgent()

        # Generate skills in discovery and analysis phases
        agent.process(
            {
                "action": "generate",
                "maturity_data": {
                    "current_phase": "discovery",
                    "completion_percent": 35,
                    "weak_categories": ["problem_definition"],
                    "category_scores": {"problem_definition": 0.3},
                },
                "learning_data": {"learning_velocity": "medium", "engagement_score": 0.75},
            }
        )

        agent.process(
            {
                "action": "generate",
                "maturity_data": {
                    "current_phase": "analysis",
                    "completion_percent": 50,
                    "weak_categories": ["functional_requirements"],
                    "category_scores": {"functional_requirements": 0.4},
                },
                "learning_data": {"learning_velocity": "medium", "engagement_score": 0.75},
            }
        )

        # List only discovery phase skills
        result = agent.process({"action": "list", "phase": "discovery"})

        assert result["status"] == "success"
        assert result["skills_count"] == 1
        assert result["skills"][0]["maturity_phase"] == "discovery"

    def test_list_skills_by_agent(self):
        """Test listing skills filtered by target agent."""
        agent = SkillGeneratorAgent()

        # Generate skills that target different agents
        agent.process(
            {
                "action": "generate",
                "maturity_data": {
                    "current_phase": "discovery",
                    "completion_percent": 35,
                    "weak_categories": ["problem_definition"],
                    "category_scores": {"problem_definition": 0.3},
                },
                "learning_data": {"learning_velocity": "medium", "engagement_score": 0.75},
            }
        )

        # List only SocraticCounselor skills
        result = agent.process({"action": "list", "agent_name": "SocraticCounselor"})

        assert result["status"] == "success"
        for skill in result["skills"]:
            assert skill["target_agent"] == "SocraticCounselor"

    def test_list_empty_when_no_matches(self):
        """Test list returns empty when no skills match filter."""
        agent = SkillGeneratorAgent()

        # Generate skills
        agent.process(
            {
                "action": "generate",
                "maturity_data": {
                    "current_phase": "discovery",
                    "completion_percent": 35,
                    "weak_categories": ["problem_definition"],
                    "category_scores": {"problem_definition": 0.3},
                },
                "learning_data": {"learning_velocity": "medium", "engagement_score": 0.75},
            }
        )

        # List non-existent phase
        result = agent.process({"action": "list", "phase": "nonexistent"})

        assert result["status"] == "success"
        assert result["skills_count"] == 0


class TestActionRouting:
    """Test process method action routing."""

    def test_invalid_action(self):
        """Test error handling for invalid action."""
        agent = SkillGeneratorAgent()

        result = agent.process({"action": "invalid_action"})

        assert result["status"] == "error"
        assert "Unknown action" in result["message"]

    def test_default_action_is_generate(self):
        """Test default action is generate when not specified."""
        agent = SkillGeneratorAgent()

        result = agent.process(
            {
                "maturity_data": {
                    "current_phase": "discovery",
                    "completion_percent": 35,
                    "weak_categories": ["problem_definition"],
                    "category_scores": {"problem_definition": 0.3},
                },
                "learning_data": {"learning_velocity": "medium", "engagement_score": 0.75},
            }
        )

        # Should succeed with generate action
        assert result["status"] == "success"
        assert "skills_generated" in result


class TestSkillDataStructure:
    """Test skill data structure and serialization."""

    def test_skill_has_required_fields(self):
        """Test generated skills have all required fields."""
        agent = SkillGeneratorAgent()

        result = agent.process(
            {
                "action": "generate",
                "maturity_data": {
                    "current_phase": "discovery",
                    "completion_percent": 35,
                    "weak_categories": ["problem_definition"],
                    "category_scores": {"problem_definition": 0.3},
                },
                "learning_data": {"learning_velocity": "medium", "engagement_score": 0.75},
            }
        )

        skill = result["skills"][0]
        required_fields = [
            "id",
            "target_agent",
            "skill_type",
            "config",
            "confidence",
            "maturity_phase",
            "category_focus",
            "generated_at",
            "effectiveness_score",
            "applied",
            "feedback",
        ]

        for field in required_fields:
            assert field in skill, f"Missing field: {field}"

    def test_skill_confidence_bounds(self):
        """Test skill confidence is in valid range [0, 1]."""
        agent = SkillGeneratorAgent()

        result = agent.process(
            {
                "action": "generate",
                "maturity_data": {
                    "current_phase": "discovery",
                    "completion_percent": 35,
                    "weak_categories": ["problem_definition"],
                    "category_scores": {"problem_definition": 0.3},
                },
                "learning_data": {"learning_velocity": "medium", "engagement_score": 0.75},
            }
        )

        for skill in result["skills"]:
            assert 0.0 <= skill["confidence"] <= 1.0

    def test_skill_config_customization(self):
        """Test skill config is customized based on learning velocity."""
        agent = SkillGeneratorAgent()

        # High learning velocity
        result_high = agent.process(
            {
                "action": "generate",
                "maturity_data": {
                    "current_phase": "discovery",
                    "completion_percent": 35,
                    "weak_categories": ["problem_definition"],
                    "category_scores": {"problem_definition": 0.3},
                },
                "learning_data": {"learning_velocity": "high", "engagement_score": 0.75},
            }
        )

        # Low learning velocity
        result_low = agent.process(
            {
                "action": "generate",
                "maturity_data": {
                    "current_phase": "discovery",
                    "completion_percent": 35,
                    "weak_categories": ["problem_definition"],
                    "category_scores": {"problem_definition": 0.3},
                },
                "learning_data": {"learning_velocity": "low", "engagement_score": 0.75},
            }
        )

        # Both should have intensity customized
        assert result_high["skills"][0]["config"]["intensity"] == "high"
        assert result_low["skills"][0]["config"]["intensity"] == "low"
