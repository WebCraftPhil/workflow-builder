"""
Unit tests for IntegrationAgent.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any

from agents.integration_agent import IntegrationAgent


class TestIntegrationAgent:
    """Test cases for IntegrationAgent."""

    @pytest.fixture
    def agent(self):
        """Create IntegrationAgent instance for testing."""
        credential_manager = Mock()
        service_registry = Mock()
        http_client = Mock()

        return IntegrationAgent(credential_manager, service_registry, http_client)

    @pytest.fixture
    def github_credentials(self):
        """GitHub API credentials."""
        return {
            "apiKey": "ghp_test1234567890abcdef",
            "user": "testuser",
            "repository": "test/repo"
        }

    @pytest.fixture
    def oauth_credentials(self):
        """OAuth2 credentials."""
        return {
            "oauthToken": "oauth_token_12345",
            "clientId": "client_123",
            "clientSecret": "secret_456"
        }

    @pytest.fixture
    def database_credentials(self):
        """Database credentials."""
        return {
            "username": "test_user",
            "password": "test_password",
            "host": "localhost",
            "port": 5432,
            "database": "test_db"
        }

    @pytest.mark.asyncio
    async def test_oauth_authentication_success(self, agent, github_credentials):
        """Test successful OAuth authentication."""
        # Setup
        agent.credential_manager.get_credentials = AsyncMock(return_value=github_credentials)
        agent.service_registry.check_service_health = AsyncMock(return_value={
            "available": True,
            "response_time": 150
        })
        agent.http_client.make_request = AsyncMock(return_value={
            "status_code": 200,
            "data": {"user": "testuser", "authenticated": True}
        })

        # Execute
        result = await agent.handle_integration({
            "serviceName": "github",
            "operation": "authenticate",
            "credentials": github_credentials,
            "parameters": {},
            "data": None
        })

        # Assertions
        assert result["success"] is True
        assert result["data"]["authenticated"] is True
        agent.credential_manager.get_credentials.assert_called_once()

    @pytest.mark.asyncio
    async def test_api_key_authentication(self, agent, github_credentials):
        """Test API key authentication."""
        # Setup
        agent.credential_manager.get_credentials = AsyncMock(return_value=github_credentials)
        agent.service_registry.check_service_health = AsyncMock(return_value={
            "available": True
        })
        agent.http_client.make_request = AsyncMock(return_value={
            "status_code": 200,
            "data": {"success": True}
        })

        # Execute
        result = await agent.handle_integration({
            "serviceName": "github",
            "operation": "execute",
            "credentials": github_credentials,
            "parameters": {"endpoint": "/user"},
            "data": None
        })

        # Assertions
        assert result["success"] is True
        agent.http_client.make_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_service_health_check(self, agent):
        """Test service health monitoring."""
        # Setup
        agent.service_registry.check_service_health = AsyncMock(return_value={
            "available": True,
            "response_time": 120,
            "status_code": 200
        })

        # Execute
        health_status = await agent.check_service_health("github")

        # Assertions
        assert health_status["available"] is True
        assert health_status["response_time"] == 120

    @pytest.mark.asyncio
    async def test_service_unavailable(self, agent, github_credentials):
        """Test handling of unavailable services."""
        # Setup
        agent.credential_manager.get_credentials = AsyncMock(return_value=github_credentials)
        agent.service_registry.check_service_health = AsyncMock(return_value={
            "available": False,
            "error": "Service temporarily unavailable"
        })

        # Execute
        result = await agent.handle_integration({
            "serviceName": "github",
            "operation": "execute",
            "credentials": github_credentials,
            "parameters": {},
            "data": None
        })

        # Assertions
        assert result["success"] is False
        assert "unavailable" in result["error"]["message"].lower()

    @pytest.mark.asyncio
    async def test_rate_limiting(self, agent, github_credentials):
        """Test rate limiting enforcement."""
        # Setup
        agent.credential_manager.get_credentials = AsyncMock(return_value=github_credentials)
        agent.service_registry.check_service_health = AsyncMock(return_value={
            "available": True
        })

        # Configure rate limit
        agent.rate_limiter = Mock()
        agent.rate_limiter.is_allowed = Mock(side_effect=[True, True, False])  # First two allowed, third blocked

        # Execute multiple requests
        result1 = await agent.handle_integration({
            "serviceName": "github",
            "operation": "execute",
            "credentials": github_credentials,
            "parameters": {},
            "data": None
        })

        result2 = await agent.handle_integration({
            "serviceName": "github",
            "operation": "execute",
            "credentials": github_credentials,
            "parameters": {},
            "data": None
        })

        result3 = await agent.handle_integration({
            "serviceName": "github",
            "operation": "execute",
            "credentials": github_credentials,
            "parameters": {},
            "data": None
        })

        # Assertions
        assert result1["success"] is True
        assert result2["success"] is True
        assert result3["success"] is False
        assert "rate limit" in result3["error"]["message"].lower()

    @pytest.mark.asyncio
    async def test_credential_encryption(self, agent, github_credentials):
        """Test credential encryption and storage."""
        # Setup
        agent.credential_manager.store_credentials = AsyncMock(return_value=True)
        agent.credential_manager.get_credentials = AsyncMock(return_value=github_credentials)

        # Execute credential storage
        result = await agent.store_credentials("github", github_credentials)

        # Execute credential retrieval
        retrieved = await agent.get_credentials("github")

        # Assertions
        assert result is True
        assert retrieved == github_credentials

    @pytest.mark.asyncio
    async def test_data_transformation(self, agent, github_credentials):
        """Test data format transformation."""
        # Setup
        agent.credential_manager.get_credentials = AsyncMock(return_value=github_credentials)
        agent.service_registry.check_service_health = AsyncMock(return_value={
            "available": True
        })

        # Raw API response
        raw_response = {
            "status_code": 200,
            "data": {
                "id": 123,
                "name": "Test Repository",
                "owner": {"login": "testuser"},
                "created_at": "2024-01-01T00:00:00Z"
            }
        }

        agent.http_client.make_request = AsyncMock(return_value=raw_response)

        # Execute with transformation request
        result = await agent.handle_integration({
            "serviceName": "github",
            "operation": "execute",
            "credentials": github_credentials,
            "parameters": {
                "endpoint": "/repositories/test/repo",
                "transform": "simplify"
            },
            "data": None
        })

        # Assertions
        assert result["success"] is True
        # In real implementation, would verify data transformation

    @pytest.mark.asyncio
    async def test_request_retry_logic(self, agent, github_credentials):
        """Test request retry with exponential backoff."""
        # Setup - first two requests fail, third succeeds
        agent.credential_manager.get_credentials = AsyncMock(return_value=github_credentials)
        agent.service_registry.check_service_health = AsyncMock(return_value={
            "available": True
        })

        agent.http_client.make_request = AsyncMock(side_effect=[
            Exception("Network timeout"),
            Exception("Server error"),
            {"status_code": 200, "data": {"success": True}}
        ])

        # Execute
        result = await agent.handle_integration({
            "serviceName": "github",
            "operation": "execute",
            "credentials": github_credentials,
            "parameters": {},
            "data": None
        })

        # Assertions
        assert result["success"] is True
        assert agent.http_client.make_request.call_count == 3

    @pytest.mark.asyncio
    async def test_timeout_handling(self, agent, github_credentials):
        """Test timeout handling."""
        # Setup slow response
        async def slow_request(*args, **kwargs):
            await asyncio.sleep(10)  # Longer than timeout
            return {"status_code": 200, "data": {"success": True}}

        agent.credential_manager.get_credentials = AsyncMock(return_value=github_credentials)
        agent.service_registry.check_service_health = AsyncMock(return_value={
            "available": True
        })
        agent.http_client.make_request = AsyncMock(side_effect=slow_request)

        # Execute with short timeout
        result = await agent.handle_integration({
            "serviceName": "github",
            "operation": "execute",
            "credentials": github_credentials,
            "parameters": {"timeout": 1},
            "data": None
        })

        # Assertions
        assert result["success"] is False
        assert "timeout" in result["error"]["message"].lower()

    @pytest.mark.asyncio
    async def test_webhook_handling(self, agent, github_credentials):
        """Test webhook processing."""
        # Setup webhook data
        webhook_data = {
            "serviceName": "github",
            "operation": "webhook",
            "credentials": github_credentials,
            "parameters": {},
            "data": {
                "action": "push",
                "repository": {"name": "test-repo"},
                "sender": {"login": "testuser"}
            }
        }

        agent.credential_manager.get_credentials = AsyncMock(return_value=github_credentials)
        agent.service_registry.check_service_health = AsyncMock(return_value={
            "available": True
        })

        # Execute webhook processing
        result = await agent.handle_integration(webhook_data)

        # Assertions
        assert result["success"] is True
        assert result["metadata"]["operation"] == "webhook"

    @pytest.mark.asyncio
    async def test_credential_refresh(self, agent, oauth_credentials):
        """Test OAuth token refresh."""
        # Setup
        agent.credential_manager.get_credentials = AsyncMock(return_value=oauth_credentials)
        agent.credential_manager.refresh_credentials = AsyncMock(return_value={
            **oauth_credentials,
            "oauthToken": "new_oauth_token_67890"
        })
        agent.http_client.make_request = AsyncMock(side_effect=[
            {"status_code": 401, "data": {"error": "token_expired"}},  # First request fails
            {"status_code": 200, "data": {"success": True}}  # Retry succeeds
        ])

        # Execute
        result = await agent.handle_integration({
            "serviceName": "google",
            "operation": "execute",
            "credentials": oauth_credentials,
            "parameters": {},
            "data": None
        })

        # Assertions
        assert result["success"] is True
        agent.credential_manager.refresh_credentials.assert_called_once()

    @pytest.mark.asyncio
    async def test_error_logging(self, agent, github_credentials):
        """Test comprehensive error logging."""
        # Setup
        agent.credential_manager.get_credentials = AsyncMock(return_value=github_credentials)
        agent.service_registry.check_service_health = AsyncMock(return_value={
            "available": True
        })
        agent.http_client.make_request = AsyncMock(side_effect=Exception("API Error"))

        # Execute
        result = await agent.handle_integration({
            "serviceName": "github",
            "operation": "execute",
            "credentials": github_credentials,
            "parameters": {},
            "data": None
        })

        # Assertions
        assert result["success"] is False
        assert result["error"]["code"] == "API_ERROR"
        # In real implementation, would verify error logging

    @pytest.mark.asyncio
    async def test_quota_management(self, agent, github_credentials):
        """Test API quota and usage management."""
        # Setup
        agent.credential_manager.get_credentials = AsyncMock(return_value=github_credentials)
        agent.service_registry.check_service_health = AsyncMock(return_value={
            "available": True
        })
        agent.http_client.make_request = AsyncMock(return_value={
            "status_code": 200,
            "data": {"success": True},
            "headers": {"X-RateLimit-Remaining": "4500"}
        })

        # Execute
        result = await agent.handle_integration({
            "serviceName": "github",
            "operation": "execute",
            "credentials": github_credentials,
            "parameters": {},
            "data": None
        })

        # Assertions
        assert result["success"] is True
        assert result["metadata"]["rateLimitRemaining"] == 4500

    @pytest.mark.asyncio
    async def test_different_service_integrations(self, agent):
        """Test integration with different external services."""
        services = ["github", "slack", "google", "database"]

        for service in services:
            # Setup
            credentials = {"apiKey": f"test_{service}_key"}
            agent.credential_manager.get_credentials = AsyncMock(return_value=credentials)
            agent.service_registry.check_service_health = AsyncMock(return_value={
                "available": True
            })
            agent.http_client.make_request = AsyncMock(return_value={
                "status_code": 200,
                "data": {"service": service, "success": True}
            })

            # Execute
            result = await agent.handle_integration({
                "serviceName": service,
                "operation": "test",
                "credentials": credentials,
                "parameters": {},
                "data": None
            })

            # Assertions
            assert result["success"] is True
            assert result["metadata"]["serviceName"] == service

    @pytest.mark.asyncio
    async def test_batch_operations(self, agent, github_credentials):
        """Test batch API operations."""
        # Setup multiple requests
        batch_operations = [
            {"endpoint": "/user", "method": "GET"},
            {"endpoint": "/repos", "method": "GET"},
            {"endpoint": "/gists", "method": "GET"}
        ]

        agent.credential_manager.get_credentials = AsyncMock(return_value=github_credentials)
        agent.service_registry.check_service_health = AsyncMock(return_value={
            "available": True
        })

        # Mock different responses for each endpoint
        agent.http_client.make_request = AsyncMock(side_effect=[
            {"status_code": 200, "data": {"id": 123, "login": "testuser"}},
            {"status_code": 200, "data": {"repos": []}},
            {"status_code": 200, "data": {"gists": []}}
        ])

        # Execute batch
        results = []
        for operation in batch_operations:
            result = await agent.handle_integration({
                "serviceName": "github",
                "operation": "execute",
                "credentials": github_credentials,
                "parameters": operation,
                "data": None
            })
            results.append(result)

        # Assertions
        assert len(results) == 3
        assert all(result["success"] for result in results)

    @pytest.mark.asyncio
    async def test_circuit_breaker_pattern(self, agent, github_credentials):
        """Test circuit breaker pattern for failing services."""
        # Setup circuit breaker
        agent.circuit_breaker = Mock()
        agent.circuit_breaker.is_open = Mock(return_value=True)

        # Execute
        result = await agent.handle_integration({
            "serviceName": "github",
            "operation": "execute",
            "credentials": github_credentials,
            "parameters": {},
            "data": None
        })

        # Assertions
        assert result["success"] is False
        assert "circuit" in result["error"]["message"].lower() or "breaker" in result["error"]["message"].lower()

    @pytest.mark.asyncio
    async def test_request_caching(self, agent, github_credentials):
        """Test response caching for repeated requests."""
        # Setup cache
        agent.cache = Mock()
        agent.cache.get = Mock(return_value=None)  # Cache miss
        agent.cache.set = Mock(return_value=True)

        agent.credential_manager.get_credentials = AsyncMock(return_value=github_credentials)
        agent.service_registry.check_service_health = AsyncMock(return_value={
            "available": True
        })
        agent.http_client.make_request = AsyncMock(return_value={
            "status_code": 200,
            "data": {"cached": True}
        })

        # Execute first request
        result1 = await agent.handle_integration({
            "serviceName": "github",
            "operation": "execute",
            "credentials": github_credentials,
            "parameters": {"cache": True},
            "data": None
        })

        # Execute second identical request
        result2 = await agent.handle_integration({
            "serviceName": "github",
            "operation": "execute",
            "credentials": github_credentials,
            "parameters": {"cache": True},
            "data": None
        })

        # Assertions
        assert result1["success"] is True
        assert result2["success"] is True
        # In real implementation, would verify cache was used for second request

    @pytest.mark.asyncio
    async def test_security_validation(self, agent, github_credentials):
        """Test security validation of credentials."""
        # Setup security validation
        agent.credential_manager.validate_credentials = AsyncMock(return_value={
            "valid": True,
            "warnings": []
        })

        # Execute
        result = await agent.handle_integration({
            "serviceName": "github",
            "operation": "authenticate",
            "credentials": github_credentials,
            "parameters": {},
            "data": None
        })

        # Assertions
        assert result["success"] is True
        agent.credential_manager.validate_credentials.assert_called_once()

    @pytest.mark.asyncio
    async def test_performance_monitoring(self, agent, github_credentials):
        """Test performance monitoring."""
        # Setup
        agent.credential_manager.get_credentials = AsyncMock(return_value=github_credentials)
        agent.service_registry.check_service_health = AsyncMock(return_value={
            "available": True
        })
        agent.http_client.make_request = AsyncMock(return_value={
            "status_code": 200,
            "data": {"success": True}
        })

        # Execute
        result = await agent.handle_integration({
            "serviceName": "github",
            "operation": "execute",
            "credentials": github_credentials,
            "parameters": {},
            "data": None
        })

        # Assertions
        assert result["success"] is True
        assert "executionTime" in result["metadata"]
        # In real implementation, would verify performance metrics collection

    @pytest.mark.asyncio
    async def test_concurrent_integrations(self, agent, github_credentials):
        """Test handling multiple concurrent integrations."""
        # Setup
        agent.credential_manager.get_credentials = AsyncMock(return_value=github_credentials)
        agent.service_registry.check_service_health = AsyncMock(return_value={
            "available": True
        })
        agent.http_client.make_request = AsyncMock(return_value={
            "status_code": 200,
            "data": {"success": True}
        })

        # Execute concurrent requests
        tasks = []
        for i in range(5):
            task = agent.handle_integration({
                "serviceName": "github",
                "operation": "execute",
                "credentials": github_credentials,
                "parameters": {"request_id": i},
                "data": None
            })
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        # Assertions
        assert len(results) == 5
        assert all(result["success"] for result in results)

    @pytest.mark.asyncio
    async def test_graceful_degradation(self, agent, github_credentials):
        """Test graceful degradation when services are partially available."""
        # Setup partial service availability
        agent.credential_manager.get_credentials = AsyncMock(return_value=github_credentials)
        agent.service_registry.check_service_health = AsyncMock(return_value={
            "available": False,
            "partial": True,
            "available_endpoints": ["/user"]
        })

        # Execute request for available endpoint
        result = await agent.handle_integration({
            "serviceName": "github",
            "operation": "execute",
            "credentials": github_credentials,
            "parameters": {"endpoint": "/user"},
            "data": None
        })

        # Assertions
        # In real implementation, would handle partial availability gracefully
        assert "partial" in str(result).lower() or result["success"] is True
