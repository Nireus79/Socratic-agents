"""Learning Agent - Continuous learning and performance improvement."""

from typing import Any, Dict, List, Optional

from .base import BaseAgent


class LearningAgent(BaseAgent):
    """Agent that learns from interactions and improves over time."""

    def __init__(self, llm_client: Optional[Any] = None):
        """Initialize the Learning Agent."""
        super().__init__(name="LearningAgent", llm_client=llm_client)
        self.interactions: List[Dict[str, Any]] = []
        self.patterns: List[str] = []
        # Phase 2: Skill integration fields
        self.skill_effectiveness_history: Dict[str, List[float]] = {}
        self.user_profile = self._initialize_user_profile()
        self.personalization_rules = self._initialize_personalization_rules()

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process learning requests."""
        action = request.get("action", "record")
        if action == "record":
            return self.record_interaction(request.get("interaction"))  # type: ignore[arg-type]
        elif action == "analyze":
            return self.analyze_patterns()
        elif action == "suggest":
            return self.suggest_improvements()
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
