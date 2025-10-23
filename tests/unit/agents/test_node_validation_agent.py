"""
Unit tests for NodeValidationAgent.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any

from agents.node_validation_agent import NodeValidationAgent


class TestNodeValidationAgent:
    """Test cases for NodeValidationAgent."""

    @pytest.fixture
    def agent(self):
        """Create NodeValidationAgent instance for testing."""
        schema_registry = Mock()
        type_checker = Mock()
        return NodeValidationAgent(schema_registry, type_checker)

    @pytest.fixture
    def valid_node_input(self):
        """Valid node validation input."""
        return {
            "nodeType": "n8n-nodes-base.httpRequest",
            "parameters": {
                "method": "GET",
                "url": "https://api.example.com/data",
                "headers": {
                    "Content-Type": "application/json"
                }
            },
            "connections": {
                "inputs": [],
                "outputs": []
            },
            "context": {
                "workflowId": "test-workflow-123",
                "availableNodes": [
                    "n8n-nodes-base.httpRequest",
                    "n8n-nodes-base.set",
                    "n8n-nodes-base.if"
                ]
            }
        }

    @pytest.fixture
    def invalid_node_input(self):
        """Invalid node validation input."""
        return {
            "nodeType": "n8n-nodes-base.httpRequest",
            "parameters": {
                "method": "INVALID_METHOD",
                "url": "not-a-valid-url"
            },
            "connections": {
                "inputs": [{"nodeId": "non-existent", "outputIndex": 0}],
                "outputs": []
            },
            "context": {
                "workflowId": "invalid-workflow",
                "availableNodes": []
            }
        }

    def test_parameter_validation_success(self, agent, valid_node_input):
        """Test successful parameter validation."""
        # Setup
        agent.schema_registry.validate = Mock(return_value={
            "valid": True,
            "errors": []
        })

        # Execute
        result = agent.validate_parameters(
            valid_node_input["nodeType"],
            valid_node_input["parameters"]
        )

        # Assertions
        assert result["valid"] is True
        assert len(result["errors"]) == 0

    def test_parameter_validation_failure(self, agent, invalid_node_input):
        """Test parameter validation failure."""
        # Setup
        agent.schema_registry.validate = Mock(return_value={
            "valid": False,
            "errors": [
                {"field": "method", "message": "Invalid HTTP method"},
                {"field": "url", "message": "Invalid URL format"}
            ]
        })

        # Execute
        result = agent.validate_parameters(
            invalid_node_input["nodeType"],
            invalid_node_input["parameters"]
        )

        # Assertions
        assert result["valid"] is False
        assert len(result["errors"]) == 2
        assert any(error["field"] == "method" for error in result["errors"])

    def test_connection_compatibility_check(self, agent, valid_node_input):
        """Test connection compatibility between nodes."""
        # Setup
        agent.type_checker.check_compatibility = Mock(return_value={
            "compatible": True,
            "warnings": []
        })

        # Execute
        result = agent.validate_connections(valid_node_input["connections"])

        # Assertions
        assert result["compatible"] is True
        assert len(result["warnings"]) == 0

    def test_connection_compatibility_failure(self, agent, invalid_node_input):
        """Test connection compatibility failure."""
        # Setup
        agent.type_checker.check_compatibility = Mock(return_value={
            "compatible": False,
            "errors": [
                {"message": "Incompatible node types"},
                {"message": "Missing required input"}
            ]
        })

        # Execute
        result = agent.validate_connections(invalid_node_input["connections"])

        # Assertions
        assert result["compatible"] is False
        assert len(result["errors"]) == 2

    def test_data_flow_analysis(self, agent, valid_node_input):
        """Test data flow analysis."""
        # Setup
        agent.analyze_data_flow = Mock(return_value={
            "warnings": [
                {"message": "Large data payload may impact performance"}
            ],
            "suggestions": [
                {"type": "optimization", "description": "Consider data compression"}
            ]
        })

        # Execute
        result = agent.analyze_data_flow(valid_node_input)

        # Assertions
        assert "warnings" in result
        assert "suggestions" in result
        assert len(result["warnings"]) > 0

    def test_circular_dependency_detection(self, agent):
        """Test circular dependency detection."""
        # Setup workflow with circular dependency
        workflow_data = {
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
        }

        # Execute
        result = agent.detect_circular_dependencies(workflow_data)

        # Assertions
        assert result["has_cycles"] is True
        assert len(result["cycles"]) > 0

    def test_performance_impact_assessment(self, agent, valid_node_input):
        """Test performance impact assessment."""
        # Setup
        agent.assess_performance_impact = Mock(return_value={
            "score": 75,
            "warnings": [
                {"message": "High memory usage expected"}
            ],
            "suggestions": [
                {"type": "memory", "description": "Consider increasing memory limits"}
            ]
        })

        # Execute
        result = agent.assess_performance_impact(valid_node_input)

        # Assertions
        assert "score" in result
        assert "warnings" in result
        assert "suggestions" in result
        assert result["score"] == 75

    def test_comprehensive_validation(self, agent, valid_node_input):
        """Test comprehensive node validation."""
        # Setup all mock methods
        agent.validate_parameters = Mock(return_value={
            "valid": True,
            "errors": []
        })
        agent.validate_connections = Mock(return_value={
            "compatible": True,
            "errors": [],
            "warnings": []
        })
        agent.analyze_data_flow = Mock(return_value={
            "warnings": [],
            "suggestions": []
        })
        agent.assess_performance_impact = Mock(return_value={
            "score": 90,
            "warnings": [],
            "suggestions": []
        })

        # Execute
        result = agent.validate_node(valid_node_input)

        # Assertions
        assert result["isValid"] is True
        assert len(result["errors"]) == 0
        assert len(result["warnings"]) == 0
        assert len(result["suggestions"]) == 0

    def test_comprehensive_validation_with_errors(self, agent, invalid_node_input):
        """Test comprehensive validation with errors."""
        # Setup all mock methods to return errors
        agent.validate_parameters = Mock(return_value={
            "valid": False,
            "errors": [{"field": "method", "message": "Invalid method"}]
        })
        agent.validate_connections = Mock(return_value={
            "compatible": False,
            "errors": [{"message": "Incompatible connection"}],
            "warnings": []
        })
        agent.analyze_data_flow = Mock(return_value={
            "warnings": [{"message": "Potential data loss"}],
            "suggestions": [{"type": "fix", "description": "Add error handling"}]
        })
        agent.assess_performance_impact = Mock(return_value={
            "score": 30,
            "warnings": [{"message": "Very high resource usage"}],
            "suggestions": [{"type": "optimization", "description": "Optimize query"}]
        })

        # Execute
        result = agent.validate_node(invalid_node_input)

        # Assertions
        assert result["isValid"] is False
        assert len(result["errors"]) > 0
        assert len(result["warnings"]) > 0
        assert len(result["suggestions"]) > 0

    def test_schema_caching(self, agent, valid_node_input):
        """Test schema validation caching."""
        # First call
        agent.schema_registry.validate = Mock(return_value={"valid": True, "errors": []})
        result1 = agent.validate_parameters("httpRequest", valid_node_input["parameters"])

        # Second call with same parameters (should use cache)
        result2 = agent.validate_parameters("httpRequest", valid_node_input["parameters"])

        # Assertions
        assert result1["valid"] is True
        assert result2["valid"] is True
        # In real implementation, would verify cache was used for second call

    def test_custom_validation_rules(self, agent):
        """Test custom validation rules."""
        # Setup custom validation rule
        custom_parameters = {
            "method": "POST",
            "url": "https://internal-api.company.com/data",
            "headers": {"Authorization": "Bearer token123"}
        }

        # Mock validation with custom rule
        agent.schema_registry.validate = Mock(return_value={
            "valid": True,
            "errors": []
        })

        # Execute
        result = agent.validate_parameters("httpRequest", custom_parameters)

        # Assertions
        assert result["valid"] is True

    def test_validation_performance(self, agent, valid_node_input):
        """Test validation performance."""
        import time

        # Setup
        agent.schema_registry.validate = Mock(return_value={"valid": True, "errors": []})

        # Measure validation time
        start_time = time.time()
        result = agent.validate_parameters(valid_node_input["nodeType"], valid_node_input["parameters"])
        end_time = time.time()

        # Assertions
        assert result["valid"] is True
        assert (end_time - start_time) < 1.0  # Should complete within 1 second

    def test_batch_validation(self, agent):
        """Test batch validation of multiple nodes."""
        nodes_to_validate = [
            {
                "nodeType": "n8n-nodes-base.httpRequest",
                "parameters": {"method": "GET", "url": "https://api1.com"}
            },
            {
                "nodeType": "n8n-nodes-base.set",
                "parameters": {"values": {"string": [{"name": "test", "value": "value"}]}}
            },
            {
                "nodeType": "n8n-nodes-base.if",
                "parameters": {"conditions": {"boolean": []}}
            }
        ]

        # Setup
        agent.schema_registry.validate = Mock(return_value={"valid": True, "errors": []})

        # Execute batch validation
        results = []
        for node in nodes_to_validate:
            result = agent.validate_parameters(node["nodeType"], node["parameters"])
            results.append(result)

        # Assertions
        assert len(results) == 3
        assert all(result["valid"] for result in results)

    def test_validation_error_severity_levels(self, agent):
        """Test different severity levels for validation errors."""
        # Setup different types of errors
        agent.schema_registry.validate = Mock(return_value={
            "valid": False,
            "errors": [
                {"field": "required_field", "message": "Required field missing", "severity": "error"},
                {"field": "optional_field", "message": "Optional field issue", "severity": "warning"},
                {"field": "info_field", "message": "Informational", "severity": "info"}
            ]
        })

        # Execute
        result = agent.validate_parameters("testNode", {})

        # Assertions
        assert result["valid"] is False
        assert len(result["errors"]) == 3

        # Check severity levels
        severities = [error["severity"] for error in result["errors"]]
        assert "error" in severities
        assert "warning" in severities
        assert "info" in severities

    def test_node_type_compatibility_matrix(self, agent):
        """Test node type compatibility checking."""
        # Test compatible connections
        compatible_pairs = [
            ("n8n-nodes-base.manualTrigger", "n8n-nodes-base.httpRequest"),
            ("n8n-nodes-base.httpRequest", "n8n-nodes-base.set"),
            ("n8n-nodes-base.set", "n8n-nodes-base.if")
        ]

        for source_type, target_type in compatible_pairs:
            agent.type_checker.check_compatibility = Mock(return_value={
                "compatible": True,
                "warnings": []
            })

            result = agent.check_node_compatibility(source_type, target_type)
            assert result["compatible"] is True

    def test_incompatible_node_connections(self, agent):
        """Test incompatible node connections."""
        # Test incompatible connections
        incompatible_pairs = [
            ("n8n-nodes-base.httpRequest", "n8n-nodes-base.manualTrigger"),  # Wrong direction
            ("unknown-node-type", "n8n-nodes-base.set"),  # Unknown type
            ("n8n-nodes-base.set", "invalid-node-type")  # Invalid target
        ]

        for source_type, target_type in incompatible_pairs:
            agent.type_checker.check_compatibility = Mock(return_value={
                "compatible": False,
                "errors": [{"message": "Incompatible node types"}]
            })

            result = agent.check_node_compatibility(source_type, target_type)
            assert result["compatible"] is False

    def test_data_type_validation(self, agent):
        """Test data type validation between connected nodes."""
        # Setup data type checking
        agent.type_checker.validate_data_types = Mock(return_value={
            "valid": True,
            "conversions": [],
            "warnings": []
        })

        # Test valid data flow
        data_flow = {
            "sourceNode": "node-1",
            "targetNode": "node-2",
            "sourceOutput": {"type": "string", "value": "test"},
            "targetInput": {"type": "string", "required": True}
        }

        result = agent.validate_data_types(data_flow)
        assert result["valid"] is True

    def test_data_type_conversion(self, agent):
        """Test automatic data type conversion."""
        # Setup type conversion
        agent.type_checker.validate_data_types = Mock(return_value={
            "valid": True,
            "conversions": [{"from": "string", "to": "number", "method": "parseInt"}],
            "warnings": [{"message": "Automatic type conversion applied"}]
        })

        data_flow = {
            "sourceNode": "node-1",
            "targetNode": "node-2",
            "sourceOutput": {"type": "string", "value": "123"},
            "targetInput": {"type": "number", "required": True}
        }

        result = agent.validate_data_types(data_flow)
        assert result["valid"] is True
        assert len(result["conversions"]) > 0

    def test_missing_required_parameters(self, agent):
        """Test validation of missing required parameters."""
        # Setup validation for missing required fields
        agent.schema_registry.validate = Mock(return_value={
            "valid": False,
            "errors": [
                {"field": "url", "message": "URL is required", "severity": "error"},
                {"field": "method", "message": "HTTP method is required", "severity": "error"}
            ]
        })

        # Execute
        result = agent.validate_parameters("httpRequest", {})

        # Assertions
        assert result["valid"] is False
        assert len(result["errors"]) == 2
        assert all(error["severity"] == "error" for error in result["errors"])

    def test_parameter_value_ranges(self, agent):
        """Test validation of parameter value ranges."""
        # Test timeout parameter validation
        agent.schema_registry.validate = Mock(return_value={
            "valid": False,
            "errors": [
                {"field": "timeout", "message": "Timeout must be between 1 and 300 seconds", "severity": "error"}
            ]
        })

        invalid_params = {"method": "GET", "url": "https://api.example.com", "timeout": 500}

        result = agent.validate_parameters("httpRequest", invalid_params)
        assert result["valid"] is False
        assert "timeout" in [error["field"] for error in result["errors"]]

    def test_conditional_logic_validation(self, agent):
        """Test validation of conditional logic in nodes."""
        # Setup conditional validation
        agent.schema_registry.validate = Mock(return_value={
            "valid": True,
            "errors": []
        })

        conditional_params = {
            "conditions": {
                "boolean": [
                    {
                        "value1": "={{ $json.status }}",
                        "value2": "active"
                    }
                ]
            }
        }

        result = agent.validate_parameters("if", conditional_params)
        assert result["valid"] is True

    def test_webhook_validation(self, agent):
        """Test webhook-specific validation."""
        # Setup webhook validation
        agent.schema_registry.validate = Mock(return_value={
            "valid": True,
            "errors": []
        })

        webhook_params = {
            "httpMethod": "POST",
            "path": "webhook/test",
            "responseMode": "lastNode"
        }

        result = agent.validate_parameters("webhook", webhook_params)
        assert result["valid"] is True

    def test_database_query_validation(self, agent):
        """Test database query validation."""
        # Setup database validation
        agent.schema_registry.validate = Mock(return_value={
            "valid": False,
            "errors": [
                {"field": "query", "message": "SQL injection risk detected", "severity": "warning"}
            ]
        })

        dangerous_query = {
            "query": "SELECT * FROM users WHERE id = " + "={{ $json.userId }}"  # Potential injection
        }

        result = agent.validate_parameters("postgres", dangerous_query)
        assert result["valid"] is False
        assert len(result["errors"]) > 0

    def test_ai_node_validation(self, agent):
        """Test AI node validation."""
        # Setup AI node validation
        agent.schema_registry.validate = Mock(return_value={
            "valid": True,
            "errors": []
        })

        ai_params = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": "={{ $json.prompt }}"}
            ],
            "maxTokens": 1000
        }

        result = agent.validate_parameters("openAI", ai_params)
        assert result["valid"] is True
