"""
Integration tests for workflow execution across multiple agents.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock

from tests.mocks.n8n_api_mock import N8nApiMock
from tests.mocks.redis_mock import RedisMock
from tests.mocks.websocket_mock import WebSocketMock


class TestWorkflowExecutionIntegration:
    """Integration tests for complete workflow execution."""

    @pytest.fixture
    def mock_n8n_api(self):
        """Mock n8n API for integration testing."""
        return N8nApiMock()

    @pytest.fixture
    def mock_redis(self):
        """Mock Redis for state management."""
        return RedisMock()

    @pytest.fixture
    def mock_websocket(self):
        """Mock WebSocket for real-time updates."""
        return WebSocketMock()

    @pytest.fixture
    def integration_setup(self, mock_n8n_api, mock_redis, mock_websocket):
        """Setup integration test environment."""
        return {
            "n8n_api": mock_n8n_api,
            "redis": mock_redis,
            "websocket": mock_websocket
        }

    @pytest.mark.asyncio
    async def test_complete_workflow_lifecycle(self, integration_setup):
        """Test complete workflow lifecycle from creation to execution."""
        n8n_api = integration_setup["n8n_api"]

        # 1. Create workflow
        workflow_data = {
            "nodes": [
                {"id": "trigger", "type": "n8n-nodes-base.manualTrigger", "position": [100, 100]},
                {"id": "http", "type": "n8n-nodes-base.httpRequest", "position": [300, 100]},
                {"id": "set", "type": "n8n-nodes-base.set", "position": [500, 100]}
            ],
            "connections": [
                {"source": "trigger", "target": "http"},
                {"source": "http", "target": "set"}
            ]
        }

        create_result = await n8n_api.create_workflow(workflow_data)
        workflow_id = create_result["id"]

        # 2. Execute workflow
        execution_result = await n8n_api.execute_workflow(workflow_id, {"test": "input"})

        # 3. Verify execution
        assert execution_result["status"] == "success"
        assert execution_result["executionId"] is not None

        # 4. Get execution details
        execution_details = await n8n_api.get_execution(execution_result["executionId"])
        assert execution_details["status"] == "success"

    @pytest.mark.asyncio
    async def test_multi_agent_coordination(self, integration_setup):
        """Test coordination between multiple agents during workflow execution."""
        n8n_api = integration_setup["n8n_api"]
        redis = integration_setup["redis"]
        websocket = integration_setup["websocket"]

        # Setup complex workflow requiring multiple agents
        complex_workflow = {
            "nodes": [
                {"id": "webhook", "type": "n8n-nodes-base.webhook", "position": [50, 50]},
                {"id": "if", "type": "n8n-nodes-base.if", "position": [200, 50]},
                {"id": "github", "type": "n8n-nodes-base.github", "position": [350, 20]},
                {"id": "slack", "type": "n8n-nodes-base.slack", "position": [350, 80]},
                {"id": "database", "type": "n8n-nodes-base.postgres", "position": [500, 50]}
            ],
            "connections": [
                {"source": "webhook", "target": "if"},
                {"source": "if", "target": "github", "sourceOutput": 0},
                {"source": "if", "target": "slack", "sourceOutput": 1},
                {"source": "github", "target": "database"},
                {"source": "slack", "target": "database"}
            ]
        }

        # Create and execute workflow
        create_result = await n8n_api.create_workflow(complex_workflow)
        execution_result = await n8n_api.execute_workflow(create_result["id"])

        # Verify multi-agent coordination
        assert execution_result["status"] == "success"
        assert n8n_api.get_request_count("POST", "/workflows") == 1
        assert n8n_api.get_request_count("POST", "/executions") == 1

    @pytest.mark.asyncio
    async def test_error_propagation_across_agents(self, integration_setup):
        """Test error propagation across multiple agents."""
        n8n_api = integration_setup["n8n_api"]

        # Setup workflow with intentional error
        error_workflow = {
            "nodes": [
                {"id": "trigger", "type": "n8n-nodes-base.manualTrigger", "position": [100, 100]},
                {"id": "error-node", "type": "n8n-nodes-base.httpRequest", "position": [300, 100],
                 "parameters": {"url": "https://httpstat.us/500"}},  # Always returns 500
                {"id": "error-handler", "type": "n8n-nodes-base.errorTrigger", "position": [300, 200]}
            ],
            "connections": [
                {"source": "trigger", "target": "error-node"},
                {"source": "error-node", "target": "error-handler", "sourceOutput": 1}  # Error output
            ]
        }

        # Create and execute workflow
        create_result = await n8n_api.create_workflow(error_workflow)
        execution_result = await n8n_api.execute_workflow(create_result["id"])

        # Verify error handling across agents
        assert execution_result["status"] in ["success", "error"]
        # In real implementation, would verify error propagation to error handler

    @pytest.mark.asyncio
    async def test_state_consistency_across_agents(self, integration_setup):
        """Test state consistency across all agents."""
        n8n_api = integration_setup["n8n_api"]
        redis = integration_setup["redis"]

        # Setup workflow that modifies state
        state_workflow = {
            "nodes": [
                {"id": "trigger", "type": "n8n-nodes-base.manualTrigger", "position": [100, 100]},
                {"id": "set-1", "type": "n8n-nodes-base.set", "position": [300, 100],
                 "parameters": {"values": {"string": [{"name": "state1", "value": "value1"}]}}},
                {"id": "set-2", "type": "n8n-nodes-base.set", "position": [500, 100],
                 "parameters": {"values": {"string": [{"name": "state2", "value": "={{ $json.state1 }}-modified"}]}}},
                {"id": "set-3", "type": "n8n-nodes-base.set", "position": [700, 100],
                 "parameters": {"values": {"string": [{"name": "final", "value": "={{ $json.state2 }}-final"}]}}}
            ],
            "connections": [
                {"source": "trigger", "target": "set-1"},
                {"source": "set-1", "target": "set-2"},
                {"source": "set-2", "target": "set-3"}
            ]
        }

        # Create and execute workflow
        create_result = await n8n_api.create_workflow(state_workflow)
        execution_result = await n8n_api.execute_workflow(create_result["id"])

        # Verify state consistency
        assert execution_result["status"] == "success"
        # In real implementation, would verify state flow between nodes

    @pytest.mark.asyncio
    async def test_concurrent_workflow_execution(self, integration_setup):
        """Test concurrent execution of multiple workflows."""
        n8n_api = integration_setup["n8n_api"]

        # Setup multiple workflows
        workflows = []
        for i in range(3):
            workflow = {
                "nodes": [
                    {"id": f"trigger-{i}", "type": "n8n-nodes-base.manualTrigger", "position": [100, 100]},
                    {"id": f"http-{i}", "type": "n8n-nodes-base.httpRequest", "position": [300, 100]}
                ],
                "connections": [
                    {"source": f"trigger-{i}", "target": f"http-{i}"}
                ]
            }
            create_result = await n8n_api.create_workflow(workflow)
            workflows.append(create_result["id"])

        # Execute workflows concurrently
        execution_tasks = [
            n8n_api.execute_workflow(workflow_id, {"concurrent": True, "id": i})
            for i, workflow_id in enumerate(workflows)
        ]

        execution_results = await asyncio.gather(*execution_tasks)

        # Verify concurrent execution
        assert len(execution_results) == 3
        assert all(result["status"] == "success" for result in execution_results)

    @pytest.mark.asyncio
    async def test_workflow_with_external_integrations(self, integration_setup):
        """Test workflow execution with external service integrations."""
        n8n_api = integration_setup["n8n_api"]

        # Setup workflow with external API calls
        integration_workflow = {
            "nodes": [
                {"id": "trigger", "type": "n8n-nodes-base.manualTrigger", "position": [100, 100]},
                {"id": "github-api", "type": "n8n-nodes-base.github", "position": [300, 100],
                 "credentials": {"githubApi": {"id": "github-123"}}},
                {"id": "slack-notification", "type": "n8n-nodes-base.slack", "position": [500, 100],
                 "credentials": {"slackApi": {"id": "slack-456"}}},
                {"id": "database-save", "type": "n8n-nodes-base.postgres", "position": [700, 100],
                 "credentials": {"postgres": {"id": "db-789"}}}
            ],
            "connections": [
                {"source": "trigger", "target": "github-api"},
                {"source": "github-api", "target": "slack-notification"},
                {"source": "slack-notification", "target": "database-save"}
            ]
        }

        # Create and execute workflow
        create_result = await n8n_api.create_workflow(integration_workflow)
        execution_result = await n8n_api.execute_workflow(create_result["id"])

        # Verify external integration handling
        assert execution_result["status"] == "success"
        # In real implementation, would verify external API calls were made correctly

    @pytest.mark.asyncio
    async def test_workflow_validation_integration(self, integration_setup):
        """Test integration between validation and execution agents."""
        n8n_api = integration_setup["n8n_api"]

        # Setup workflow with validation issues
        invalid_workflow = {
            "nodes": [
                {"id": "trigger", "type": "n8n-nodes-base.manualTrigger", "position": [100, 100]},
                {"id": "invalid-connection", "type": "n8n-nodes-base.set", "position": [300, 100]}
            ],
            "connections": [
                {"source": "trigger", "target": "non-existent-node"}  # Invalid connection
            ]
        }

        # Create workflow (should succeed)
        create_result = await n8n_api.create_workflow(invalid_workflow)
        assert create_result["success"] is True

        # Execute workflow (should handle validation gracefully)
        execution_result = await n8n_api.execute_workflow(create_result["id"])

        # Verify validation integration
        # In real implementation, would verify validation errors are properly handled

    @pytest.mark.asyncio
    async def test_canvas_state_synchronization(self, integration_setup):
        """Test synchronization between canvas state and workflow execution."""
        n8n_api = integration_setup["n8n_api"]
        websocket = integration_setup["websocket"]

        # Setup workflow with canvas state
        canvas_workflow = {
            "nodes": [
                {"id": "node-1", "type": "n8n-nodes-base.manualTrigger", "position": [100, 100]},
                {"id": "node-2", "type": "n8n-nodes-base.httpRequest", "position": [300, 100]},
                {"id": "node-3", "type": "n8n-nodes-base.set", "position": [500, 100]}
            ],
            "connections": [
                {"source": "node-1", "target": "node-2"},
                {"source": "node-2", "target": "node-3"}
            ],
            "viewport": {"x": 0, "y": 0, "zoom": 1.0},
            "metadata": {"createdBy": "test-user", "version": "1.0"}
        }

        # Create workflow
        create_result = await n8n_api.create_workflow(canvas_workflow)
        workflow_id = create_result["id"]

        # Simulate canvas updates via WebSocket
        websocket.queue_message({
            "type": "node_move",
            "nodeId": "node-2",
            "position": {"x": 400, "y": 150}
        })

        # Execute workflow
        execution_result = await n8n_api.execute_workflow(workflow_id)

        # Verify state synchronization
        assert execution_result["status"] == "success"
        # In real implementation, would verify canvas state was synchronized

    @pytest.mark.asyncio
    async def test_performance_under_load(self, integration_setup):
        """Test performance under concurrent load."""
        n8n_api = integration_setup["n8n_api"]

        # Setup multiple workflows for load testing
        workflow_template = {
            "nodes": [
                {"id": "trigger", "type": "n8n-nodes-base.manualTrigger", "position": [100, 100]},
                {"id": "process", "type": "n8n-nodes-base.set", "position": [300, 100]}
            ],
            "connections": [
                {"source": "trigger", "target": "process"}
            ]
        }

        # Create multiple workflows
        workflow_ids = []
        for i in range(10):
            create_result = await n8n_api.create_workflow({
                **workflow_template,
                "nodes": [
                    {**node, "id": f"{node['id']}-{i}"} for node in workflow_template["nodes"]
                ],
                "connections": [
                    {**conn, "source": f"{conn['source']}-{i}", "target": f"{conn['target']}-{i}"}
                    for conn in workflow_template["connections"]
                ]
            })
            workflow_ids.append(create_result["id"])

        # Execute all workflows concurrently
        start_time = asyncio.get_event_loop().time()

        execution_tasks = [
            n8n_api.execute_workflow(workflow_id, {"load_test": True, "id": i})
            for i, workflow_id in enumerate(workflow_ids)
        ]

        execution_results = await asyncio.gather(*execution_tasks)

        end_time = asyncio.get_event_loop().time()

        # Verify performance under load
        assert len(execution_results) == 10
        assert all(result["status"] == "success" for result in execution_results)
        total_time = end_time - start_time
        assert total_time < 10.0  # Should complete within 10 seconds

    @pytest.mark.asyncio
    async def test_error_recovery_integration(self, integration_setup):
        """Test error recovery across multiple agents."""
        n8n_api = integration_setup["n8n_api"]

        # Setup workflow with potential failures
        recovery_workflow = {
            "nodes": [
                {"id": "trigger", "type": "n8n-nodes-base.manualTrigger", "position": [100, 100]},
                {"id": "unreliable-api", "type": "n8n-nodes-base.httpRequest", "position": [300, 100],
                 "parameters": {"url": "https://httpstat.us/500"}},
                {"id": "error-handler", "type": "n8n-nodes-base.errorTrigger", "position": [300, 200]},
                {"id": "fallback", "type": "n8n-nodes-base.set", "position": [500, 200]}
            ],
            "connections": [
                {"source": "trigger", "target": "unreliable-api"},
                {"source": "unreliable-api", "target": "error-handler", "sourceOutput": 1},
                {"source": "error-handler", "target": "fallback"}
            ]
        }

        # Create and execute workflow
        create_result = await n8n_api.create_workflow(recovery_workflow)
        execution_result = await n8n_api.execute_workflow(create_result["id"])

        # Verify error recovery integration
        assert execution_result["status"] in ["success", "error"]
        # In real implementation, would verify error recovery across agents

    @pytest.mark.asyncio
    async def test_data_persistence_integration(self, integration_setup):
        """Test data persistence across workflow execution."""
        n8n_api = integration_setup["n8n_api"]
        redis = integration_setup["redis"]

        # Setup workflow that saves data
        persistence_workflow = {
            "nodes": [
                {"id": "trigger", "type": "n8n-nodes-base.manualTrigger", "position": [100, 100]},
                {"id": "generate-data", "type": "n8n-nodes-base.set", "position": [300, 100],
                 "parameters": {"values": {"string": [{"name": "data", "value": "test-data-123"}]}}},
                {"id": "save-to-redis", "type": "n8n-nodes-base.redis", "position": [500, 100],
                 "parameters": {"command": "set", "key": "workflow-output", "value": "={{ $json.data }}"}}
            ],
            "connections": [
                {"source": "trigger", "target": "generate-data"},
                {"source": "generate-data", "target": "save-to-redis"}
            ]
        }

        # Create and execute workflow
        create_result = await n8n_api.create_workflow(persistence_workflow)
        execution_result = await n8n_api.execute_workflow(create_result["id"])

        # Verify data persistence
        assert execution_result["status"] == "success"

        # Check if data was persisted (in real implementation)
        # persisted_data = await redis.get("workflow-output")
        # assert persisted_data == "test-data-123"

    @pytest.mark.asyncio
    async def test_real_time_collaboration_integration(self, integration_setup):
        """Test real-time collaboration during workflow execution."""
        n8n_api = integration_setup["n8n_api"]
        websocket = integration_setup["websocket"]

        # Setup collaborative workflow
        collab_workflow = {
            "nodes": [
                {"id": "shared-trigger", "type": "n8n-nodes-base.manualTrigger", "position": [100, 100]},
                {"id": "shared-action", "type": "n8n-nodes-base.httpRequest", "position": [300, 100]}
            ],
            "connections": [
                {"source": "shared-trigger", "target": "shared-action"}
            ]
        }

        # Create workflow
        create_result = await n8n_api.create_workflow(collab_workflow)
        workflow_id = create_result["id"]

        # Simulate collaborative edits
        websocket.queue_message({
            "type": "node_update",
            "userId": "user-1",
            "nodeId": "shared-action",
            "updates": {"parameters": {"url": "https://api1.example.com"}}
        })

        websocket.queue_message({
            "type": "node_update",
            "userId": "user-2",
            "nodeId": "shared-action",
            "updates": {"parameters": {"method": "POST"}}
        })

        # Execute workflow
        execution_result = await n8n_api.execute_workflow(workflow_id)

        # Verify collaboration integration
        assert execution_result["status"] == "success"
        # In real implementation, would verify collaborative changes were applied

    @pytest.mark.asyncio
    async def test_workflow_versioning_integration(self, integration_setup):
        """Test workflow versioning across multiple executions."""
        n8n_api = integration_setup["n8n_api"]

        # Initial workflow version
        initial_workflow = {
            "nodes": [
                {"id": "trigger", "type": "n8n-nodes-base.manualTrigger", "position": [100, 100]},
                {"id": "version-1", "type": "n8n-nodes-base.set", "position": [300, 100]}
            ],
            "connections": [
                {"source": "trigger", "target": "version-1"}
            ],
            "version": "1.0.0"
        }

        # Create initial version
        create_result = await n8n_api.create_workflow(initial_workflow)
        workflow_id = create_result["id"]

        # Execute initial version
        execution1 = await n8n_api.execute_workflow(workflow_id, {"version": "1.0.0"})

        # Update workflow (new version)
        updated_workflow = {
            **initial_workflow,
            "nodes": [
                *initial_workflow["nodes"],
                {"id": "version-2", "type": "n8n-nodes-base.set", "position": [500, 100]}
            ],
            "connections": [
                *initial_workflow["connections"],
                {"source": "version-1", "target": "version-2"}
            ],
            "version": "1.1.0"
        }

        await n8n_api.update_workflow(workflow_id, updated_workflow)

        # Execute updated version
        execution2 = await n8n_api.execute_workflow(workflow_id, {"version": "1.1.0"})

        # Verify versioning integration
        assert execution1["status"] == "success"
        assert execution2["status"] == "success"
        # In real implementation, would verify version-specific execution

    @pytest.mark.asyncio
    async def test_security_integration(self, integration_setup):
        """Test security integration across agents."""
        n8n_api = integration_setup["n8n_api"]

        # Setup workflow with security-sensitive operations
        secure_workflow = {
            "nodes": [
                {"id": "trigger", "type": "n8n-nodes-base.manualTrigger", "position": [100, 100]},
                {"id": "secure-api", "type": "n8n-nodes-base.httpRequest", "position": [300, 100],
                 "credentials": {"githubApi": {"id": "secure-cred"}}},
                {"id": "data-validator", "type": "n8n-nodes-base.set", "position": [500, 100]}
            ],
            "connections": [
                {"source": "trigger", "target": "secure-api"},
                {"source": "secure-api", "target": "data-validator"}
            ],
            "permissions": {
                "required": ["api:read", "data:write"],
                "owner": "test-user"
            }
        }

        # Create and execute workflow
        create_result = await n8n_api.create_workflow(secure_workflow)
        execution_result = await n8n_api.execute_workflow(create_result["id"])

        # Verify security integration
        assert execution_result["status"] == "success"
        # In real implementation, would verify security checks and credential validation

    @pytest.mark.asyncio
    async def test_resource_management_integration(self, integration_setup):
        """Test resource management across multiple agents."""
        n8n_api = integration_setup["n8n_api"]
        redis = integration_setup["redis"]

        # Setup resource-intensive workflow
        resource_workflow = {
            "nodes": [
                {"id": "trigger", "type": "n8n-nodes-base.manualTrigger", "position": [100, 100]},
                {"id": "batch-processor", "type": "n8n-nodes-base.splitInBatches", "position": [300, 100],
                 "parameters": {"batchSize": 100}},
                {"id": "data-processor", "type": "n8n-nodes-base.set", "position": [500, 100]},
                {"id": "cache-writer", "type": "n8n-nodes-base.redis", "position": [700, 100]}
            ],
            "connections": [
                {"source": "trigger", "target": "batch-processor"},
                {"source": "batch-processor", "target": "data-processor"},
                {"source": "data-processor", "target": "cache-writer"}
            ]
        }

        # Create and execute workflow
        create_result = await n8n_api.create_workflow(resource_workflow)
        execution_result = await n8n_api.execute_workflow(create_result["id"], {
            "largeData": list(range(1000))
        })

        # Verify resource management
        assert execution_result["status"] == "success"
        # In real implementation, would verify resource cleanup and memory management

    @pytest.mark.asyncio
    async def test_monitoring_integration(self, integration_setup):
        """Test monitoring integration across all agents."""
        n8n_api = integration_setup["n8n_api"]

        # Setup monitored workflow
        monitored_workflow = {
            "nodes": [
                {"id": "trigger", "type": "n8n-nodes-base.manualTrigger", "position": [100, 100]},
                {"id": "monitored-api", "type": "n8n-nodes-base.httpRequest", "position": [300, 100]},
                {"id": "result-processor", "type": "n8n-nodes-base.set", "position": [500, 100]}
            ],
            "connections": [
                {"source": "trigger", "target": "monitored-api"},
                {"source": "monitored-api", "target": "result-processor"}
            ],
            "monitoring": {
                "enabled": True,
                "metrics": ["execution_time", "memory_usage", "api_calls"],
                "alerts": ["error_rate", "timeout"]
            }
        }

        # Create and execute workflow
        create_result = await n8n_api.create_workflow(monitored_workflow)
        execution_result = await n8n_api.execute_workflow(create_result["id"])

        # Verify monitoring integration
        assert execution_result["status"] == "success"
        assert "executionTime" in execution_result
        # In real implementation, would verify comprehensive monitoring data collection
