"""
Test utilities and helper functions for n8n Visual Workflow Builder tests.
"""

import asyncio
import time
import json
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, AsyncMock


class TestDataGenerator:
    """Generate test data for various scenarios."""

    @staticmethod
    def create_workflow_node(node_id: str, node_type: str,
                           position: Dict[str, int],
                           parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a workflow node with standard structure."""
        return {
            "id": node_id,
            "type": node_type,
            "position": position,
            "parameters": parameters or {},
            "data": {
                "label": node_type.split('.')[-1].replace('n8n-nodes-base.', '').title()
            }
        }

    @staticmethod
    def create_connection(source_id: str, target_id: str,
                        source_output: int = 0, target_input: int = 0) -> Dict[str, Any]:
        """Create a workflow connection."""
        return {
            "source": source_id,
            "target": target_id,
            "sourceOutput": source_output,
            "targetInput": target_input,
            "id": f"{source_id}->{target_id}"
        }

    @staticmethod
    def generate_linear_workflow(node_count: int = 3) -> Dict[str, Any]:
        """Generate a linear workflow with specified number of nodes."""
        nodes = []
        connections = []

        for i in range(node_count):
            node_id = f"node-{i}"
            node_type = "n8n-nodes-base.set" if i > 0 else "n8n-nodes-base.manualTrigger"

            nodes.append(TestDataGenerator.create_workflow_node(
                node_id=node_id,
                node_type=node_type,
                position={"x": 100 + i * 200, "y": 100}
            ))

            if i > 0:
                connections.append(TestDataGenerator.create_connection(
                    f"node-{i-1}", node_id
                ))

        return {"nodes": nodes, "connections": connections}

    @staticmethod
    def generate_branching_workflow() -> Dict[str, Any]:
        """Generate a branching workflow with conditional logic."""
        return {
            "nodes": [
                TestDataGenerator.create_workflow_node(
                    "trigger", "n8n-nodes-base.manualTrigger",
                    {"x": 100, "y": 100}
                ),
                TestDataGenerator.create_workflow_node(
                    "condition", "n8n-nodes-base.if",
                    {"x": 300, "y": 100}
                ),
                TestDataGenerator.create_workflow_node(
                    "success", "n8n-nodes-base.set",
                    {"x": 500, "y": 50}
                ),
                TestDataGenerator.create_workflow_node(
                    "failure", "n8n-nodes-base.set",
                    {"x": 500, "y": 150}
                )
            ],
            "connections": [
                TestDataGenerator.create_connection("trigger", "condition"),
                TestDataGenerator.create_connection("condition", "success", source_output=0),
                TestDataGenerator.create_connection("condition", "failure", source_output=1)
            ]
        }


class PerformanceTester:
    """Utilities for performance testing."""

    @staticmethod
    async def measure_execution_time(coro_func, *args, **kwargs):
        """Measure execution time of an async function."""
        start_time = time.time()
        result = await coro_func(*args, **kwargs)
        end_time = time.time()

        return {
            "result": result,
            "execution_time": end_time - start_time,
            "start_time": start_time,
            "end_time": end_time
        }

    @staticmethod
    async def stress_test(func, iterations: int = 100, concurrent: bool = False):
        """Run stress test on a function."""
        if concurrent:
            tasks = [func() for _ in range(iterations)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        else:
            results = []
            for _ in range(iterations):
                try:
                    result = await func()
                    results.append(result)
                except Exception as e:
                    results.append({"error": str(e)})

        return {
            "total_iterations": iterations,
            "successful": len([r for r in results if "error" not in r]),
            "failed": len([r for r in results if "error" in r]),
            "results": results
        }

    @staticmethod
    def check_memory_usage():
        """Check current memory usage (simplified)."""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()

        return {
            "rss": memory_info.rss,  # Resident Set Size
            "vms": memory_info.vms,  # Virtual Memory Size
            "percent": process.memory_percent()
        }


class MockBuilder:
    """Build complex mocks for testing."""

    @staticmethod
    def create_agent_mock(agent_name: str):
        """Create a mock agent with standard interface."""
        mock_agent = Mock()
        mock_agent.name = agent_name

        # Standard agent methods
        mock_agent.initialize = AsyncMock(return_value=True)
        mock_agent.shutdown = AsyncMock(return_value=True)
        mock_agent.health_check = AsyncMock(return_value={"status": "healthy"})
        mock_agent.get_status = Mock(return_value="ready")

        return mock_agent

    @staticmethod
    def create_service_mock(service_name: str, methods: List[str] = None):
        """Create a mock service."""
        if methods is None:
            methods = ["connect", "disconnect", "execute", "status"]

        mock_service = Mock()
        mock_service.name = service_name

        for method in methods:
            if method.startswith("async_"):
                async_method = method.replace("async_", "")
                setattr(mock_service, async_method, AsyncMock())
            else:
                setattr(mock_service, method, Mock())

        return mock_service


class ValidationHelpers:
    """Helpers for validation testing."""

    @staticmethod
    def assert_workflow_structure(workflow: Dict[str, Any]):
        """Assert workflow has valid structure."""
        assert "nodes" in workflow
        assert "connections" in workflow
        assert isinstance(workflow["nodes"], list)
        assert isinstance(workflow["connections"], list)

        # Check nodes have required fields
        for node in workflow["nodes"]:
            assert "id" in node
            assert "type" in node
            assert "position" in node
            assert isinstance(node["position"], dict)
            assert "x" in node["position"]
            assert "y" in node["position"]

        # Check connections have required fields
        for connection in workflow["connections"]:
            assert "source" in connection
            assert "target" in connection

    @staticmethod
    def assert_execution_result(result: Dict[str, Any]):
        """Assert execution result has valid structure."""
        assert "status" in result
        assert result["status"] in ["success", "error", "running", "cancelled"]

        if result["status"] == "success":
            assert "results" in result
            assert "executionTime" in result

        if result["status"] == "error":
            assert "error" in result
            assert "message" in result["error"]

    @staticmethod
    def assert_canvas_state(canvas: Dict[str, Any]):
        """Assert canvas state has valid structure."""
        assert "nodes" in canvas
        assert "edges" in canvas
        assert "viewport" in canvas

        assert isinstance(canvas["nodes"], list)
        assert isinstance(canvas["edges"], list)
        assert isinstance(canvas["viewport"], dict)

        # Check viewport fields
        assert "x" in canvas["viewport"]
        assert "y" in canvas["viewport"]
        assert "zoom" in canvas["viewport"]


class AsyncTestHelpers:
    """Helpers for async testing."""

    @staticmethod
    async def wait_for_condition(condition_func, timeout: float = 5.0, interval: float = 0.1):
        """Wait for a condition to become true."""
        start_time = time.time()

        while time.time() - start_time < timeout:
            if await condition_func():
                return True
            await asyncio.sleep(interval)

        return False

    @staticmethod
    async def gather_with_timeout(*tasks, timeout: float = 10.0):
        """Gather tasks with timeout."""
        try:
            return await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            return {"error": "Timeout", "timeout": timeout}

    @staticmethod
    def create_async_mock(return_value=None, side_effect=None):
        """Create an async mock function."""
        async def mock_func(*args, **kwargs):
            if side_effect:
                if isinstance(side_effect, Exception):
                    raise side_effect
                elif callable(side_effect):
                    return await side_effect(*args, **kwargs)
                else:
                    return side_effect
            return return_value

        return AsyncMock(side_effect=mock_func)


class DataComparisonHelpers:
    """Helpers for comparing test data."""

    @staticmethod
    def compare_workflows(workflow1: Dict[str, Any], workflow2: Dict[str, Any]) -> Dict[str, Any]:
        """Compare two workflows and return differences."""
        differences = {
            "nodes": {"added": [], "removed": [], "modified": []},
            "connections": {"added": [], "removed": [], "modified": []}
        }

        # Compare nodes
        nodes1 = {node["id"]: node for node in workflow1.get("nodes", [])}
        nodes2 = {node["id"]: node for node in workflow2.get("nodes", [])}

        for node_id in nodes1:
            if node_id not in nodes2:
                differences["nodes"]["removed"].append(node_id)

        for node_id in nodes2:
            if node_id not in nodes1:
                differences["nodes"]["added"].append(node_id)
            elif nodes1[node_id] != nodes2[node_id]:
                differences["nodes"]["modified"].append(node_id)

        return differences

    @staticmethod
    def assert_workflow_equality(workflow1: Dict[str, Any], workflow2: Dict[str, Any]):
        """Assert two workflows are equal (ignoring metadata)."""
        def normalize_workflow(workflow):
            """Normalize workflow for comparison."""
            normalized = json.loads(json.dumps(workflow))
            # Remove metadata that shouldn't affect equality
            for node in normalized.get("nodes", []):
                node.pop("data", None)
            return normalized

        assert normalize_workflow(workflow1) == normalize_workflow(workflow2)


class ErrorSimulation:
    """Simulate various error conditions for testing."""

    @staticmethod
    def create_network_error():
        """Create a network error."""
        return Exception("Network timeout")

    @staticmethod
    def create_validation_error(field: str, message: str):
        """Create a validation error."""
        return Exception(f"Validation error for {field}: {message}")

    @staticmethod
    def create_permission_error():
        """Create a permission error."""
        return Exception("Insufficient permissions")

    @staticmethod
    def create_resource_error(resource: str):
        """Create a resource exhaustion error."""
        return Exception(f"Resource exhausted: {resource}")

    @staticmethod
    async def simulate_intermittent_failure(func, failure_rate: float = 0.3):
        """Simulate intermittent failures."""
        import random

        if random.random() < failure_rate:
            raise Exception("Intermittent failure")

        return await func()

    @staticmethod
    async def simulate_degraded_performance(func, delay_range: tuple = (0.1, 2.0)):
        """Simulate degraded performance."""
        import random

        delay = random.uniform(*delay_range)
        await asyncio.sleep(delay)

        return await func()
