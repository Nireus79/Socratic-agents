"""
Tests for specs extraction with status and confidence scoring.
"""

import pytest
from unittest.mock import Mock
from socratic_agents.agents.socratic_counselor import SocraticCounselor


class TestSpecsExtractionStatus:
    """Test specs extraction with status and confidence scoring."""

    def test_empty_response_returns_empty_status(self):
        """Empty response should return empty status with 0 confidence."""
        counselor = SocraticCounselor()
        result = counselor._extract_insights_only({"response": ""})
        
        assert result["status"] == "empty"
        assert result["confidence_score"] == 0.0
        assert result["metadata"]["item_count"] == 0

    def test_llm_extraction_success(self):
        """LLM extraction with 8+ items returns success status."""
        counselor = SocraticCounselor()
        counselor.llm_client = Mock()
        
        json_response = '{"goals": ["g1", "g2", "g3"], "requirements": ["r1", "r2", "r3"], "gaps": ["gap1", "gap2"], "decisions": ["d1", "d2"], "questions": ["q1", "q2"]}'
        counselor.llm_client.generate_response.return_value = json_response
        
        result = counselor._extract_insights_only({"response": "test"})
        
        assert result["status"] == "success"
        assert result["confidence_score"] > 0.85
        assert result["metadata"]["item_count"] == 12

    def test_llm_extraction_partial(self):
        """LLM extraction with 3-7 items returns partial status."""
        counselor = SocraticCounselor()
        counselor.llm_client = Mock()
        
        json_response = '{"goals": ["g1"], "requirements": ["r1", "r2"], "gaps": [], "decisions": [], "questions": []}'
        counselor.llm_client.generate_response.return_value = json_response
        
        result = counselor._extract_insights_only({"response": "test"})
        
        assert result["status"] == "partial"
        assert result["confidence_score"] == 0.6

    def test_specs_structure_normalized(self):
        """Specs should always have standard keys."""
        counselor = SocraticCounselor()
        counselor.llm_client = Mock()
        
        json_response = '{"goals": ["g1"], "other": "ignored"}'
        counselor.llm_client.generate_response.return_value = json_response
        
        result = counselor._extract_insights_only({"response": "test"})
        
        expected_keys = {"goals", "requirements", "gaps", "decisions", "questions"}
        assert set(result["specs"].keys()) == expected_keys

    def test_confidence_score_range(self):
        """Confidence score should be between 0.0 and 1.0."""
        counselor = SocraticCounselor()
        counselor.llm_client = Mock()
        
        json_response = '{"goals": ["g1"], "requirements": ["r1"], "gaps": [], "decisions": [], "questions": []}'
        counselor.llm_client.generate_response.return_value = json_response
        
        result = counselor._extract_insights_only({"response": "test"})
        
        assert 0.0 <= result["confidence_score"] <= 1.0

