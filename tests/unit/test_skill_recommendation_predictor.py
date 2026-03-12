import pytest

from socratic_agents.analytics.skill_recommendation_predictor import SkillRecommendationPredictor


class TestSkillRecommendationPredictor:
    @pytest.fixture
    def predictor(self):
        return SkillRecommendationPredictor()

    @pytest.fixture
    def user_profile(self):
        return {"engagement_score": 0.8, "learning_velocity": "medium"}

    def test_predict_effectiveness_basic(self, predictor, user_profile):
        skill = {"id": "skill1", "category_focus": "testing"}
        predictor.add_effectiveness_record("skill1", 0.8)

        result = predictor.predict_effectiveness(skill, user_profile)
        assert result["status"] == "success"
        assert "predicted_effectiveness" in result
        assert 0.0 <= result["predicted_effectiveness"] <= 1.0
        assert "confidence" in result

    def test_predict_effectiveness_missing_skill_id(self, predictor, user_profile):
        skill = {"category_focus": "testing"}
        result = predictor.predict_effectiveness(skill, user_profile)
        assert result["status"] == "error"

    def test_rank_skills_by_prediction(self, predictor, user_profile):
        skills = [
            {"id": "skill1", "category_focus": "testing"},
            {"id": "skill2", "category_focus": "testing"},
        ]
        predictor.add_effectiveness_record("skill1", 0.9)
        predictor.add_effectiveness_record("skill2", 0.6)

        ranked = predictor.rank_skills_by_prediction(skills, user_profile)
        assert len(ranked) == 2
        assert ranked[0]["predicted_effectiveness"] >= ranked[1]["predicted_effectiveness"]

    def test_predict_recommendation_success(self, predictor):
        predictor.add_effectiveness_record("skill1", 0.8)
        predictor.add_effectiveness_record("skill1", 0.9)
        predictor.add_effectiveness_record("skill1", 0.3)

        success = predictor.predict_recommendation_success("skill1")
        assert 0.0 <= success <= 1.0
        assert success > 0.5

    def test_identify_high_impact_skills(self, predictor):
        predictor.train_prediction_model(
            [
                {"skill_id": "skill1", "effectiveness": 0.85, "category": "testing"},
                {"skill_id": "skill2", "effectiveness": 0.4, "category": "testing"},
                {"skill_id": "skill3", "effectiveness": 0.9, "category": "quality"},
            ]
        )

        high_impact = predictor.identify_high_impact_skills(min_prediction=0.7)
        assert len(high_impact) == 2
        assert all(s["effectiveness"] >= 0.7 for s in high_impact)

    def test_train_prediction_model(self, predictor):
        training_data = [
            {"skill_id": "skill1", "effectiveness": 0.8, "category": "testing"},
            {"skill_id": "skill2", "effectiveness": 0.6, "category": "quality"},
        ]
        predictor.train_prediction_model(training_data)

        assert "skill1" in predictor.skill_effectiveness_history
        assert "skill2" in predictor.skill_effectiveness_history

    def test_get_prediction_accuracy(self, predictor):
        predictor.prediction_records = [
            {"predicted": 0.8, "actual": 0.8},
            {"predicted": 0.7, "actual": 0.6},
        ]

        accuracy = predictor.get_prediction_accuracy()
        assert "mae" in accuracy
        assert "rmse" in accuracy
        assert "sample_size" in accuracy
        assert accuracy["sample_size"] == 2

    def test_add_effectiveness_record(self, predictor):
        predictor.add_effectiveness_record("skill1", 0.85)
        assert "skill1" in predictor.skill_effectiveness_history
        assert predictor.skill_effectiveness_history["skill1"] == [0.85]

    def test_high_engagement_prediction(self, predictor):
        high_engagement_profile = {"engagement_score": 0.95}
        predictor.add_effectiveness_record("skill1", 0.7)

        result = predictor.predict_effectiveness(
            {"id": "skill1", "category_focus": "general"}, high_engagement_profile
        )
        assert result["components"]["user_engagement"] == 0.95
