# Agent Implementation Specifications

## Overview

This document defines the autonomous agents used in the n8n visual workflow builder system. Each agent is a specialized component that handles specific aspects of workflow creation, validation, execution, and management. Agents communicate through a centralized event system and state management layer.

## Agent Types

### WorkflowExecutionAgent
**Role:** Manages workflow execution lifecycle, state transitions, and runtime orchestration

**Capabilities:**
- Execute workflows in sequence or parallel
- Manage execution state and variable context
- Handle errors and implement retry logic
- Monitor performance and resource usage
- Provide real-time execution feedback

**Dependencies:**
- n8n API for workflow execution
- Redis for state persistence
- WebSocket service for real-time updates

**Inputs:**
```typescript
interface WorkflowExecutionInput {
  workflowId: string;
  executionId?: string;
  inputData: Record<string, any>;
  executionOptions: {
    timeout?: number;
    maxRetries?: number;
    parallelExecution?: boolean;
  };
}
```

**Outputs:**
```typescript
interface WorkflowExecutionOutput {
  executionId: string;
  status: 'success' | 'error' | 'running' | 'cancelled';
  results: Record<string, any>;
  executionTime: number;
  error?: {
    message: string;
    nodeId?: string;
    stackTrace?: string;
  };
}
```

**Trigger Mechanisms:**
- API call from UI (`POST /api/workflows/{id}/execute`)
- Scheduled execution via cron expressions
- Webhook trigger from external services
- Manual trigger from workflow builder interface

**Internal Logic:**
```python
class WorkflowExecutionAgent:
    def __init__(self, n8n_client, state_manager, event_bus):
        self.n8n_client = n8n_client
        self.state_manager = state_manager
        self.event_bus = event_bus

    async def execute_workflow(self, input_data: WorkflowExecutionInput) -> WorkflowExecutionOutput:
        # 1. Initialize execution context
        execution_context = await self.initialize_context(input_data)

        # 2. Validate workflow structure
        validation_result = await self.validate_workflow(input_data.workflowId)
        if not validation_result.valid:
            return self.create_error_output(validation_result.errors)

        # 3. Execute workflow nodes in topological order
        execution_result = await self.execute_nodes(execution_context)

        # 4. Handle errors and retries
        if execution_result.has_errors and input_data.executionOptions.maxRetries > 0:
            return await self.retry_execution(input_data, execution_context)

        # 5. Finalize and return results
        return await self.finalize_execution(execution_result)
```

---

### NodeValidationAgent
**Role:** Validates node configurations, connections, and data flow compatibility

**Capabilities:**
- Schema validation for node parameters
- Connection compatibility checking
- Data type validation and conversion
- Circular dependency detection
- Performance impact analysis

**Dependencies:**
- JSON Schema validator
- n8n node specification registry
- Type inference engine

**Inputs:**
```typescript
interface NodeValidationInput {
  nodeType: string;
  parameters: Record<string, any>;
  connections: {
    inputs?: Array<{nodeId: string, outputIndex: number}>;
    outputs?: Array<{nodeId: string, inputIndex: number}>;
  };
  context: {
    workflowId: string;
    availableNodes: string[];
  };
}
```

**Outputs:**
```typescript
interface NodeValidationOutput {
  isValid: boolean;
  errors: Array<{
    field: string;
    message: string;
    severity: 'error' | 'warning' | 'info';
  }>;
  warnings: Array<{
    message: string;
    suggestion?: string;
  }>;
  suggestions: Array<{
    type: string;
    description: string;
  }>;
}
```

**Trigger Mechanisms:**
- Real-time validation on node configuration changes
- Pre-execution validation before workflow run
- Batch validation for workflow import/export
- Scheduled validation for workflow maintenance

**Internal Logic:**
```python
class NodeValidationAgent:
    def __init__(self, schema_registry, type_checker):
        self.schema_registry = schema_registry
        self.type_checker = type_checker

    async def validate_node(self, input_data: NodeValidationInput) -> NodeValidationOutput:
        # 1. Parameter schema validation
        schema_errors = self.validate_parameters(input_data.nodeType, input_data.parameters)

        # 2. Connection compatibility check
        connection_errors = self.validate_connections(input_data.connections)

        # 3. Data flow analysis
        flow_warnings = self.analyze_data_flow(input_data)

        # 4. Performance impact assessment
        performance_suggestions = self.assess_performance_impact(input_data)

        # 5. Generate comprehensive validation report
        return self.compile_validation_report(schema_errors, connection_errors,
                                            flow_warnings, performance_suggestions)
```

---

### CanvasManagerAgent
**Role:** Manages visual canvas state, node positioning, and UI interactions

**Capabilities:**
- Canvas state persistence and restoration
- Node positioning and layout optimization
- Zoom and pan management
- Selection and multi-selection handling
- Undo/redo functionality
- Real-time collaboration support

**Dependencies:**
- ReactFlow canvas engine
- WebSocket service for collaboration
- Local storage for state persistence

**Inputs:**
```typescript
interface CanvasManagementInput {
  action: 'move' | 'select' | 'delete' | 'copy' | 'paste' | 'zoom' | 'pan';
  targetNodes?: string[];
  position?: {x: number, y: number};
  zoomLevel?: number;
  panOffset?: {x: number, y: number};
  canvasState?: {
    nodes: Array<{id: string, position: {x: number, y: number}}>;
    edges: Array<{id: string, source: string, target: string}>;
  };
}
```

**Outputs:**
```typescript
interface CanvasManagementOutput {
  success: boolean;
  newState: {
    nodes: Array<{id: string, position: {x: number, y: number}}>;
    edges: Array<{id: string, source: string, target: string}>;
  };
  affectedNodes: string[];
  eventType: string;
  timestamp: number;
}
```

**Trigger Mechanisms:**
- User interactions (mouse, keyboard, touch)
- WebSocket events for collaborative editing
- API calls for programmatic canvas manipulation
- Timer-based auto-save functionality

**Internal Logic:**
```python
class CanvasManagerAgent:
    def __init__(self, canvas_engine, storage_service, collaboration_service):
        self.canvas_engine = canvas_engine
        self.storage_service = storage_service
        self.collaboration_service = collaboration_service

    async def handle_canvas_action(self, input_data: CanvasManagementInput) -> CanvasManagementOutput:
        # 1. Validate action permissions
        if not self.validate_action_permissions(input_data.action):
            return self.create_error_output("Insufficient permissions")

        # 2. Execute canvas action
        new_state = await self.execute_action(input_data)

        # 3. Update internal state
        self.update_internal_state(new_state)

        # 4. Broadcast changes to collaborators
        await self.broadcast_to_collaborators(new_state)

        # 5. Persist state changes
        await self.persist_state(new_state)

        return self.create_success_output(new_state)
```

---

### IntegrationAgent
**Role:** Manages external service integrations, API authentication, and data transformation

**Capabilities:**
- OAuth and API key management
- Service health monitoring
- Data format transformation
- Rate limiting and quota management
- Credential encryption and storage

**Dependencies:**
- OAuth2 client libraries
- HTTP client with retry logic
- Encryption service for credentials
- Service registry and discovery

**Inputs:**
```typescript
interface IntegrationInput {
  serviceName: string;
  operation: 'authenticate' | 'test' | 'execute' | 'refresh';
  credentials: {
    apiKey?: string;
    oauthToken?: string;
    username?: string;
    password?: string;
  };
  parameters: Record<string, any>;
  data?: any;
}
```

**Outputs:**
```typescript
interface IntegrationOutput {
  success: boolean;
  data?: any;
  error?: {
    code: string;
    message: string;
    details?: Record<string, any>;
  };
  metadata: {
    serviceName: string;
    operation: string;
    executionTime: number;
    rateLimitRemaining?: number;
  };
}
```

**Trigger Mechanisms:**
- Node execution in workflow
- Scheduled credential refresh
- Service health check intervals
- Manual testing from UI

**Internal Logic:**
```python
class IntegrationAgent:
    def __init__(self, credential_manager, service_registry, http_client):
        self.credential_manager = credential_manager
        self.service_registry = service_registry
        self.http_client = http_client

    async def handle_integration(self, input_data: IntegrationInput) -> IntegrationOutput:
        # 1. Retrieve and validate credentials
        credentials = await self.credential_manager.get_credentials(input_data.serviceName)

        # 2. Check service availability
        service_status = await self.service_registry.check_service_health(input_data.serviceName)
        if not service_status.available:
            return self.create_service_unavailable_output(service_status)

        # 3. Execute integration with rate limiting
        result = await self.execute_with_rate_limit(input_data, credentials)

        # 4. Transform response data if needed
        transformed_data = self.transform_response_data(result, input_data.serviceName)

        # 5. Update usage metrics and quotas
        await self.update_usage_metrics(input_data.serviceName, result)

        return self.create_success_output(transformed_data, result.metadata)
```

---

### ExportImportAgent
**Role:** Handles workflow serialization, import/export, and template management

**Capabilities:**
- JSON-based workflow serialization
- Import validation and conflict resolution
- Template creation and management
- Version control integration
- Format conversion (JSON, YAML, XML)

**Dependencies:**
- JSON Schema validator
- File system abstraction layer
- Version control system integration
- Template storage service

**Inputs:**
```typescript
interface ExportImportInput {
  action: 'export' | 'import' | 'create_template' | 'validate';
  workflowId?: string;
  workflowData?: any;
  format: 'json' | 'yaml' | 'xml';
  options: {
    includeCredentials?: boolean;
    includeExecutionHistory?: boolean;
    version?: string;
  };
}
```

**Outputs:**
```typescript
interface ExportImportOutput {
  success: boolean;
  data?: any;
  filePath?: string;
  errors?: Array<{
    line?: number;
    column?: number;
    message: string;
  }>;
  metadata: {
    format: string;
    version: string;
    timestamp: number;
    size: number;
  };
}
```

**Trigger Mechanisms:**
- User-initiated export/import actions
- Scheduled backup operations
- Template marketplace synchronization
- Version control webhooks

**Internal Logic:**
```python
class ExportImportAgent:
    def __init__(self, workflow_repository, template_service, validation_service):
        self.workflow_repository = workflow_repository
        self.template_service = template_service
        self.validation_service = validation_service

    async def handle_export_import(self, input_data: ExportImportInput) -> ExportImportOutput:
        # 1. Validate input parameters
        validation_result = self.validate_input_parameters(input_data)
        if not validation_result.valid:
            return self.create_validation_error_output(validation_result.errors)

        # 2. Execute requested action
        if input_data.action == 'export':
            result = await self.export_workflow(input_data)
        elif input_data.action == 'import':
            result = await self.import_workflow(input_data)
        elif input_data.action == 'create_template':
            result = await self.create_template(input_data)

        # 3. Validate output data
        output_validation = self.validate_output_data(result.data, input_data.format)
        if not output_validation.valid:
            return self.create_output_validation_error(output_validation.errors)

        # 4. Generate file or return data
        if input_data.options.generateFile:
            file_result = await self.generate_file(result.data, input_data.format)
            return self.create_file_output(file_result)
        else:
            return self.create_data_output(result.data, result.metadata)
```

## Configuration

### Environment Variables
- `N8N_API_URL`: n8n server API endpoint
- `REDIS_URL`: Redis connection string for state management
- `WEBSOCKET_URL`: WebSocket server URL for real-time collaboration
- `AGENT_EXECUTION_TIMEOUT`: Default timeout for agent operations (default: 30s)
- `AGENT_MAX_RETRIES`: Maximum retry attempts for failed operations (default: 3)
- `CANVAS_AUTO_SAVE_INTERVAL`: Auto-save interval in seconds (default: 30)
- `INTEGRATION_RATE_LIMIT`: Rate limit for external API calls (default: 100/minute)

### Configuration Files
- `agents/config.yaml`: Main agent configuration and service endpoints
- `agents/credentials.json`: Encrypted service credentials and API keys
- `agents/validation-rules.json`: Node validation schemas and rules
- `agents/integration-specs.json`: External service integration specifications

### Agent-Specific Configuration

#### WorkflowExecutionAgent
```yaml
workflow_execution:
  max_concurrent_executions: 10
  default_timeout: 300
  retry_strategy: exponential_backoff
  state_persistence: redis
  monitoring_enabled: true
```

#### NodeValidationAgent
```yaml
node_validation:
  strict_mode: false
  allow_unknown_nodes: true
  performance_warnings: true
  schema_cache_ttl: 3600
```

#### CanvasManagerAgent
```yaml
canvas_management:
  auto_save_enabled: true
  auto_save_interval: 30
  max_undo_steps: 50
  collaboration_enabled: true
  layout_algorithm: force_directed
```

## Communication

### Inter-Agent Communication
Agents communicate through a centralized event-driven architecture:

- **Event Bus**: Asynchronous message passing via Redis pub/sub
- **State Manager**: Shared state management through Zustand stores
- **Direct API Calls**: Synchronous request-response for critical operations
- **WebSocket Broadcasting**: Real-time updates for collaborative features

### Agent Communication Patterns

#### Request-Response Pattern
```python
# WorkflowExecutionAgent requests validation from NodeValidationAgent
async def execute_workflow_with_validation(self, workflow_data):
    # 1. Send validation request
    validation_result = await self.event_bus.request(
        'node_validation',
        {'workflow': workflow_data}
    )

    # 2. Process validation results
    if not validation_result.valid:
        return {'error': validation_result.errors}

    # 3. Execute workflow
    return await self.execute_workflow(workflow_data)
```

#### Publish-Subscribe Pattern
```python
# CanvasManagerAgent broadcasts state changes
async def handle_node_move(self, node_id, new_position):
    # 1. Update local state
    self.update_node_position(node_id, new_position)

    # 2. Broadcast to all collaborators
    await self.event_bus.publish('canvas:node_moved', {
        'nodeId': node_id,
        'position': new_position,
        'timestamp': time.time()
    })

    # 3. Persist changes
    await self.persist_state()
```

### External API Integration

#### n8n API Communication
- **Base URL**: Configurable n8n server endpoint
- **Authentication**: API key or OAuth2
- **Rate Limiting**: Built-in rate limiting with exponential backoff
- **Health Monitoring**: Continuous service availability checks

#### Third-Party Service Integration
- **Credential Management**: Encrypted storage and rotation
- **OAuth Flows**: Support for OAuth2 authorization code flow
- **Webhook Handling**: Incoming webhook processing and validation
- **Data Transformation**: Automatic format conversion between services

### Communication Protocols

#### Message Format
```typescript
interface AgentMessage {
  id: string;
  source: string;
  target: string;
  type: 'request' | 'response' | 'event' | 'broadcast';
  action: string;
  payload: any;
  timestamp: number;
  correlationId?: string;
  metadata: {
    priority: 'low' | 'normal' | 'high' | 'critical';
    ttl?: number;
    retries?: number;
  };
}
```

#### Authentication & Security
- **API Keys**: Service-to-service authentication
- **JWT Tokens**: User session management
- **Message Encryption**: End-to-end encryption for sensitive data
- **Access Control**: Role-based permissions for agent operations

#### Error Handling
```python
class AgentError(Exception):
    def __init__(self, code: str, message: str, agent: str, details: dict = None):
        self.code = code
        self.message = message
        self.agent = agent
        self.details = details or {}
        super().__init__(self.message)

# Example usage in error handling
async def handle_agent_error(self, error: AgentError):
    # 1. Log structured error
    await self.log_error(error)

    # 2. Determine retry strategy
    retry_strategy = self.get_retry_strategy(error)

    # 3. Execute fallback if needed
    if retry_strategy.max_retries > 0:
        return await self.retry_operation(error, retry_strategy)

    # 4. Propagate to error handler
    return await self.propagate_error(error)
```

### Performance & Monitoring

#### Metrics Collection
- **Response Times**: Agent operation execution times
- **Error Rates**: Success/failure rates per agent
- **Resource Usage**: Memory and CPU utilization
- **Throughput**: Operations per second per agent

#### Health Checks
```python
async def health_check(self) -> AgentHealth:
    checks = await asyncio.gather(
        self.check_dependencies(),
        self.check_resource_usage(),
        self.check_recent_errors()
    )

    return AgentHealth(
        status='healthy' if all(c.ok for c in checks) else 'degraded',
        response_time=self.measure_response_time(),
        last_error=self.get_last_error(),
        metrics=self.collect_metrics()
    )
```

### Agent Lifecycle Management

#### Initialization Sequence
1. **Dependency Injection**: Initialize all required services
2. **Configuration Loading**: Load agent-specific configuration
3. **Health Check**: Verify all dependencies are available
4. **Event Registration**: Register for relevant events
5. **Ready State**: Signal readiness to accept requests

#### Shutdown Sequence
1. **Graceful Completion**: Complete in-flight operations
2. **State Persistence**: Save current state to storage
3. **Event Cleanup**: Unregister event handlers
4. **Resource Cleanup**: Close connections and release resources

This comprehensive agent system provides a robust, scalable foundation for the n8n visual workflow builder, enabling complex workflow orchestration with real-time collaboration and extensive external integrations.
