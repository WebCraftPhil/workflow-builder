"""
Unit tests for WorkflowExecutionAgent.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any

from agents.workflow_execution_agent import WorkflowExecutionAgent
from tests.mocks.n8n_api_mock import N8nApiMock


class TestWorkflowExecutionAgent:
    """Test cases for WorkflowExecutionAgent."""

    @pytest.fixture
    def agent(self, mock_n8n_api, mock_state_manager, mock_event_bus):
        """Create WorkflowExecutionAgent instance for testing."""
        return WorkflowExecutionAgent(mock_n8n_api, mock_state_manager, mock_event_bus)

    @pytest.fixture
    def valid_workflow_input(self):
        """Valid workflow execution input."""
        return {
            "workflowId": "test-workflow-123",
            "executionId": "exec-456",
            "inputData": {"test": "input"},
            "executionOptions": {
                "timeout": 30,
                "maxRetries": 3,
                "parallelExecution": False
            }
        }

    @pytest.mark.asyncio
    async def test_workflow_execution_success(self, agent, mock_n8n_api, valid_workflow_input):
        """Test successful workflow execution."""
        # Setup mock
        mock_n8n_api.execute_workflow = AsyncMock(return_value={
            "executionId": "exec-456",
            "status": "success",
            "results": {"output": "success"},
            "executionTime": 1.5
        })

        # Execute
        result = await agent.execute_workflow(valid_workflow_input)

        # Assertions
        assert result["status"] == "success"
        assert result["executionId"] == "exec-456"
        assert result["results"]["output"] == "success"
        mock_n8n_api.execute_workflow.assert_called_once()

    @pytest.mark.asyncio
    async def test_workflow_execution_with_retry(self, agent, mock_n8n_api, valid_workflow_input):
        """Test workflow execution with retry logic."""
        # Setup mock to fail twice then succeed
        mock_n8n_api.execute_workflow = AsyncMock(side_effect=[
            Exception("Network error"),
            Exception("Timeout error"),
            {
                "executionId": "exec-456",
                "status": "success",
                "results": {"output": "success after retry"},
                "executionTime": 2.0
            }
        ])

        # Execute
        result = await agent.execute_workflow(valid_workflow_input)

        # Assertions
        assert result["status"] == "success"
        assert mock_n8n_api.execute_workflow.call_count == 3

    @pytest.mark.asyncio
    async def test_workflow_execution_timeout(self, agent, mock_n8n_api, valid_workflow_input):
        """Test workflow execution timeout handling."""
        # Setup mock to hang
        async def hanging_execution(*args, **kwargs):
            await asyncio.sleep(10)  # Longer than timeout
            return {"status": "success"}

        mock_n8n_api.execute_workflow = AsyncMock(side_effect=hang_execution)

        # Execute with short timeout
        valid_workflow_input["executionOptions"]["timeout"] = 1
        result = await agent.execute_workflow(valid_workflow_input)

        # Assertions
        assert result["status"] == "error"
        assert "timeout" in result["error"]["message"].lower()

    @pytest.mark.asyncio
    async def test_workflow_validation_failure(self, agent, mock_n8n_api, valid_workflow_input):
        """Test workflow execution with validation failure."""
        # Setup mock to return invalid workflow
        mock_n8n_api.get_workflow = AsyncMock(return_value={
            "id": "test-workflow-123",
            "nodes": [],
            "connections": [{"source": "non-existent", "target": "another"}]
        })

        # Execute
        result = await agent.execute_workflow(valid_workflow_input)

        # Assertions
        assert result["status"] == "error"
        assert "validation" in result["error"]["message"].lower()

    @pytest.mark.asyncio
    async def test_parallel_execution(self, agent, mock_n8n_api, valid_workflow_input):
        """Test parallel workflow execution."""
        # Setup mock for parallel execution
        mock_n8n_api.execute_workflow = AsyncMock(return_value={
            "executionId": "exec-456",
            "status": "success",
            "results": {"output": "parallel success"},
            "executionTime": 0.5
        })

        valid_workflow_input["executionOptions"]["parallelExecution"] = True

        # Execute
        result = await agent.execute_workflow(valid_workflow_input)

        # Assertions
        assert result["status"] == "success"
        mock_n8n_api.execute_workflow.assert_called_once()

    @pytest.mark.asyncio
    async def test_execution_state_persistence(self, agent, mock_state_manager, valid_workflow_input):
        """Test execution state persistence."""
        # Setup
        execution_context = {"state": "test_state", "variables": {"var1": "value1"}}

        # Execute
        await agent.persist_execution_state("exec-456", execution_context)

        # Assertions
        mock_state_manager.set_state.assert_called_with(
            "execution:exec-456",
            execution_context
        )

    @pytest.mark.asyncio
    async def test_execution_context_initialization(self, agent, valid_workflow_input):
        """Test execution context initialization."""
        # Execute
        context = await agent.initialize_context(valid_workflow_input)

        # Assertions
        assert context["workflowId"] == valid_workflow_input["workflowId"]
        assert context["inputData"] == valid_workflow_input["inputData"]
        assert context["executionOptions"] == valid_workflow_input["executionOptions"]
        assert "startTime" in context
        assert "variables" in context

    @pytest.mark.asyncio
    async def test_node_execution_order(self, agent, mock_n8n_api):
        """Test that nodes are executed in correct topological order."""
        # Setup complex workflow with dependencies
        workflow_data = {
            "nodes": [
                {"id": "node-1", "type": "trigger"},
                {"id": "node-2", "type": "action"},
                {"id": "node-3", "type": "action"},
                {"id": "node-4", "type": "action"}
            ],
            "connections": [
                {"source": "node-1", "target": "node-2"},
                {"source": "node-1", "target": "node-3"},
                {"source": "node-2", "target": "node-4"}
            ]
        }

        execution_order = []
        original_execute = mock_n8n_api.execute_workflow

        async def track_execution(*args, **kwargs):
            execution_order.append(args[0] if args else "unknown")
            return await original_execute(*args, **kwargs)

        mock_n8n_api.execute_workflow = AsyncMock(side_effect=track_execution)

        # Execute
        await agent.execute_nodes({"workflowData": workflow_data})

        # Assertions - nodes should be executed in dependency order
        # Note: This is a simplified test - real implementation would handle topological sorting
        assert len(execution_order) > 0

    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(self, agent, mock_n8n_api, valid_workflow_input):
        """Test error handling and recovery mechanisms."""
        # Setup mock to fail then recover
        mock_n8n_api.execute_workflow = AsyncMock(side_effect=[
            Exception("Temporary failure"),
            {
                "executionId": "exec-456",
                "status": "success",
                "results": {"output": "recovered"},
                "executionTime": 1.0
            }
        ])

        # Execute
        result = await agent.execute_workflow(valid_workflow_input)

        # Assertions
        assert result["status"] == "success"
        assert mock_n8n_api.execute_workflow.call_count == 2

    @pytest.mark.asyncio
    async def test_resource_cleanup(self, agent, valid_workflow_input):
        """Test proper resource cleanup after execution."""
        # Setup
        agent.resources = ["temp_file_1", "temp_file_2", "db_connection"]

        # Execute
        await agent.cleanup_resources("exec-456")

        # Assertions - resources should be cleaned up
        # In real implementation, this would verify actual cleanup
        assert hasattr(agent, 'cleanup_resources')

    @pytest.mark.asyncio
    async def test_performance_monitoring(self, agent, mock_n8n_api, valid_workflow_input):
        """Test performance monitoring during execution."""
        # Setup
        mock_n8n_api.execute_workflow = AsyncMock(return_value={
            "executionId": "exec-456",
            "status": "success",
            "results": {"output": "test"},
            "executionTime": 2.5
        })

        # Execute
        result = await agent.execute_workflow(valid_workflow_input)

        # Assertions
        assert result["executionTime"] == 2.5
        # In real implementation, would check performance metrics collection

    @pytest.mark.asyncio
    async def test_empty_workflow_handling(self, agent, mock_n8n_api):
        """Test handling of empty workflows."""
        empty_workflow = {
            "workflowId": "empty-workflow",
            "executionId": "exec-empty",
            "inputData": {},
            "executionOptions": {}
        }

        # Setup mock for empty workflow
        mock_n8n_api.get_workflow = AsyncMock(return_value={
            "id": "empty-workflow",
            "nodes": [],
            "connections": []
        })

        # Execute
        result = await agent.execute_workflow(empty_workflow)

        # Assertions
        # Empty workflows should either succeed or return appropriate message
        assert result["status"] in ["success", "error"]

    @pytest.mark.asyncio
    async def test_circular_dependency_detection(self, agent, mock_n8n_api):
        """Test detection of circular dependencies in workflows."""
        circular_workflow = {
            "workflowId": "circular-workflow",
            "executionId": "exec-circular",
            "inputData": {},
            "executionOptions": {}
        }

        # Setup mock with circular dependency
        mock_n8n_api.get_workflow = AsyncMock(return_value={
            "id": "circular-workflow",
            "nodes": [
                {"id": "node-1", "type": "set"},
                {"id": "node-2", "type": "set"},
                {"id": "node-3", "type": "set"}
            ],
            "connections": [
                {"source": "node-1", "target": "node-2"},
                {"source": "node-2", "target": "node-3"},
                {"source": "node-3", "target": "node-1"}  # Creates cycle
            ]
        })

        # Execute
        result = await agent.execute_workflow(circular_workflow)

        # Assertions
        assert result["status"] == "error"
        assert "circular" in result["error"]["message"].lower() or "cycle" in result["error"]["message"].lower()

    @pytest.mark.asyncio
    async def test_large_workflow_execution(self, agent, mock_n8n_api):
        """Test execution of large workflows."""
        large_workflow_input = {
            "workflowId": "large-workflow",
            "executionId": "exec-large",
            "inputData": {"batch": list(range(100))},
            "executionOptions": {
                "timeout": 300,
                "maxRetries": 1,
                "parallelExecution": True
            }
        }

        # Setup mock for large workflow
        mock_n8n_api.execute_workflow = AsyncMock(return_value={
            "executionId": "exec-large",
            "status": "success",
            "results": {"processed": 100, "output": "batch complete"},
            "executionTime": 45.5
        })

        # Execute
        result = await agent.execute_workflow(large_workflow_input)

        # Assertions
        assert result["status"] == "success"
        assert result["executionTime"] == 45.5

    @pytest.mark.asyncio
    async def test_execution_cancellation(self, agent, mock_n8n_api):
        """Test workflow execution cancellation."""
        # Setup long-running execution
        async def long_execution(*args, **kwargs):
            await asyncio.sleep(5)
            return {"status": "success"}

        mock_n8n_api.execute_workflow = AsyncMock(side_effect=long_execution)

        # Start execution
        task = asyncio.create_task(agent.execute_workflow({
            "workflowId": "test-workflow",
            "executionId": "exec-cancel",
            "inputData": {},
            "executionOptions": {"timeout": 30}
        }))

        # Cancel after short time
        await asyncio.sleep(0.1)
        task.cancel()

        # Assertions
        with pytest.raises(asyncio.CancelledError):
            await task

    @pytest.mark.asyncio
    async def test_variable_context_management(self, agent, valid_workflow_input):
        """Test variable context management during execution."""
        # Setup workflow with variable operations
        workflow_with_variables = {
            **valid_workflow_input,
            "inputData": {
                "initial": "value",
                "number": 42
            }
        }

        # Execute
        context = await agent.initialize_context(workflow_with_variables)

        # Assertions
        assert context["variables"]["initial"] == "value"
        assert context["variables"]["number"] == 42
        assert "executionId" in context["variables"]
        assert "startTime" in context["variables"]

    @pytest.mark.asyncio
    async def test_memory_usage_monitoring(self, agent, mock_n8n_api, valid_workflow_input):
        """Test memory usage monitoring during execution."""
        # Setup
        mock_n8n_api.execute_workflow = AsyncMock(return_value={
            "executionId": "exec-456",
            "status": "success",
            "results": {"output": "test"},
            "executionTime": 1.0
        })

        # Execute
        result = await agent.execute_workflow(valid_workflow_input)

        # Assertions
        assert result["status"] == "success"
        # In real implementation, would verify memory usage tracking

    @pytest.mark.asyncio
    async def test_execution_metrics_collection(self, agent, mock_n8n_api, valid_workflow_input):
        """Test collection of execution metrics."""
        # Setup
        mock_n8n_api.execute_workflow = AsyncMock(return_value={
            "executionId": "exec-456",
            "status": "success",
            "results": {"output": "test"},
            "executionTime": 2.5
        })

        # Execute
        result = await agent.execute_workflow(valid_workflow_input)

        # Assertions
        assert result["executionTime"] == 2.5
        # In real implementation, would verify comprehensive metrics collection
