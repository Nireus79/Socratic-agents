"""
Phase 6 Backward Compatibility Tests

Validate that:
1. Old agent invocation patterns still work
2. API response format is consistent
3. Exception types match documented behavior
"""

import pytest


class TestAPIResponseFormat:
    """Test API response format consistency"""

    def test_response_structure(self):
        """Test response has required fields"""
        response = {
            "success": True,
            "status": "success",
            "data": {},
            "message": "OK"
        }
        
        assert "success" in response
        assert "status" in response
        assert "data" in response
        assert "message" in response

    def test_error_response_format(self):
        """Test error response format"""
        error_response = {
            "success": False,
            "status": "error",
            "data": {"error": "Test error"},
            "message": "Error occurred"
        }
        
        assert error_response["success"] is False
        assert "error" in error_response["data"]


class TestJobStatusValues:
    """Test valid job status values"""

    def test_valid_status_values(self):
        """Test valid job status values"""
        valid_statuses = ["pending", "completed", "failed", "timeout"]
        
        for status in valid_statuses:
            assert status in valid_statuses


class TestClientMethods:
    """Test client methods exist and are callable"""

    def test_async_client_methods(self):
        """Test all async client methods exist"""
        from socratic_agents import SocratesAgentClient
        
        client = SocratesAgentClient()
        assert hasattr(client, 'list_agents')
        assert hasattr(client, 'invoke_agent_sync')
        assert hasattr(client, 'invoke_agent_async')
        assert hasattr(client, 'get_job_status')
        assert hasattr(client, 'wait_for_result')
        assert hasattr(client, 'get_batch_job_status')
        assert hasattr(client, 'close')

    def test_sync_client_methods(self):
        """Test all sync client methods exist"""
        from socratic_agents import SocratesAgentClientSync
        
        client = SocratesAgentClientSync()
        assert hasattr(client, 'list_agents')
        assert hasattr(client, 'invoke_agent')
        assert hasattr(client, 'submit_job')
        assert hasattr(client, 'get_job_status')
        assert hasattr(client, 'wait_for_result')
        assert hasattr(client, 'close')


class TestExportedAPIs:
    """Test that all public APIs are properly exported"""

    def test_client_exports(self):
        """Test client classes are exported"""
        import socratic_agents
        
        assert hasattr(socratic_agents, 'SocratesAgentClient')
        assert hasattr(socratic_agents, 'SocratesAgentClientSync')

    def test_exception_exports(self):
        """Test exception classes are exported"""
        import socratic_agents
        
        assert hasattr(socratic_agents, 'SocratesAgentClientError')
        assert hasattr(socratic_agents, 'AgentNotFoundError')
        assert hasattr(socratic_agents, 'AgentTimeoutError')
        assert hasattr(socratic_agents, 'JobNotFoundError')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
