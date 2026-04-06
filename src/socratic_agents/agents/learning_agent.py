"""Learning Agent - Continuous learning and performance improvement.

Integrates with socratic-learning library to provide:
- Learning analytics and pattern detection
- User profile building and metrics
- Phase maturity assessment
- Personalization and recommendations
- Interaction logging and tracking
"""

from typing import Any, Dict, List, Optional
import logging

from .base import BaseAgent

try:
    from socratic_learning.analytics.learning_engine import LearningEngine, UserProfile
    from socratic_learning.analytics.maturity_calculator import MaturityCalculator
    from socratic_learning.analytics.pattern_detector import PatternDetector
    from socratic_learning.analytics.metrics_collector import MetricsCollector
    from socratic_learning.recommendations.engine import RecommendationEngine
    from socratic_learning.storage.sqlite_store import SQLiteLearningStore
    SOCRATIC_LEARNING_AVAILABLE = True
except ImportError:
    SOCRATIC_LEARNING_AVAILABLE = False


logger = logging.getLogger(__name__)


class LearningAgent(BaseAgent):
    """Agent that learns from interactions and improves over time."""

    def __init__(
        self,
        llm_client: Optional[Any] = None,
        database_path: str = ":memory:",
    ):
        """
        Initialize the Learning Agent.

        Args:
            llm_client: Optional LLM client for enhanced analytics
            database_path: Path to SQLite database for persistence
        """
        super().__init__(name="LearningAgent", llm_client=llm_client)
        self.interactions: List[Dict[str, Any]] = []
        self.patterns: List[str] = []

        # Initialize socratic-learning components if available
        self.use_full_learning = SOCRATIC_LEARNING_AVAILABLE
        if self.use_full_learning:
            try:
                self.store = SQLiteLearningStore(database_path)
                self.learning_engine = LearningEngine(logger_instance=logger)
                self.maturity_calculator = MaturityCalculator()
                self.metrics_collector = MetricsCollector(store=self.store)
                self.recommendation_engine = RecommendationEngine()
                self.pattern_detector = PatternDetector(self.store)
                logger.debug("Full socratic-learning components initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize learning components: {e}")
                self.use_full_learning = False

        # Skill integration fields
        self.skill_effectiveness_history: Dict[str, List[float]] = {}
        self.user_profile = self._initialize_user_profile()
        self.personalization_rules = self._initialize_personalization_rules()

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process learning requests.

        Supported actions:
        - record: Record an interaction
        - analyze: Analyze patterns
        - suggest: Suggest improvements
        - metrics: Calculate learning metrics
        - assess_maturity: Assess phase maturity
        - patterns: Detect learning patterns
        - recommend: Generate recommendations
        - personalize_skills: Personalize skills
        - track_feedback: Track skill feedback
        - get_profile: Get user profile
        """
        action = request.get("action", "record")

        if action == "record":
            return self.record_interaction(request.get("interaction"))  # type: ignore[arg-type]
        elif action == "analyze":
            return self.analyze_patterns()
        elif action == "suggest":
            return self.suggest_improvements()
        elif action == "metrics":
            return self.calculate_learning_metrics(request.get("user_id", "user"))  # type: ignore[arg-type]
        elif action == "assess_maturity":
            return self.assess_phase_maturity(
                request.get("phase", "discovery"),  # type: ignore[arg-type]
                request.get("phase_specs", []),  # type: ignore[arg-type]
            )
        elif action == "patterns":
            return self.detect_learning_patterns(request.get("agent_name"))  # type: ignore[arg-type]
        elif action == "recommend":
            return self.generate_recommendations(request.get("user_id", "user"))  # type: ignore[arg-type]
        elif action == "personalize_skills":
            return self.personalize_skills(
                request.get("skills", []),  # type: ignore[arg-type]
                request.get("user_profile", self.user_profile),  # type: ignore[arg-type]
            )
        elif action == "track_feedback":
            return self.track_skill_feedback(
                request.get("skill_id"),  # type: ignore[arg-type]
                request.get("feedback"),  # type: ignore[arg-type]
            )
        elif action == "get_profile":
            return self.get_user_learning_profile()
        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    def record_interaction(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """Record an interaction for learning."""
        if not interaction:
            return {"status": "error", "message": "Interaction required"}
        self.interactions.append({"data": interaction})
        return {
            "status": "success",
            "agent": self.name,
            "recorded": True,
            "total_interactions": len(self.interactions),
        }

    def analyze_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in recorded interactions."""
        if not self.interactions:
            return {
                "status": "success",
                "agent": self.name,
                "patterns": [],
                "message": "No interactions recorded",
            }
        self.patterns = [
            f"{len(self.interactions)} interactions recorded",
            "Learning system active",
        ]
        return {
            "status": "success",
            "agent": self.name,
            "patterns_found": len(self.patterns),
            "patterns": self.patterns,
        }

    def suggest_improvements(self) -> Dict[str, Any]:
        """Suggest improvements based on learning."""
        suggestions = [
            "Record more interactions for patterns",
            "Analyze recent interactions",
            "Share learnings with agents",
        ]
        return {"status": "success", "agent": self.name, "suggestions": suggestions}

    def get_user_learning_profile(self) -> Dict[str, Any]:
        """
        Get the current user's learning profile.

        Returns characteristics about how the user learns and prefers to work.

        Returns:
            Dictionary with learning characteristics
        """
        return self.user_profile

    def personalize_skills(
        self, skills: List[Dict[str, Any]], user_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Personalize skill recommendations based on user learning profile.

        Adjusts priority, difficulty, and presentation of skills based on
        user's learning velocity, engagement, and historical patterns.

        Args:
            skills: List of skill dictionaries to personalize
            user_profile: User's learning profile (uses self.user_profile if None)

        Returns:
            Personalized and prioritized skills
        """
        if not skills:
            return {
                "status": "success",
                "agent": self.name,
                "personalized_skills": [],
            }

        profile = user_profile or self.user_profile
        learning_velocity = profile.get("learning_velocity", "medium")
        engagement = profile.get("engagement_score", 0.5)

        personalized = []
        for skill in skills:
            personalized_skill = skill.copy()

            # Adjust difficulty based on learning velocity
            if learning_velocity == "high":
                personalized_skill["difficulty"] = "advanced"
                personalized_skill["confidence_boost"] = 1.2
            elif learning_velocity == "low":
                personalized_skill["difficulty"] = "beginner"
                personalized_skill["confidence_boost"] = 0.8
            else:
                personalized_skill["difficulty"] = "intermediate"
                personalized_skill["confidence_boost"] = 1.0

            # Adjust priority based on engagement
            original_priority = skill.get("priority", "medium")
            if engagement > 0.7 and original_priority in ["high", "medium"]:
                personalized_skill["personalized_priority"] = "high"
            elif engagement < 0.4 and original_priority == "high":
                personalized_skill["personalized_priority"] = "medium"
            else:
                personalized_skill["personalized_priority"] = original_priority

            # Add personalization metadata
            personalized_skill["personalization_reason"] = (
                f"Adjusted for {learning_velocity} velocity, " f"{engagement:.0%} engagement"
            )

            personalized.append(personalized_skill)

        # Sort by personalized priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        personalized.sort(
            key=lambda s: priority_order.get(s.get("personalized_priority", "low"), 3)
        )

        return {
            "status": "success",
            "agent": self.name,
            "personalized_skills": personalized,
            "personalization_profile": profile,
        }

    def track_skill_feedback(self, skill_id: str, feedback: str) -> Dict[str, Any]:
        """
        Track effectiveness feedback for a skill.

        Records how well a skill worked for the user, updating learning
        metrics for future personalization.

        Args:
            skill_id: ID of the skill
            feedback: Feedback type ('helped', 'no_effect', 'harmful')

        Returns:
            Status of feedback tracking
        """
        if not skill_id:
            return {"status": "error", "message": "Skill ID required"}

        # Convert feedback to effectiveness score
        feedback_scores = {"helped": 0.8, "no_effect": 0.5, "harmful": 0.2}
        effectiveness = feedback_scores.get(feedback, 0.5)

        # Track history
        if skill_id not in self.skill_effectiveness_history:
            self.skill_effectiveness_history[skill_id] = []

        self.skill_effectiveness_history[skill_id].append(effectiveness)

        # Update user profile based on trends
        self._update_user_profile_from_feedback(skill_id, effectiveness)

        # Record interaction
        self.record_interaction(
            {
                "type": "skill_feedback",
                "skill_id": skill_id,
                "feedback": feedback,
                "effectiveness": effectiveness,
            }
        )

        return {
            "status": "success",
            "agent": self.name,
            "skill_id": skill_id,
            "feedback": feedback,
            "effectiveness_score": effectiveness,
            "history_length": len(self.skill_effectiveness_history.get(skill_id, [])),
        }

    def predict_skill_effectiveness(self, skill: Dict[str, Any]) -> float:
        """
        Predict skill effectiveness using historical data.

        Uses past skill application results to estimate how well a new skill
        will work for the user.

        Args:
            skill: Skill dictionary to predict for

        Returns:
            Predicted effectiveness (0.0-1.0)
        """
        skill_id = skill.get("id")

        # If we have history for this skill, use it
        if skill_id and skill_id in self.skill_effectiveness_history:
            history = self.skill_effectiveness_history[skill_id]
            if history:
                avg_effectiveness = sum(history) / len(history)
                return min(1.0, avg_effectiveness * 1.1)  # Slight optimism boost

        # Otherwise, use skill confidence and user profile
        base_confidence = skill.get("confidence", 0.7)
        engagement_boost = self.user_profile.get("engagement_score", 0.5)

        predicted = base_confidence * (0.8 + (engagement_boost * 0.2))
        return min(1.0, max(0.0, predicted))

    def _initialize_user_profile(self) -> Dict[str, Any]:
        """Initialize user learning profile with defaults."""
        return {
            "learning_velocity": "medium",
            "engagement_score": 0.6,
            "preferred_skill_difficulty": "intermediate",
            "skill_adoption_speed": "medium",
            "preferred_learning_style": "interactive",
            "total_interactions": 0,
            "total_skills_applied": 0,
        }

    def _initialize_personalization_rules(self) -> Dict[str, Any]:
        """Initialize personalization rules."""
        return {
            "boost_high_engagement": True,
            "adjust_difficulty_velocity": True,
            "track_skill_effectiveness": True,
            "recommend_similar_skills": True,
            "penalize_harmful_skills": True,
        }

    def _update_user_profile_from_feedback(self, skill_id: str, effectiveness: float) -> None:
        """Update user profile based on skill feedback."""
        # Adjust engagement based on effectiveness
        if effectiveness > 0.7:
            self.user_profile["engagement_score"] = min(
                1.0, self.user_profile["engagement_score"] + 0.05
            )
        elif effectiveness < 0.3:
            self.user_profile["engagement_score"] = max(
                0.0, self.user_profile["engagement_score"] - 0.05
            )

        self.user_profile["total_skills_applied"] += 1

    # ===== Full Learning Analytics Methods =====

    def calculate_learning_metrics(self, user_id: str) -> Dict[str, Any]:
        """
        Calculate comprehensive learning metrics for a user.

        Uses socratic-learning to compute engagement, velocity, and experience level.

        Args:
            user_id: ID of the user

        Returns:
            Dictionary with learning metrics
        """
        if not self.use_full_learning:
            # Fallback: basic metrics
            return {
                "status": "success",
                "mode": "basic",
                "engagement_score": self.user_profile.get("engagement_score", 0.5),
                "learning_velocity": self.user_profile.get("learning_velocity", "medium"),
                "experience_level": self._estimate_experience_level(),
                "interactions_count": len(self.interactions),
            }

        try:
            # Extract metrics from interactions
            questions_asked = [
                {"times_asked": 1, "times_answered_well": 1 if i.get("success", False) else 0}
                for i in self.interactions
                if i.get("type") == "question"
            ]
            responses_quality = [
                i.get("quality_score", 0.5) for i in self.interactions if i.get("response")
            ]
            topic_interactions = [
                i.get("topic", "general") for i in self.interactions
            ]

            # Build profile using learning engine
            profile = self.learning_engine.build_user_profile(
                user_id=user_id,
                questions_asked=questions_asked,
                responses_quality=responses_quality,
                topic_interactions=topic_interactions,
                projects_completed=0,
            )

            # Calculate metrics
            metrics = self.learning_engine.calculate_learning_metrics(profile)
            metrics["status"] = "success"
            metrics["mode"] = "full"
            metrics["total_interactions"] = len(self.interactions)

            return metrics

        except Exception as e:
            logger.warning(f"Failed to calculate full learning metrics: {e}")
            return {
                "status": "error",
                "message": f"Metrics calculation failed: {str(e)}",
            }

    def assess_phase_maturity(
        self,
        phase: str,
        phase_specs: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Assess maturity of a project phase.

        Uses socratic-learning's MaturityCalculator for confidence-weighted assessment.

        Args:
            phase: Phase name (discovery, analysis, design, implementation)
            phase_specs: List of specifications with categories and values

        Returns:
            Maturity assessment with readiness status
        """
        if not self.use_full_learning:
            # Fallback: basic maturity
            return {
                "status": "success",
                "phase": phase,
                "maturity_percentage": 50.0,
                "is_ready": False,
                "mode": "basic",
            }

        try:
            maturity = self.maturity_calculator.calculate_phase_maturity(
                phase_specs=phase_specs,
                phase=phase,
            )
            maturity["status"] = "success"
            maturity["mode"] = "full"
            return maturity

        except Exception as e:
            logger.warning(f"Failed to assess phase maturity: {e}")
            return {
                "status": "error",
                "message": f"Maturity assessment failed: {str(e)}",
            }

    def detect_learning_patterns(self, agent_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Detect patterns in agent interactions.

        Identifies error patterns, success patterns, and performance anomalies.

        Args:
            agent_name: Optional agent name to filter patterns

        Returns:
            Dictionary with detected patterns
        """
        if not self.use_full_learning:
            # Fallback: basic patterns
            return {
                "status": "success",
                "patterns": self.patterns,
                "pattern_count": len(self.patterns),
                "mode": "basic",
            }

        try:
            # Detect different pattern types
            error_patterns = self.pattern_detector.detect_error_patterns(agent_name)
            success_patterns = self.pattern_detector.detect_success_patterns(agent_name)
            perf_patterns = self.pattern_detector.detect_performance_patterns(agent_name)

            all_patterns = error_patterns + success_patterns + perf_patterns

            patterns_data = [
                {
                    "type": p.pattern_type,
                    "name": p.name,
                    "description": p.description,
                    "confidence": p.confidence,
                    "occurrence_count": p.occurrence_count,
                }
                for p in all_patterns
            ]

            return {
                "status": "success",
                "patterns": patterns_data,
                "pattern_count": len(patterns_data),
                "error_patterns": len(error_patterns),
                "success_patterns": len(success_patterns),
                "performance_patterns": len(perf_patterns),
                "mode": "full",
            }

        except Exception as e:
            logger.warning(f"Failed to detect patterns: {e}")
            return {
                "status": "error",
                "message": f"Pattern detection failed: {str(e)}",
            }

    def generate_recommendations(self, user_id: str) -> Dict[str, Any]:
        """
        Generate personalized learning recommendations.

        Uses socratic-learning to generate skills and learning suggestions.

        Args:
            user_id: User ID to generate recommendations for

        Returns:
            Dictionary with recommendations
        """
        if not self.use_full_learning:
            # Fallback: basic suggestions
            return {
                "status": "success",
                "recommendations": self._get_basic_recommendations(),
                "mode": "basic",
            }

        try:
            # Get learning hints from engine
            profile = self._build_learning_profile(user_id)
            metrics = self.learning_engine.calculate_learning_metrics(profile)
            hints = self.learning_engine.get_personalization_hints(profile, metrics)

            return {
                "status": "success",
                "recommendations": hints,
                "recommendation_count": len(hints),
                "based_on_metrics": metrics,
                "mode": "full",
            }

        except Exception as e:
            logger.warning(f"Failed to generate recommendations: {e}")
            return {
                "status": "error",
                "message": f"Recommendation generation failed: {str(e)}",
            }

    def _estimate_experience_level(self) -> str:
        """Estimate user experience level based on interaction count."""
        interaction_count = len(self.interactions)
        if interaction_count < 10:
            return "beginner"
        elif interaction_count < 50:
            return "intermediate"
        else:
            return "advanced"

    def _get_basic_recommendations(self) -> List[str]:
        """Get basic learning recommendations."""
        level = self._estimate_experience_level()
        if level == "beginner":
            return [
                "Focus on fundamental concepts",
                "Practice basic examples",
                "Build confidence with simple tasks",
            ]
        elif level == "intermediate":
            return [
                "Explore advanced patterns",
                "Apply knowledge to complex problems",
                "Mentor beginners",
            ]
        else:
            return [
                "Pursue specialized knowledge",
                "Share expertise with team",
                "Explore emerging techniques",
            ]

    def _build_learning_profile(self, user_id: str) -> Any:
        """Build learning profile from interactions."""
        questions_asked = [
            {"times_asked": 1, "times_answered_well": 1 if i.get("success") else 0}
            for i in self.interactions
            if i.get("type") == "question"
        ]
        responses_quality = [
            i.get("quality_score", 0.5) for i in self.interactions if i.get("response")
        ]
        topics = [i.get("topic", "general") for i in self.interactions]

        return self.learning_engine.build_user_profile(
            user_id=user_id,
            questions_asked=questions_asked,
            responses_quality=responses_quality,
            topic_interactions=topics,
            projects_completed=0,
        )
