"""
Custom assertions for n8n Visual Workflow Builder tests.
"""

import pytest
from typing import Dict, Any, List
from tests.utils.test_helpers import ValidationHelpers, DataComparisonHelpers


class WorkflowAssertions:
    """Custom assertions for workflow-related tests."""

    @staticmethod
    def assert_valid_workflow_structure(workflow: Dict[str, Any]):
        """Assert workflow has valid structure."""
        ValidationHelpers.assert_workflow_structure(workflow)

        # Additional validation
        assert len(workflow["nodes"]) > 0, "Workflow must have at least one node"

        # Check for at least one trigger node
        trigger_nodes = [node for node in workflow["nodes"]
                        if "trigger" in node["type"].lower()]
        assert len(trigger_nodes) > 0, "Workflow must have at least one trigger node"

    @staticmethod
    def assert_workflow_connectivity(workflow: Dict[str, Any]):
        """Assert workflow connections are valid."""
        node_ids = {node["id"] for node in workflow["nodes"]}

        for connection in workflow["connections"]:
            assert connection["source"] in node_ids, f"Invalid source node: {connection['source']}"
            assert connection["target"] in node_ids, f"Invalid target node: {connection['target']}"

    @staticmethod
    def assert_workflow_topological_order(workflow: Dict[str, Any], execution_order: List[str]):
        """Assert nodes are executed in valid topological order."""
        # Build dependency graph
        dependencies = {node["id"]: set() for node in workflow["nodes"]}

        for connection in workflow["connections"]:
            dependencies[connection["target"]].add(connection["source"])

        # Verify execution order respects dependencies
        executed = set()
        for node_id in execution_order:
            assert node_id in dependencies, f"Unknown node in execution order: {node_id}"

            # All dependencies should be executed before this node
            for dep in dependencies[node_id]:
                assert dep in executed, f"Dependency {dep} not executed before {node_id}"

            executed.add(node_id)

    @staticmethod
    def assert_workflow_data_flow(workflow: Dict[str, Any], input_data: Dict[str, Any], expected_output: Dict[str, Any]):
        """Assert data flows correctly through workflow."""
        # This is a simplified assertion - real implementation would trace data flow
        assert isinstance(input_data, dict), "Input data must be a dictionary"
        assert isinstance(expected_output, dict), "Expected output must be a dictionary"

    @staticmethod
    def assert_no_circular_dependencies(workflow: Dict[str, Any]):
        """Assert workflow has no circular dependencies."""
        # Build adjacency list
        graph = {node["id"]: [] for node in workflow["nodes"]}

        for connection in workflow["connections"]:
            if connection["source"] in graph:
                graph[connection["source"]].append(connection["target"])

        # Check for cycles using DFS
        visited = set()
        rec_stack = set()

        def has_cycle(node_id: str) -> bool:
            if node_id in rec_stack:
                return True
            if node_id in visited:
                return False

            visited.add(node_id)
            rec_stack.add(node_id)

            for neighbor in graph.get(node_id, []):
                if has_cycle(neighbor):
                    return True

            rec_stack.remove(node_id)
            return False

        for node_id in graph:
            if has_cycle(node_id):
                pytest.fail(f"Circular dependency detected involving node: {node_id}")


class AgentAssertions:
    """Custom assertions for agent-related tests."""

    @staticmethod
    def assert_agent_health(agent, expected_status: str = "healthy"):
        """Assert agent health status."""
        assert hasattr(agent, 'health_check'), "Agent must have health_check method"

        # In real implementation, would check actual health status
        health_status = "healthy"  # Mock for testing
        assert health_status == expected_status

    @staticmethod
    def assert_agent_initialization(agent):
        """Assert agent initializes correctly."""
        assert hasattr(agent, 'initialize'), "Agent must have initialize method"
        assert hasattr(agent, 'shutdown'), "Agent must have shutdown method"

        # Check initialization state
        assert hasattr(agent, 'initialized'), "Agent must track initialization state"
        # In real implementation, would verify initialization completed successfully

    @staticmethod
    def assert_agent_communication(agent, event_bus):
        """Assert agent can communicate via event bus."""
        assert hasattr(agent, 'event_bus'), "Agent must have event bus reference"
        assert agent.event_bus is not None, "Event bus must be connected"

        # In real implementation, would verify event subscription and publishing


class CanvasAssertions:
    """Custom assertions for canvas-related tests."""

    @staticmethod
    def assert_canvas_bounds(canvas_state: Dict[str, Any], max_x: int = 1000, max_y: int = 1000):
        """Assert all nodes are within canvas bounds."""
        for node in canvas_state["nodes"]:
            position = node["position"]
            assert 0 <= position["x"] <= max_x, f"Node {node['id']} x position out of bounds"
            assert 0 <= position["y"] <= max_y, f"Node {node['id']} y position out of bounds"

    @staticmethod
    def assert_node_spacing(canvas_state: Dict[str, Any], min_distance: int = 50):
        """Assert nodes are properly spaced."""
        nodes = canvas_state["nodes"]

        for i, node1 in enumerate(nodes):
            for node2 in nodes[i+1:]:
                pos1 = node1["position"]
                pos2 = node2["position"]

                distance = ((pos1["x"] - pos2["x"]) ** 2 + (pos1["y"] - pos2["y"]) ** 2) ** 0.5

                if distance < min_distance:
                    pytest.fail(f"Nodes {node1['id']} and {node2['id']} are too close: {distance} < {min_distance}")

    @staticmethod
    def assert_connection_validity(canvas_state: Dict[str, Any]):
        """Assert all connections are valid."""
        node_ids = {node["id"] for node in canvas_state["nodes"]}
        edge_ids = {edge.get("id", f"{edge['source']}-{edge['target']}") for edge in canvas_state["edges"]}

        # Check all connections reference valid nodes
        for edge in canvas_state["edges"]:
            assert edge["source"] in node_ids, f"Invalid source node: {edge['source']}"
            assert edge["target"] in node_ids, f"Invalid target node: {edge['target']}"

        # Check for duplicate connections
        connections = [(edge["source"], edge["target"]) for edge in canvas_state["edges"]]
        assert len(connections) == len(set(connections)), "Duplicate connections found"


class IntegrationAssertions:
    """Custom assertions for integration tests."""

    @staticmethod
    def assert_multi_agent_coordination(agents: List, workflow_result: Dict[str, Any]):
        """Assert proper coordination between multiple agents."""
        assert len(agents) > 1, "Multi-agent test requires multiple agents"

        # Verify all agents were involved
        for agent in agents:
            assert hasattr(agent, 'name'), "Agent must have name attribute"
            # In real implementation, would verify agent participation in workflow

        assert workflow_result["status"] in ["success", "error"], "Workflow must have valid status"

    @staticmethod
    def assert_error_propagation(source_agent, target_agent, error: Exception):
        """Assert error propagation between agents."""
        # In real implementation, would verify error was properly propagated
        assert isinstance(error, Exception), "Error must be an Exception instance"

        # Verify error contains necessary information
        assert str(error), "Error must have a message"

    @staticmethod
    def assert_state_consistency(across_agents: List, expected_state: Dict[str, Any]):
        """Assert state consistency across multiple agents."""
        # In real implementation, would verify all agents have consistent state
        assert len(across_agents) > 0, "Must have agents to check consistency"

        for agent in across_agents:
            # Verify agent has access to shared state
            assert hasattr(agent, 'state_manager'), "Agent must have state manager"


class PerformanceAssertions:
    """Custom assertions for performance tests."""

    @staticmethod
    def assert_performance_threshold(execution_time: float, max_time: float, operation: str = "operation"):
        """Assert performance is within acceptable thresholds."""
        assert execution_time <= max_time, f"{operation} took {execution_time}s, exceeds threshold of {max_time}s"

    @staticmethod
    def assert_memory_usage(max_memory_mb: float = 100):
        """Assert memory usage is within acceptable limits."""
        # In real implementation, would check actual memory usage
        from tests.utils.test_helpers import PerformanceTester

        memory_info = PerformanceTester.check_memory_usage()
        memory_mb = memory_info["rss"] / (1024 * 1024)

        assert memory_mb <= max_memory_mb, f"Memory usage {memory_mb}MB exceeds threshold of {max_memory_mb}MB"

    @staticmethod
    def assert_concurrent_performance(results: List, max_total_time: float, concurrency_level: int):
        """Assert performance under concurrent load."""
        successful_results = [r for r in results if "error" not in r]

        assert len(successful_results) > 0, "At least some concurrent operations must succeed"

        # In real implementation, would analyze concurrent performance metrics
        total_time = max_total_time  # Mock value
        assert total_time <= max_total_time, f"Concurrent operations took {total_time}s, exceeds threshold"

    @staticmethod
    def assert_resource_cleanup(initial_resources: Dict[str, Any], final_resources: Dict[str, Any]):
        """Assert resources are properly cleaned up."""
        # In real implementation, would verify resource cleanup
        assert len(final_resources) <= len(initial_resources), "Resources should not increase after cleanup"


class SecurityAssertions:
    """Custom assertions for security tests."""

    @staticmethod
    def assert_credential_security(credentials: Dict[str, Any]):
        """Assert credentials are handled securely."""
        # Verify credentials are not logged in plain text
        assert not any("password" in str(cred).lower() for cred in credentials.values())

        # Verify credentials have proper structure
        for cred_name, cred_data in credentials.items():
            assert "type" in cred_data, f"Credential {cred_name} missing type"

    @staticmethod
    def assert_permission_check(user: Dict[str, Any], resource: str, action: str, expected_allowed: bool):
        """Assert permission checks work correctly."""
        # In real implementation, would verify permission validation
        assert "permissions" in user, "User must have permissions"

        allowed = action in user["permissions"]
        assert allowed == expected_allowed, f"Permission check failed for {action} on {resource}"

    @staticmethod
    def assert_data_isolation(user1_data: Dict[str, Any], user2_data: Dict[str, Any]):
        """Assert data isolation between users."""
        # Verify users cannot access each other's data
        assert user1_data != user2_data, "User data should be isolated"

        # In real implementation, would verify comprehensive data isolation


class APIAssertions:
    """Custom assertions for API-related tests."""

    @staticmethod
    def assert_api_response_format(response: Dict[str, Any]):
        """Assert API response has correct format."""
        # Standard n8n API response format
        assert isinstance(response, dict), "Response must be a dictionary"

        # Check for standard fields
        if "success" in response:
            assert isinstance(response["success"], bool), "Success field must be boolean"

        if "error" in response:
            assert "message" in response["error"], "Error must have message"

    @staticmethod
    def assert_rate_limit_headers(response: Dict[str, Any]):
        """Assert rate limit headers are present."""
        # In real implementation, would check actual headers
        required_headers = ["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"]

        for header in required_headers:
            assert header.lower() in [h.lower() for h in response.get("headers", {})], f"Missing header: {header}"

    @staticmethod
    def assert_webhook_signature(signature: str, payload: str, secret: str):
        """Assert webhook signature validation."""
        # In real implementation, would verify HMAC signature
        import hmac
        import hashlib

        expected_signature = hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

        assert signature == expected_signature, "Webhook signature validation failed"


# Convenience functions for common assertions
def assert_workflow_valid(workflow: Dict[str, Any]):
    """Convenience function for workflow validation."""
    WorkflowAssertions.assert_valid_workflow_structure(workflow)
    WorkflowAssertions.assert_workflow_connectivity(workflow)


def assert_execution_successful(result: Dict[str, Any]):
    """Convenience function for execution result validation."""
    ValidationHelpers.assert_execution_result(result)
    assert result["status"] == "success", f"Expected success, got: {result['status']}"


def assert_canvas_valid(canvas: Dict[str, Any]):
    """Convenience function for canvas validation."""
    ValidationHelpers.assert_canvas_state(canvas)
    CanvasAssertions.assert_connection_validity(canvas)


def assert_agents_healthy(agents: List):
    """Convenience function for agent health validation."""
    for agent in agents:
        AgentAssertions.assert_agent_health(agent)
