# Testing Plan - n8n Visual Workflow Builder

## Overview

This comprehensive testing plan ensures the reliability, performance, and correctness of the n8n visual workflow builder system. The testing strategy covers unit tests for individual agents, integration tests for workflow orchestration, comprehensive mocking for external dependencies, and systematic validation of edge cases and error conditions.

## Testing Architecture

### Test Categories

1. **Unit Tests**: Individual agent functionality and business logic
2. **Integration Tests**: Multi-agent workflows and external service interactions
3. **End-to-End Tests**: Complete user workflows from UI to execution
4. **Performance Tests**: Load testing and stress testing scenarios
5. **Security Tests**: Authentication, authorization, and data protection

### Test Organization

```
tests/
├── unit/
│   ├── agents/
│   │   ├── test_workflow_execution_agent.py
│   │   ├── test_node_validation_agent.py
│   │   ├── test_canvas_manager_agent.py
│   │   ├── test_integration_agent.py
│   │   └── test_export_import_agent.py
│   ├── components/
│   ├── services/
│   └── utils/
├── integration/
│   ├── test_workflow_execution.py
│   ├── test_canvas_collaboration.py
│   ├── test_external_integrations.py
│   └── test_import_export.py
├── e2e/
│   ├── test_complete_workflow_creation.py
│   ├── test_user_collaboration.py
│   └── test_workflow_execution_ui.py
├── mocks/
│   ├── n8n_api_mock.py
│   ├── redis_mock.py
│   ├── websocket_mock.py
│   └── external_services_mock.py
├── fixtures/
│   ├── sample_workflows.py
│   ├── test_credentials.py
│   └── canvas_states.py
├── utils/
│   ├── test_helpers.py
│   ├── assertions.py
│   └── factories.py
└── conftest.py
```

## Unit Test Plan for Agents

### WorkflowExecutionAgent Tests

#### Core Functionality Tests
- **test_workflow_initialization**: Verify proper initialization with input parameters
- **test_context_setup**: Validate execution context creation and state management
- **test_node_execution_order**: Ensure topological execution order is maintained
- **test_parallel_execution**: Test concurrent node execution capabilities
- **test_state_persistence**: Verify workflow state is properly saved to Redis

#### Error Handling Tests
- **test_validation_failure**: Handle invalid workflow structures gracefully
- **test_execution_timeout**: Manage workflow execution timeouts
- **test_retry_logic**: Implement exponential backoff retry mechanism
- **test_partial_failure_recovery**: Continue execution after individual node failures

#### Edge Cases
- **test_empty_workflow**: Handle workflows with no executable nodes
- **test_circular_dependencies**: Detect and handle circular node dependencies
- **test_large_workflow**: Performance with workflows containing 100+ nodes
- **test_memory_cleanup**: Ensure proper resource cleanup after execution

### NodeValidationAgent Tests

#### Schema Validation Tests
- **test_parameter_validation**: Validate node parameters against JSON schemas
- **test_required_fields**: Ensure all required parameters are present
- **test_data_type_compatibility**: Verify data type matching between connected nodes
- **test_custom_validation_rules**: Test domain-specific validation logic

#### Connection Tests
- **test_valid_connections**: Verify compatible node type connections
- **test_invalid_connections**: Reject incompatible node connections
- **test_connection_loops**: Detect and prevent infinite loops in connections
- **test_missing_connections**: Handle workflows with unconnected nodes

#### Performance Tests
- **test_validation_speed**: Ensure validation completes within acceptable time
- **test_batch_validation**: Validate multiple nodes simultaneously
- **test_schema_caching**: Verify schema caching improves performance

### CanvasManagerAgent Tests

#### State Management Tests
- **test_canvas_initialization**: Proper canvas setup with ReactFlow
- **test_node_positioning**: Accurate node positioning and movement
- **test_zoom_controls**: Zoom in/out functionality and bounds
- **test_selection_management**: Single and multi-node selection

#### Collaboration Tests
- **test_websocket_events**: Real-time collaboration via WebSocket
- **test_conflict_resolution**: Handle simultaneous edits by multiple users
- **test_state_synchronization**: Ensure all clients maintain consistent state
- **test_offline_mode**: Handle temporary disconnection scenarios

#### Persistence Tests
- **test_auto_save**: Automatic state saving at configured intervals
- **test_state_restoration**: Restore canvas state after application restart
- **test_undo_redo**: Comprehensive undo/redo functionality

### IntegrationAgent Tests

#### Authentication Tests
- **test_oauth_flow**: Complete OAuth2 authorization flow
- **test_api_key_validation**: API key authentication and validation
- **test_credential_encryption**: Secure credential storage and retrieval
- **test_token_refresh**: Automatic token refresh before expiration

#### Service Interaction Tests
- **test_service_health_check**: Monitor external service availability
- **test_rate_limiting**: Implement and respect API rate limits
- **test_request_retry**: Retry failed requests with exponential backoff
- **test_data_transformation**: Convert data between different formats

#### Security Tests
- **test_credential_isolation**: Ensure credentials are isolated per user
- **test_permission_validation**: Validate user permissions for service access
- **test_audit_logging**: Log all integration activities for security

### ExportImportAgent Tests

#### Serialization Tests
- **test_json_export**: Export workflows as n8n-compatible JSON
- **test_yaml_export**: Export workflows in YAML format
- **test_template_creation**: Create reusable workflow templates
- **test_version_control**: Integration with git for version management

#### Import Tests
- **test_workflow_import**: Import workflows from various formats
- **test_validation_import**: Validate imported workflows for compatibility
- **test_conflict_resolution**: Handle naming conflicts during import
- **test_partial_import**: Import individual nodes or node groups

#### File Operations Tests
- **test_file_permissions**: Ensure proper file system permissions
- **test_large_file_handling**: Handle large workflow files efficiently
- **test_format_conversion**: Convert between different workflow formats

## Integration Test Plan for Workflows

### Multi-Agent Workflow Tests

#### Basic Workflow Execution
- **test_simple_linear_workflow**: Execute a basic 3-node workflow
- **test_branching_workflow**: Test workflows with conditional branching
- **test_parallel_workflow**: Execute workflows with parallel node execution
- **test_loop_workflow**: Test workflows containing loops

#### Complex Orchestration Tests
- **test_agent_coordination**: Verify proper coordination between all agents
- **test_event_flow**: Test event passing between agents
- **test_state_consistency**: Ensure state consistency across all agents
- **test_error_propagation**: Test error handling across agent boundaries

#### Performance Integration Tests
- **test_concurrent_workflows**: Execute multiple workflows simultaneously
- **test_resource_utilization**: Monitor CPU, memory, and network usage
- **test_scalability**: Test system performance with increasing load
- **test_memory_leaks**: Ensure no memory leaks during extended operation

### External Service Integration Tests

#### n8n API Integration
- **test_workflow_sync**: Synchronize workflows with n8n server
- **test_execution_results**: Validate execution results against n8n
- **test_credential_sharing**: Share credentials between systems
- **test_webhook_handling**: Process incoming webhooks from n8n

#### Database Integration Tests
- **test_workflow_persistence**: Save and restore workflows from database
- **test_user_management**: User authentication and authorization
- **test_audit_trails**: Maintain comprehensive audit logs
- **test_backup_restore**: Backup and restore functionality

### Real-time Collaboration Tests

#### WebSocket Integration
- **test_live_collaboration**: Multiple users editing simultaneously
- **test_conflict_resolution**: Automatic resolution of edit conflicts
- **test_connection_recovery**: Handle WebSocket disconnections
- **test_presence_indication**: Show active users in the session

#### State Synchronization
- **test_immediate_consistency**: Ensure immediate state consistency
- **test_eventual_consistency**: Handle eventual consistency scenarios
- **test_offline_sync**: Synchronize changes when users come back online

## Mocking Strategies for External APIs

### n8n API Mocking

#### Mock Setup
```python
# tests/mocks/n8n_api_mock.py
class N8nApiMock:
    def __init__(self):
        self.workflows = {}
        self.executions = {}

    def mock_workflow_create(self, workflow_data):
        """Mock workflow creation endpoint"""
        workflow_id = generate_id()
        self.workflows[workflow_id] = workflow_data
        return {"id": workflow_id, "success": True}

    def mock_workflow_execute(self, workflow_id, input_data):
        """Mock workflow execution endpoint"""
        return {
            "executionId": generate_id(),
            "status": "success",
            "results": {"output": "mocked_result"}
        }
```

#### Usage in Tests
```python
# tests/unit/agents/test_workflow_execution_agent.py
def test_workflow_execution_success(mock_n8n_api):
    agent = WorkflowExecutionAgent(mock_n8n_api, mock_state_manager)
    result = await agent.execute_workflow(valid_workflow_data)

    assert result.status == "success"
    mock_n8n_api.mock_workflow_execute.assert_called_once()
```

### Redis Mocking

#### Redis Mock Implementation
```python
# tests/mocks/redis_mock.py
class RedisMock:
    def __init__(self):
        self.data = {}

    async def set(self, key: str, value: str, ex: int = None):
        """Mock Redis SET operation"""
        self.data[key] = {"value": value, "ttl": ex}
        return True

    async def get(self, key: str):
        """Mock Redis GET operation"""
        if key in self.data:
            entry = self.data[key]
            if entry["ttl"] and time.time() > entry["ttl"]:
                del self.data[key]
                return None
            return entry["value"]
        return None
```

### WebSocket Mocking

#### WebSocket Mock Implementation
```python
# tests/mocks/websocket_mock.py
class WebSocketMock:
    def __init__(self):
        self.connections = []
        self.messages = []

    async def connect(self, url: str):
        """Mock WebSocket connection"""
        connection = {"url": url, "connected": True}
        self.connections.append(connection)
        return connection

    async def send(self, message: dict):
        """Mock message sending"""
        self.messages.append({
            "type": "send",
            "message": message,
            "timestamp": time.time()
        })

    async def receive(self):
        """Mock message receiving"""
        if self.messages:
            return self.messages.pop(0)
        return None
```

### External Service Mocking

#### Generic Service Mock
```python
# tests/mocks/external_services_mock.py
class ExternalServiceMock:
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.request_count = 0
        self.responses = {}

    def configure_response(self, endpoint: str, response: dict, delay: float = 0):
        """Configure mock responses for specific endpoints"""
        self.responses[endpoint] = {"response": response, "delay": delay}

    async def make_request(self, method: str, endpoint: str, data: dict = None):
        """Mock HTTP request to external service"""
        self.request_count += 1

        if endpoint in self.responses:
            config = self.responses[endpoint]
            if config["delay"]:
                await asyncio.sleep(config["delay"])
            return config["response"]

        return {"error": "Mock not configured for this endpoint"}
```

## Expected Behaviors and Edge Cases

### Normal Operation Behaviors

#### WorkflowExecutionAgent
- **Success Path**: Workflow executes all nodes in correct order and returns expected results
- **State Management**: Execution state is properly maintained throughout the process
- **Resource Cleanup**: All temporary resources are cleaned up after execution
- **Performance**: Execution completes within configured timeout limits

#### NodeValidationAgent
- **Real-time Feedback**: Validation results are provided immediately as user types
- **Clear Error Messages**: Specific, actionable error messages for validation failures
- **Performance**: Validation completes quickly even for complex workflows
- **Caching**: Schema validation results are cached to improve performance

#### CanvasManagerAgent
- **Smooth Interactions**: All canvas interactions feel responsive and smooth
- **Accurate Positioning**: Nodes maintain precise positions during drag operations
- **Consistent State**: Canvas state remains consistent across all connected clients
- **Auto-save**: Changes are automatically saved without user intervention

### Edge Cases and Error Conditions

#### Network Failures
- **API Unavailability**: Handle n8n API being temporarily unavailable
- **WebSocket Disconnection**: Graceful handling of WebSocket connection loss
- **External Service Outage**: Continue operation when external services are down
- **Database Connectivity**: Handle database connection failures

#### Data Corruption
- **Invalid JSON**: Handle malformed workflow JSON files
- **Missing Nodes**: Workflows with references to non-existent nodes
- **Corrupted State**: Recover from corrupted canvas or execution state
- **Invalid Credentials**: Handle expired or invalid authentication credentials

#### Resource Constraints
- **Memory Limits**: Handle workflows that exceed available memory
- **CPU Limits**: Manage workflows with high computational requirements
- **Storage Limits**: Handle workflows that exceed storage capacity
- **Concurrent Users**: Manage multiple users accessing the same workflow

#### Security Edge Cases
- **Unauthorized Access**: Prevent access to workflows without proper permissions
- **Credential Theft**: Handle compromised user credentials
- **Injection Attacks**: Prevent code injection through workflow parameters
- **Data Leakage**: Ensure sensitive data is not exposed in logs or error messages

### Performance Edge Cases

#### Large Scale Workflows
- **1000+ Nodes**: Handle workflows with very large numbers of nodes
- **Deep Nesting**: Workflows with deeply nested conditional logic
- **High Frequency**: Workflows that execute very frequently
- **Long Running**: Workflows that run for extended periods

#### Concurrent Operations
- **Multiple Users**: Many users editing the same workflow simultaneously
- **Bulk Operations**: Importing or exporting many workflows at once
- **Batch Execution**: Executing multiple workflows concurrently
- **Resource Competition**: Managing resource allocation between competing workflows

## Test Data and Fixtures

### Sample Workflows
```python
# tests/fixtures/sample_workflows.py
SIMPLE_WORKFLOW = {
    "nodes": [
        {
            "id": "trigger",
            "type": "n8n-nodes-base.manualTrigger",
            "position": [100, 100]
        },
        {
            "id": "http",
            "type": "n8n-nodes-base.httpRequest",
            "position": [300, 100],
            "parameters": {
                "method": "GET",
                "url": "https://api.example.com/data"
            }
        }
    ],
    "connections": [
        {
            "from": "trigger",
            "to": "http",
            "output": 0,
            "input": 0
        }
    ]
}

COMPLEX_WORKFLOW = {
    "nodes": [
        {"id": "webhook", "type": "n8n-nodes-base.webhook", "position": [50, 50]},
        {"id": "if", "type": "n8n-nodes-base.if", "position": [200, 50]},
        {"id": "email1", "type": "n8n-nodes-base.gmail", "position": [350, 20]},
        {"id": "email2", "type": "n8n-nodes-base.gmail", "position": [350, 80]},
        {"id": "database", "type": "n8n-nodes-base.postgres", "position": [500, 50]}
    ],
    "connections": [
        {"from": "webhook", "to": "if", "output": 0, "input": 0},
        {"from": "if", "to": "email1", "output": 0, "input": 0},
        {"from": "if", "to": "email2", "output": 1, "input": 0},
        {"from": "email1", "to": "database", "output": 0, "input": 0},
        {"from": "email2", "to": "database", "output": 0, "input": 0}
    ]
}
```

### Test Credentials
```python
# tests/fixtures/test_credentials.py
TEST_CREDENTIALS = {
    "valid_api_key": "test-api-key-12345",
    "invalid_api_key": "invalid-key",
    "expired_token": "expired-token-123",
    "oauth_config": {
        "client_id": "test-client-id",
        "client_secret": "test-client-secret",
        "redirect_uri": "http://localhost:3000/callback"
    }
}
```

### Canvas States
```python
# tests/fixtures/canvas_states.py
EMPTY_CANVAS = {"nodes": [], "edges": [], "viewport": {"x": 0, "y": 0, "zoom": 1}}

LOADED_CANVAS = {
    "nodes": [
        {"id": "1", "type": "trigger", "position": {"x": 100, "y": 100}},
        {"id": "2", "type": "action", "position": {"x": 300, "y": 100}}
    ],
    "edges": [
        {"id": "e1-2", "source": "1", "target": "2"}
    ],
    "viewport": {"x": 0, "y": 0, "zoom": 1}
}
```

## Test Execution and Reporting

### Test Running
```bash
# Run all tests
npm test

# Run unit tests only
npm run test:unit

# Run integration tests only
npm run test:integration

# Run tests with coverage
npm run test:coverage

# Run specific agent tests
npm run test:agents

# Run performance tests
npm run test:performance
```

### Coverage Requirements
- **Minimum Coverage**: 90% code coverage for all agent classes
- **Critical Path Coverage**: 100% coverage for error handling paths
- **Integration Coverage**: 95% coverage for multi-agent interactions
- **API Coverage**: 100% coverage for all external API interactions

### Test Reporting
- **JUnit XML**: Generate JUnit XML reports for CI/CD integration
- **HTML Coverage**: Generate HTML coverage reports for developer review
- **Performance Metrics**: Track test execution times and resource usage
- **Failure Analysis**: Detailed reporting of test failures with stack traces

## Continuous Integration

### CI Pipeline
1. **Linting**: Run ESLint and Prettier checks
2. **Type Checking**: Run TypeScript compiler checks
3. **Unit Tests**: Execute all unit tests with coverage reporting
4. **Integration Tests**: Run integration tests in isolated environment
5. **Build**: Build production bundle and run smoke tests
6. **Security Scan**: Run security vulnerability scans

### Quality Gates
- **Zero Failing Tests**: All tests must pass before merging
- **Coverage Threshold**: Minimum 90% code coverage required
- **Performance Budget**: Tests must complete within time budget
- **Security Compliance**: No high-severity security vulnerabilities

This comprehensive testing plan ensures the n8n visual workflow builder meets the highest standards of reliability, performance, and user experience.
