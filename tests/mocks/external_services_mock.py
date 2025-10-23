"""
Mock implementation of external services for testing purposes.
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from unittest.mock import Mock


class ExternalServiceMock:
    """Mock external service for testing."""

    def __init__(self, service_name: str):
        self.service_name = service_name
        self.request_count = 0
        self.requests: List[Dict[str, Any]] = []
        self.responses: Dict[str, Dict[str, Any]] = {}
        self.error_simulation: Optional[Exception] = None
        self.rate_limit = {"requests": 0, "window_start": 0, "limit": 100, "window_seconds": 60}

    def configure_response(self, endpoint: str, response: Any,
                          delay: float = 0, status_code: int = 200) -> None:
        """Configure mock response for specific endpoint."""
        self.responses[endpoint] = {
            "response": response,
            "delay": delay,
            "status_code": status_code
        }

    def configure_error(self, endpoint: str, error: Exception, delay: float = 0) -> None:
        """Configure error response for specific endpoint."""
        self.responses[endpoint] = {
            "error": error,
            "delay": delay
        }

    async def make_request(self, method: str, endpoint: str,
                          headers: Dict[str, str] = None,
                          data: Any = None, timeout: float = 30.0) -> Dict[str, Any]:
        """Mock HTTP request to external service."""
        self.request_count += 1

        # Record the request
        request_info = {
            "method": method,
            "endpoint": endpoint,
            "headers": headers or {},
            "data": data,
            "timestamp": asyncio.get_event_loop().time()
        }
        self.requests.append(request_info)

        # Check rate limiting
        if not self._check_rate_limit():
            return {
                "error": "Rate limit exceeded",
                "status_code": 429,
                "retry_after": 60
            }

        # Check for configured error
        if endpoint in self.responses and "error" in self.responses[endpoint]:
            config = self.responses[endpoint]
            if config["delay"]:
                await asyncio.sleep(config["delay"])
            raise config["error"]

        # Return configured response or default success
        if endpoint in self.responses and "response" in self.responses[endpoint]:
            config = self.responses[endpoint]
            if config["delay"]:
                await asyncio.sleep(config["delay"])

            response_data = config["response"]
            if isinstance(response_data, dict):
                return {
                    **response_data,
                    "status_code": config.get("status_code", 200)
                }
            else:
                return {
                    "data": response_data,
                    "status_code": config.get("status_code", 200)
                }
        else:
            # Default success response
            return {
                "data": {"success": True, "message": "Mock response"},
                "status_code": 200
            }

    def _check_rate_limit(self) -> bool:
        """Check if rate limit is exceeded."""
        current_time = asyncio.get_event_loop().time()

        # Reset window if needed
        if current_time - self.rate_limit["window_start"] > self.rate_limit["window_seconds"]:
            self.rate_limit["requests"] = 0
            self.rate_limit["window_start"] = current_time

        # Check limit
        if self.rate_limit["requests"] >= self.rate_limit["limit"]:
            return False

        self.rate_limit["requests"] += 1
        return True

    def set_rate_limit(self, requests_per_window: int, window_seconds: int = 60) -> None:
        """Set rate limiting parameters."""
        self.rate_limit = {
            "requests": 0,
            "window_start": asyncio.get_event_loop().time(),
            "limit": requests_per_window,
            "window_seconds": window_seconds
        }

    def set_error_simulation(self, error: Exception) -> None:
        """Set error to simulate on all requests."""
        self.error_simulation = error

    def clear_error_simulation(self) -> None:
        """Clear error simulation."""
        self.error_simulation = None

    def get_request_count(self, method: str = None, endpoint: str = None) -> int:
        """Get count of requests matching criteria."""
        count = 0
        for request in self.requests:
            if method and request["method"] != method:
                continue
            if endpoint and request["endpoint"] != endpoint:
                continue
            count += 1
        return count

    def get_last_request(self, method: str = None, endpoint: str = None) -> Optional[Dict[str, Any]]:
        """Get the last request matching criteria."""
        for request in reversed(self.requests):
            if method and request["method"] != method:
                continue
            if endpoint and request["endpoint"] != endpoint:
                continue
            return request
        return None

    def clear_history(self) -> None:
        """Clear request history."""
        self.requests.clear()
        self.request_count = 0

        # Reset rate limit
        self.rate_limit["requests"] = 0
        self.rate_limit["window_start"] = asyncio.get_event_loop().time()


class OAuth2ServiceMock(ExternalServiceMock):
    """Mock OAuth2 service for testing."""

    def __init__(self, service_name: str):
        super().__init__(service_name)
        self.tokens: Dict[str, Dict[str, Any]] = {}
        self.authorization_codes: Dict[str, Dict[str, Any]] = {}

    async def authorize(self, client_id: str, redirect_uri: str,
                       scope: str = "read") -> str:
        """Mock OAuth2 authorization."""
        auth_code = f"auth_code_{len(self.authorization_codes) + 1}"
        self.authorization_codes[auth_code] = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": scope,
            "created_at": asyncio.get_event_loop().time()
        }

        return auth_code

    async def token_exchange(self, code: str, client_id: str,
                           client_secret: str) -> Dict[str, Any]:
        """Mock OAuth2 token exchange."""
        if code not in self.authorization_codes:
            return {"error": "invalid_grant"}

        auth_info = self.authorization_codes[code]
        if auth_info["client_id"] != client_id:
            return {"error": "invalid_client"}

        # Generate access token
        access_token = f"access_token_{len(self.tokens) + 1}"
        refresh_token = f"refresh_token_{len(self.tokens) + 1}"

        self.tokens[access_token] = {
            "refresh_token": refresh_token,
            "client_id": client_id,
            "scope": auth_info["scope"],
            "expires_in": 3600,
            "created_at": asyncio.get_event_loop().time()
        }

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": 3600,
            "scope": auth_info["scope"]
        }

    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Mock token refresh."""
        # Find token by refresh token
        for access_token, token_info in self.tokens.items():
            if token_info["refresh_token"] == refresh_token:
                # Generate new access token
                new_access_token = f"access_token_{len(self.tokens) + 1}"
                self.tokens[new_access_token] = {
                    **token_info,
                    "created_at": asyncio.get_event_loop().time()
                }
                del self.tokens[access_token]

                return {
                    "access_token": new_access_token,
                    "token_type": "Bearer",
                    "expires_in": 3600
                }

        return {"error": "invalid_grant"}

    async def validate_token(self, access_token: str) -> Dict[str, Any]:
        """Mock token validation."""
        if access_token not in self.tokens:
            return {"error": "invalid_token"}

        token_info = self.tokens[access_token]

        # Check if token is expired (simplified)
        if asyncio.get_event_loop().time() - token_info["created_at"] > token_info.get("expires_in", 3600):
            return {"error": "token_expired"}

        return {
            "valid": True,
            "client_id": token_info["client_id"],
            "scope": token_info["scope"]
        }


class WebhookServiceMock:
    """Mock webhook service for testing."""

    def __init__(self):
        self.registered_webhooks: Dict[str, Dict[str, Any]] = {}
        self.received_webhooks: List[Dict[str, Any]] = []
        self.responses: Dict[str, Any] = {}

    async def register_webhook(self, webhook_url: str, events: List[str],
                             secret: str = None) -> str:
        """Mock webhook registration."""
        webhook_id = f"webhook_{len(self.registered_webhooks) + 1}"

        self.registered_webhooks[webhook_id] = {
            "id": webhook_id,
            "url": webhook_url,
            "events": events,
            "secret": secret,
            "created_at": asyncio.get_event_loop().time()
        }

        return webhook_id

    async def trigger_webhook(self, webhook_id: str, event: str, payload: Any) -> bool:
        """Mock webhook triggering."""
        if webhook_id not in self.registered_webhooks:
            return False

        webhook_info = self.registered_webhooks[webhook_id]
        if event not in webhook_info["events"]:
            return False

        webhook_call = {
            "webhook_id": webhook_id,
            "event": event,
            "payload": payload,
            "timestamp": asyncio.get_event_loop().time()
        }

        self.received_webhooks.append(webhook_call)

        # Simulate webhook delivery
        await asyncio.sleep(0.01)

        return True

    def get_received_webhooks(self, webhook_id: str = None, event: str = None) -> List[Dict[str, Any]]:
        """Get received webhooks matching criteria."""
        webhooks = self.received_webhooks

        if webhook_id:
            webhooks = [w for w in webhooks if w["webhook_id"] == webhook_id]

        if event:
            webhooks = [w for w in webhooks if w["event"] == event]

        return webhooks

    def clear_received_webhooks(self) -> None:
        """Clear received webhooks."""
        self.received_webhooks.clear()
