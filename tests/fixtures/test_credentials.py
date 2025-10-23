"""
Test credentials and authentication data for testing purposes.
"""

from typing import Dict, Any


# Valid credentials for testing
VALID_CREDENTIALS = {
    "github": {
        "type": "githubApi",
        "name": "GitHub API",
        "data": {
            "accessToken": "ghp_test1234567890abcdef",
            "user": "testuser",
            "repository": "test/repo"
        }
    },
    "google": {
        "type": "googleApi",
        "name": "Google API",
        "data": {
            "accessToken": "ya29.test123456789",
            "refreshToken": "1//test-refresh-token",
            "clientId": "test-client-id.apps.googleusercontent.com",
            "clientSecret": "test-client-secret"
        }
    },
    "slack": {
        "type": "slackApi",
        "name": "Slack API",
        "data": {
            "accessToken": "xoxb-test-slack-token",
            "botUserId": "U1234567890"
        }
    },
    "database": {
        "type": "postgres",
        "name": "Test Database",
        "data": {
            "host": "localhost",
            "port": 5432,
            "database": "test_db",
            "user": "test_user",
            "password": "test_password"
        }
    }
}

# Invalid credentials for testing error scenarios
INVALID_CREDENTIALS = {
    "expired_token": {
        "type": "githubApi",
        "name": "Expired Token",
        "data": {
            "accessToken": "expired_token_123"
        }
    },
    "wrong_format": {
        "type": "githubApi",
        "name": "Wrong Format",
        "data": {
            "wrongField": "wrong_value"
        }
    },
    "empty_credentials": {
        "type": "githubApi",
        "name": "Empty Credentials",
        "data": {}
    }
}

# OAuth2 flow test data
OAUTH2_TEST_DATA = {
    "authorization_url": "https://github.com/login/oauth/authorize",
    "token_url": "https://github.com/login/oauth/access_token",
    "client_id": "test_client_id_12345",
    "client_secret": "test_client_secret_67890",
    "redirect_uri": "http://localhost:3000/oauth/callback",
    "scope": "repo,read:user",
    "state": "test_state_123",
    "authorization_code": "auth_code_abcdef123456"
}

# API keys for different services
API_KEYS = {
    "github": "ghp_test1234567890abcdef",
    "gitlab": "glpat-test1234567890abcdef",
    "slack": "xoxb-test-slack-token-12345",
    "discord": "discord_bot_token_12345",
    "twitter": "twitter_bearer_token_12345",
    "openai": "sk-test1234567890abcdef",
    "anthropic": "sk-ant-test1234567890abcdef"
}

# Webhook secrets for testing
WEBHOOK_SECRETS = {
    "github": "github_webhook_secret_12345",
    "slack": "slack_webhook_secret_67890",
    "stripe": "whsec_stripe_webhook_secret_abcde"
}

# Test user data
TEST_USERS = {
    "admin": {
        "id": "user-admin-123",
        "email": "admin@test.com",
        "role": "admin",
        "permissions": ["read", "write", "delete", "admin"]
    },
    "user": {
        "id": "user-regular-456",
        "email": "user@test.com",
        "role": "user",
        "permissions": ["read", "write"]
    },
    "viewer": {
        "id": "user-viewer-789",
        "email": "viewer@test.com",
        "role": "viewer",
        "permissions": ["read"]
    }
}

# Service configurations for testing integrations
SERVICE_CONFIGS = {
    "github": {
        "base_url": "https://api.github.com",
        "rate_limit": 5000,
        "timeout": 30,
        "retry_attempts": 3
    },
    "slack": {
        "base_url": "https://slack.com/api",
        "rate_limit": 1,
        "timeout": 10,
        "retry_attempts": 2
    },
    "google": {
        "base_url": "https://www.googleapis.com",
        "rate_limit": 1000,
        "timeout": 60,
        "retry_attempts": 3
    }
}


def get_credential_by_type(credential_type: str) -> Dict[str, Any]:
    """Get test credentials by type."""
    return VALID_CREDENTIALS.get(credential_type, {})


def get_invalid_credential(credential_type: str) -> Dict[str, Any]:
    """Get invalid test credentials by type."""
    return INVALID_CREDENTIALS.get(credential_type, INVALID_CREDENTIALS["empty_credentials"])


def get_api_key(service: str) -> str:
    """Get API key for service."""
    return API_KEYS.get(service, "test-api-key")


def get_webhook_secret(service: str) -> str:
    """Get webhook secret for service."""
    return WEBHOOK_SECRETS.get(service, "test-webhook-secret")


def get_test_user(role: str) -> Dict[str, Any]:
    """Get test user by role."""
    return TEST_USERS.get(role, TEST_USERS["user"])


def get_service_config(service: str) -> Dict[str, Any]:
    """Get service configuration."""
    return SERVICE_CONFIGS.get(service, SERVICE_CONFIGS["github"])
