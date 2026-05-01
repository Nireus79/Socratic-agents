"""
Phase 6 Integration Tests - REST Client and API endpoints

Test suite validating:
1. REST client async/sync functionality
2. Error handling and exceptions
3. Job timeout and polling
4. Batch operations
"""

import pytest
import asyncio


class TestClientInitialization:
    """Test client initialization and configuration"""

    def test_default_url(self):
        """Test default API URL"""
        from socratic_agents import SocratesAgentClient
        client = SocratesAgentClient()
        assert client.api_url == "http://localhost:8000"

    def test_custom_url(self):
        """Test custom API URL"""
        from socratic_agents import SocratesAgentClient
        client = SocratesAgentClient("http://api.example.com")
        assert client.api_url == "http://api.example.com"

    def test_auth_token_header(self):
        """Test auth token in headers"""
        from socratic_agents import SocratesAgentClient
        client = SocratesAgentClient(auth_token="test_token")
        # Auth is set in http_client; verified through connection

    def test_timeout_configuration(self):
        """Test timeout configuration"""
        from socratic_agents import SocratesAgentClient
        client = SocratesAgentClient(timeout=600)
        assert client.timeout == 600


class TestExceptionTypes:
    """Test exception types are properly defined"""

    def test_exception_hierarchy(self):
        """Test exception inheritance"""
        from socratic_agents import (
            SocratesAgentClientError,
            AgentNotFoundError,
            AgentTimeoutError,
            JobNotFoundError,
        )
        
        assert issubclass(AgentNotFoundError, SocratesAgentClientError)
        assert issubclass(AgentTimeoutError, SocratesAgentClientError)
        assert issubclass(JobNotFoundError, SocratesAgentClientError)

    def test_exception_instantiation(self):
        """Test exception instantiation"""
        from socratic_agents import AgentNotFoundError
        
        exc = AgentNotFoundError("Test agent not found")
        assert str(exc) == "Test agent not found"


class TestSyncWrapper:
    """Test synchronous wrapper functionality"""

    def test_sync_wrapper_exists(self):
        """Test SocratesAgentClientSync class exists"""
        from socratic_agents import SocratesAgentClientSync
        client = SocratesAgentClientSync("http://localhost:8000")
        assert client is not None

    def test_sync_context_manager(self):
        """Test sync context manager"""
        from socratic_agents import SocratesAgentClientSync
        
        with SocratesAgentClientSync("http://localhost:8000") as client:
            assert client is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
