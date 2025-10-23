"""
Pytest configuration and shared fixtures for n8n Visual Workflow Builder tests.
"""

import asyncio
import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any

# Import mock classes
from tests.mocks.n8n_api_mock import N8nApiMock
from tests.mocks.redis_mock import RedisMock
from tests.mocks.websocket_mock import WebSocketMock
from tests.mocks.external_services_mock import ExternalServiceMock

# Import test fixtures
from tests.fixtures.sample_workflows import SIMPLE_WORKFLOW, COMPLEX_WORKFLOW
from tests.fixtures.test_credentials import TEST_CREDENTIALS
from tests.fixtures.canvas_states import EMPTY_CANVAS, LOADED_CANVAS


@pytest.fixture
def event_loop():
    """Create an asyncio event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_n8n_api():
    """Mock n8n API client."""
    return N8nApiMock()


@pytest.fixture
def mock_redis_client():
    """Mock Redis client."""
    return RedisMock()


@pytest.fixture
def mock_websocket():
    """Mock WebSocket connection."""
    return WebSocketMock()


@pytest.fixture
def mock_external_service():
    """Mock external service client."""
    return ExternalServiceMock("test-service")


@pytest.fixture
def mock_state_manager():
    """Mock state manager."""
    state_manager = Mock()
    state_manager.get_state = AsyncMock(return_value={})
    state_manager.set_state = AsyncMock(return_value=True)
    state_manager.update_state = AsyncMock(return_value=True)
    return state_manager


@pytest.fixture
def mock_event_bus():
    """Mock event bus."""
    event_bus = Mock()
    event_bus.publish = AsyncMock(return_value=True)
    event_bus.request = AsyncMock(return_value={"success": True})
    event_bus.subscribe = AsyncMock(return_value=True)
    return event_bus


@pytest.fixture
def simple_workflow():
    """Sample simple workflow for testing."""
    return SIMPLE_WORKFLOW.copy()


@pytest.fixture
def complex_workflow():
    """Sample complex workflow for testing."""
    return COMPLEX_WORKFLOW.copy()


@pytest.fixture
def valid_credentials():
    """Valid test credentials."""
    return TEST_CREDENTIALS.copy()


@pytest.fixture
def empty_canvas():
    """Empty canvas state."""
    return EMPTY_CANVAS.copy()


@pytest.fixture
def loaded_canvas():
    """Loaded canvas with nodes."""
    return LOADED_CANVAS.copy()


@pytest.fixture
def mock_workflow_execution_input():
    """Mock workflow execution input."""
    return {
        "workflowId": "test-workflow-123",
        "executionId": "exec-456",
        "inputData": {"test": "data"},
        "executionOptions": {
            "timeout": 30,
            "maxRetries": 3,
            "parallelExecution": False
        }
    }


@pytest.fixture
def mock_node_validation_input():
    """Mock node validation input."""
    return {
        "nodeType": "n8n-nodes-base.httpRequest",
        "parameters": {
            "method": "GET",
            "url": "https://api.example.com/data"
        },
        "connections": {
            "inputs": [],
            "outputs": []
        },
        "context": {
            "workflowId": "test-workflow-123",
            "availableNodes": ["httpRequest", "set", "if"]
        }
    }


@pytest.fixture
def mock_canvas_management_input():
    """Mock canvas management input."""
    return {
        "action": "move",
        "targetNodes": ["node-1", "node-2"],
        "position": {"x": 100, "y": 200},
        "zoomLevel": 1.0,
        "panOffset": {"x": 0, "y": 0}
    }


@pytest.fixture
def mock_integration_input():
    """Mock integration input."""
    return {
        "serviceName": "github",
        "operation": "authenticate",
        "credentials": {
            "apiKey": "test-api-key"
        },
        "parameters": {},
        "data": None
    }


@pytest.fixture
def mock_export_import_input():
    """Mock export/import input."""
    return {
        "action": "export",
        "workflowId": "test-workflow-123",
        "workflowData": SIMPLE_WORKFLOW,
        "format": "json",
        "options": {
            "includeCredentials": False,
            "includeExecutionHistory": False,
            "version": "1.0.0"
        }
    }


# Test utilities
@pytest.fixture
def generate_id():
    """Generate unique IDs for tests."""
    import uuid
    return str(uuid.uuid4())


@pytest.fixture
def wait_for_async():
    """Wait for async operations in tests."""
    def _wait_for_async(coro):
        return asyncio.run(coro)
    return _wait_for_async


# Performance testing utilities
@pytest.fixture
def performance_monitor():
    """Monitor performance during tests."""
    import time

    class PerformanceMonitor:
        def __init__(self):
            self.start_times = {}
            self.end_times = {}

        def start_timer(self, name: str):
            self.start_times[name] = time.time()

        def end_timer(self, name: str):
            self.end_times[name] = time.time()

        def get_duration(self, name: str) -> float:
            if name in self.start_times and name in self.end_times:
                return self.end_times[name] - self.start_times[name]
            return 0.0

        def reset(self):
            self.start_times.clear()
            self.end_times.clear()

    return PerformanceMonitor()


# Async test utilities
@pytest_asyncio.fixture
async def async_cleanup():
    """Cleanup after async tests."""
    yield
    # Cleanup code here
    await asyncio.sleep(0.1)  # Allow pending tasks to complete


# Custom pytest markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as an end-to-end test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as a performance test"
    )
    config.addinivalue_line(
        "markers", "security: mark test as a security test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


# Test data factories
@pytest.fixture
def workflow_factory():
    """Factory for creating test workflows."""
    def create_workflow(node_count: int = 3, connections: bool = True):
        nodes = []
        edges = []

        for i in range(node_count):
            nodes.append({
                "id": f"node-{i}",
                "type": "n8n-nodes-base.set",
                "position": {"x": 100 + i * 200, "y": 100},
                "parameters": {"values": {"string": [{"name": "test", "value": f"value-{i}"}]}}
            })

        if connections and node_count > 1:
            for i in range(node_count - 1):
                edges.append({
                    "id": f"edge-{i}-{i+1}",
                    "source": f"node-{i}",
                    "target": f"node-{i+1}"
                })

        return {"nodes": nodes, "connections": edges}

    return create_workflow
