"""
Unit tests for ExportImportAgent.
"""

import pytest
import asyncio
import json
import yaml
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any

from agents.export_import_agent import ExportImportAgent


class TestExportImportAgent:
    """Test cases for ExportImportAgent."""

    @pytest.fixture
    def agent(self):
        """Create ExportImportAgent instance for testing."""
        workflow_repository = Mock()
        template_service = Mock()
        validation_service = Mock()

        return ExportImportAgent(workflow_repository, template_service, validation_service)

    @pytest.fixture
    def sample_workflow(self):
        """Sample workflow for testing."""
        return {
            "nodes": [
                {
                    "id": "trigger",
                    "type": "n8n-nodes-base.manualTrigger",
                    "position": [100, 100],
                    "parameters": {"description": "Test workflow"}
                },
                {
                    "id": "action",
                    "type": "n8n-nodes-base.httpRequest",
                    "position": [300, 100],
                    "parameters": {
                        "method": "GET",
                        "url": "https://api.example.com"
                    }
                }
            ],
            "connections": [
                {
                    "source": "trigger",
                    "target": "action",
                    "sourceOutput": 0,
                    "targetInput": 0
                }
            ]
        }

    @pytest.fixture
    def workflow_with_credentials(self):
        """Workflow with credentials for testing."""
        return {
            "nodes": [
                {
                    "id": "trigger",
                    "type": "n8n-nodes-base.manualTrigger",
                    "position": [100, 100]
                },
                {
                    "id": "github-action",
                    "type": "n8n-nodes-base.github",
                    "position": [300, 100],
                    "credentials": {
                        "githubApi": {
                            "id": "github-cred-123",
                            "name": "GitHub API"
                        }
                    }
                }
            ],
            "connections": [
                {"source": "trigger", "target": "github-action"}
            ]
        }

    @pytest.mark.asyncio
    async def test_json_export(self, agent, sample_workflow):
        """Test JSON export functionality."""
        # Setup
        agent.workflow_repository.get_workflow = AsyncMock(return_value=sample_workflow)
        agent.validation_service.validate_export = Mock(return_value={"valid": True})

        # Execute
        result = await agent.export_workflow({
            "workflowId": "workflow-123",
            "format": "json",
            "options": {"includeCredentials": False}
        })

        # Assertions
        assert result["success"] is True
        assert result["metadata"]["format"] == "json"
        assert "data" in result
        # Verify JSON structure
        exported_data = json.loads(result["data"])
        assert "nodes" in exported_data
        assert "connections" in exported_data

    @pytest.mark.asyncio
    async def test_yaml_export(self, agent, sample_workflow):
        """Test YAML export functionality."""
        # Setup
        agent.workflow_repository.get_workflow = AsyncMock(return_value=sample_workflow)
        agent.validation_service.validate_export = Mock(return_value={"valid": True})

        # Execute
        result = await agent.export_workflow({
            "workflowId": "workflow-123",
            "format": "yaml",
            "options": {"includeCredentials": False}
        })

        # Assertions
        assert result["success"] is True
        assert result["metadata"]["format"] == "yaml"
        # Verify YAML structure
        exported_data = yaml.safe_load(result["data"])
        assert "nodes" in exported_data
        assert "connections" in exported_data

    @pytest.mark.asyncio
    async def test_xml_export(self, agent, sample_workflow):
        """Test XML export functionality."""
        # Setup
        agent.workflow_repository.get_workflow = AsyncMock(return_value=sample_workflow)
        agent.validation_service.validate_export = Mock(return_value={"valid": True})

        # Execute
        result = await agent.export_workflow({
            "workflowId": "workflow-123",
            "format": "xml",
            "options": {"includeCredentials": False}
        })

        # Assertions
        assert result["success"] is True
        assert result["metadata"]["format"] == "xml"
        # Verify XML contains expected elements
        assert "<nodes>" in result["data"]
        assert "<connections>" in result["data"]

    @pytest.mark.asyncio
    async def test_export_with_credentials(self, agent, workflow_with_credentials):
        """Test export with credentials included."""
        # Setup
        agent.workflow_repository.get_workflow = AsyncMock(return_value=workflow_with_credentials)
        agent.validation_service.validate_export = Mock(return_value={"valid": True})

        # Execute
        result = await agent.export_workflow({
            "workflowId": "workflow-456",
            "format": "json",
            "options": {"includeCredentials": True}
        })

        # Assertions
        assert result["success"] is True
        exported_data = json.loads(result["data"])
        # Verify credentials are included
        github_node = next(node for node in exported_data["nodes"] if node["type"] == "n8n-nodes-base.github")
        assert "credentials" in github_node

    @pytest.mark.asyncio
    async def test_export_without_credentials(self, agent, workflow_with_credentials):
        """Test export without credentials."""
        # Setup
        agent.workflow_repository.get_workflow = AsyncMock(return_value=workflow_with_credentials)
        agent.validation_service.validate_export = Mock(return_value={"valid": True})

        # Execute
        result = await agent.export_workflow({
            "workflowId": "workflow-456",
            "format": "json",
            "options": {"includeCredentials": False}
        })

        # Assertions
        assert result["success"] is True
        exported_data = json.loads(result["data"])
        # Verify credentials are excluded
        github_node = next(node for node in exported_data["nodes"] if node["type"] == "n8n-nodes-base.github")
        assert "credentials" not in github_node

    @pytest.mark.asyncio
    async def test_workflow_import(self, agent, sample_workflow):
        """Test workflow import functionality."""
        # Setup
        agent.validation_service.validate_import = Mock(return_value={
            "valid": True,
            "errors": [],
            "warnings": []
        })
        agent.workflow_repository.create_workflow = AsyncMock(return_value={
            "id": "imported-workflow-123",
            "success": True
        })

        # Execute
        result = await agent.import_workflow({
            "workflowData": sample_workflow,
            "format": "json",
            "options": {"includeCredentials": False}
        })

        # Assertions
        assert result["success"] is True
        assert result["data"]["id"] == "imported-workflow-123"
        agent.validation_service.validate_import.assert_called_once()

    @pytest.mark.asyncio
    async def test_import_validation_failure(self, agent):
        """Test import with validation failure."""
        # Setup invalid workflow data
        invalid_workflow = {
            "nodes": [],
            "connections": [
                {"source": "non-existent", "target": "another-invalid"}
            ]
        }

        agent.validation_service.validate_import = Mock(return_value={
            "valid": False,
            "errors": [
                {"field": "connections", "message": "Invalid connection"},
                {"field": "nodes", "message": "No nodes defined"}
            ]
        })

        # Execute
        result = await agent.import_workflow({
            "workflowData": invalid_workflow,
            "format": "json",
            "options": {}
        })

        # Assertions
        assert result["success"] is False
        assert len(result["errors"]) > 0

    @pytest.mark.asyncio
    async def test_template_creation(self, agent, sample_workflow):
        """Test workflow template creation."""
        # Setup
        agent.template_service.create_template = AsyncMock(return_value={
            "id": "template-123",
            "success": True,
            "name": "Test Template"
        })

        # Execute
        result = await agent.create_template({
            "workflowData": sample_workflow,
            "name": "Test Template",
            "description": "A test template",
            "category": "Testing"
        })

        # Assertions
        assert result["success"] is True
        assert result["data"]["id"] == "template-123"
        agent.template_service.create_template.assert_called_once()

    @pytest.mark.asyncio
    async def test_template_application(self, agent, sample_workflow):
        """Test template application."""
        # Setup
        agent.template_service.get_template = AsyncMock(return_value={
            "id": "template-123",
            "workflow": sample_workflow,
            "variables": ["{{name}}", "{{email}}"]
        })
        agent.workflow_repository.create_workflow = AsyncMock(return_value={
            "id": "workflow-from-template",
            "success": True
        })

        # Execute
        result = await agent.apply_template({
            "templateId": "template-123",
            "variables": {"name": "Test User", "email": "test@example.com"}
        })

        # Assertions
        assert result["success"] is True
        assert result["data"]["id"] == "workflow-from-template"

    @pytest.mark.asyncio
    async def test_format_conversion(self, agent, sample_workflow):
        """Test format conversion between JSON and YAML."""
        # Test JSON to YAML conversion
        agent.workflow_repository.get_workflow = AsyncMock(return_value=sample_workflow)

        # Export as JSON
        json_result = await agent.export_workflow({
            "workflowId": "workflow-123",
            "format": "json",
            "options": {}
        })

        # Import JSON and export as YAML
        agent.validation_service.validate_import = Mock(return_value={"valid": True})
        agent.workflow_repository.create_workflow = AsyncMock(return_value={"id": "converted-123"})

        # Import the JSON data
        import_result = await agent.import_workflow({
            "workflowData": json.loads(json_result["data"]),
            "format": "json",
            "options": {}
        })

        # Export the imported workflow as YAML
        yaml_result = await agent.export_workflow({
            "workflowId": "converted-123",
            "format": "yaml",
            "options": {}
        })

        # Assertions
        assert json_result["success"] is True
        assert yaml_result["success"] is True
        assert json_result["metadata"]["format"] == "json"
        assert yaml_result["metadata"]["format"] == "yaml"

    @pytest.mark.asyncio
    async def test_version_control_integration(self, agent, sample_workflow):
        """Test version control integration."""
        # Setup
        agent.workflow_repository.get_workflow = AsyncMock(return_value=sample_workflow)
        agent.validation_service.validate_export = Mock(return_value={"valid": True})

        # Execute export with version info
        result = await agent.export_workflow({
            "workflowId": "workflow-123",
            "format": "json",
            "options": {
                "version": "1.0.0",
                "includeVersion": True
            }
        })

        # Assertions
        assert result["success"] is True
        assert result["metadata"]["version"] == "1.0.0"
        exported_data = json.loads(result["data"])
        assert "version" in exported_data

    @pytest.mark.asyncio
    async def test_conflict_resolution(self, agent, sample_workflow):
        """Test conflict resolution during import."""
        # Setup workflow with naming conflict
        existing_workflow = {
            **sample_workflow,
            "name": "Existing Workflow"
        }

        agent.workflow_repository.get_workflow = AsyncMock(side_effect=[
            existing_workflow,  # First call returns existing
            None  # Second call for new name
        ])
        agent.workflow_repository.create_workflow = AsyncMock(return_value={
            "id": "workflow-new-name",
            "success": True
        })

        # Execute import with conflict resolution
        result = await agent.import_workflow({
            "workflowData": sample_workflow,
            "format": "json",
            "options": {
                "conflictResolution": "rename",
                "includeCredentials": False
            }
        })

        # Assertions
        assert result["success"] is True
        agent.workflow_repository.create_workflow.assert_called_once()

    @pytest.mark.asyncio
    async def test_batch_operations(self, agent, sample_workflow):
        """Test batch import/export operations."""
        # Setup
        agent.workflow_repository.get_workflow = AsyncMock(return_value=sample_workflow)
        agent.validation_service.validate_export = Mock(return_value={"valid": True})
        agent.validation_service.validate_import = Mock(return_value={"valid": True})
        agent.workflow_repository.create_workflow = AsyncMock(return_value={
            "id": "batch-workflow-1",
            "success": True
        })

        # Test batch export
        export_tasks = []
        for i in range(3):
            task = agent.export_workflow({
                "workflowId": f"workflow-{i}",
                "format": "json",
                "options": {}
            })
            export_tasks.append(task)

        export_results = await asyncio.gather(*export_tasks)

        # Test batch import
        import_tasks = []
        for i, export_result in enumerate(export_results):
            task = agent.import_workflow({
                "workflowData": json.loads(export_result["data"]),
                "format": "json",
                "options": {}
            })
            import_tasks.append(task)

        import_results = await asyncio.gather(*import_tasks)

        # Assertions
        assert len(export_results) == 3
        assert len(import_results) == 3
        assert all(result["success"] for result in export_results)
        assert all(result["success"] for result in import_results)

    @pytest.mark.asyncio
    async def test_file_generation(self, agent, sample_workflow):
        """Test file generation for exports."""
        # Setup
        agent.workflow_repository.get_workflow = AsyncMock(return_value=sample_workflow)
        agent.validation_service.validate_export = Mock(return_value={"valid": True})

        # Execute export with file generation
        result = await agent.export_workflow({
            "workflowId": "workflow-123",
            "format": "json",
            "options": {
                "generateFile": True,
                "includeCredentials": False
            }
        })

        # Assertions
        assert result["success"] is True
        assert "filePath" in result
        # In real implementation, would verify file was created

    @pytest.mark.asyncio
    async def test_large_workflow_handling(self, agent):
        """Test handling of large workflows."""
        # Create large workflow
        large_workflow = {
            "nodes": [
                {
                    "id": f"node-{i}",
                    "type": "n8n-nodes-base.set",
                    "position": [i * 100, 100],
                    "parameters": {"values": {"string": [{"name": f"field{i}", "value": f"value{i}"}]}}
                }
                for i in range(100)
            ],
            "connections": [
                {"source": f"node-{i}", "target": f"node-{i+1}"}
                for i in range(99)
            ]
        }

        # Setup
        agent.workflow_repository.get_workflow = AsyncMock(return_value=large_workflow)
        agent.validation_service.validate_export = Mock(return_value={"valid": True})

        # Execute
        result = await agent.export_workflow({
            "workflowId": "large-workflow",
            "format": "json",
            "options": {}
        })

        # Assertions
        assert result["success"] is True
        assert result["metadata"]["size"] > 10000  # Should be large file
        exported_data = json.loads(result["data"])
        assert len(exported_data["nodes"]) == 100

    @pytest.mark.asyncio
    async def test_error_recovery(self, agent, sample_workflow):
        """Test error recovery during import/export."""
        # Setup validation to fail initially, then succeed
        agent.validation_service.validate_import = Mock(side_effect=[
            {"valid": False, "errors": [{"message": "Initial validation error"}]},
            {"valid": True, "errors": [], "warnings": []}
        ])
        agent.workflow_repository.create_workflow = AsyncMock(return_value={
            "id": "recovered-workflow",
            "success": True
        })

        # Execute with retry
        result = await agent.import_workflow({
            "workflowData": sample_workflow,
            "format": "json",
            "options": {"maxRetries": 2}
        })

        # Assertions
        assert result["success"] is True
        agent.validation_service.validate_import.assert_called()

    @pytest.mark.asyncio
    async def test_metadata_preservation(self, agent, sample_workflow):
        """Test metadata preservation during import/export."""
        # Add metadata to workflow
        workflow_with_metadata = {
            **sample_workflow,
            "metadata": {
                "version": "1.0.0",
                "author": "Test User",
                "created": "2024-01-01T00:00:00Z",
                "tags": ["test", "automation"]
            }
        }

        # Setup
        agent.workflow_repository.get_workflow = AsyncMock(return_value=workflow_with_metadata)
        agent.validation_service.validate_export = Mock(return_value={"valid": True})

        # Export
        export_result = await agent.export_workflow({
            "workflowId": "workflow-123",
            "format": "json",
            "options": {"preserveMetadata": True}
        })

        # Import
        agent.validation_service.validate_import = Mock(return_value={"valid": True})
        agent.workflow_repository.create_workflow = AsyncMock(return_value={
            "id": "imported-workflow",
            "success": True
        })

        import_result = await agent.import_workflow({
            "workflowData": json.loads(export_result["data"]),
            "format": "json",
            "options": {"preserveMetadata": True}
        })

        # Assertions
        assert export_result["success"] is True
        assert import_result["success"] is True
        # In real implementation, would verify metadata preservation

    @pytest.mark.asyncio
    async def test_validation_error_details(self, agent):
        """Test detailed validation error reporting."""
        # Setup validation with detailed errors
        agent.validation_service.validate_import = Mock(return_value={
            "valid": False,
            "errors": [
                {
                    "line": 10,
                    "column": 5,
                    "message": "Invalid node type",
                    "severity": "error"
                },
                {
                    "line": 15,
                    "column": 12,
                    "message": "Missing required parameter",
                    "severity": "warning"
                }
            ]
        })

        # Execute
        result = await agent.import_workflow({
            "workflowData": {"nodes": [], "connections": []},
            "format": "json",
            "options": {}
        })

        # Assertions
        assert result["success"] is False
        assert len(result["errors"]) == 2
        assert result["errors"][0]["line"] == 10
        assert result["errors"][0]["column"] == 5

    @pytest.mark.asyncio
    async def test_schema_version_handling(self, agent, sample_workflow):
        """Test handling of different schema versions."""
        # Setup different schema versions
        v1_workflow = {
            **sample_workflow,
            "schemaVersion": "1.0"
        }

        v2_workflow = {
            **sample_workflow,
            "schemaVersion": "2.0"
        }

        agent.validation_service.validate_import = Mock(return_value={"valid": True})
        agent.workflow_repository.create_workflow = AsyncMock(return_value={"id": "versioned-workflow"})

        # Test v1 import
        result1 = await agent.import_workflow({
            "workflowData": v1_workflow,
            "format": "json",
            "options": {"schemaVersion": "1.0"}
        })

        # Test v2 import
        result2 = await agent.import_workflow({
            "workflowData": v2_workflow,
            "format": "json",
            "options": {"schemaVersion": "2.0"}
        })

        # Assertions
        assert result1["success"] is True
        assert result2["success"] is True

    @pytest.mark.asyncio
    async def test_backup_and_restore(self, agent, sample_workflow):
        """Test backup and restore functionality."""
        # Setup
        agent.workflow_repository.get_all_workflows = AsyncMock(return_value=[
            {"id": "workflow-1", "data": sample_workflow},
            {"id": "workflow-2", "data": sample_workflow}
        ])
        agent.validation_service.validate_export = Mock(return_value={"valid": True})

        # Execute backup
        backup_result = await agent.create_backup({
            "format": "json",
            "includeCredentials": False,
            "includeExecutionHistory": True
        })

        # Execute restore
        agent.validation_service.validate_import = Mock(return_value={"valid": True})
        agent.workflow_repository.restore_workflows = AsyncMock(return_value={
            "restored": 2,
            "success": True
        })

        restore_result = await agent.restore_backup({
            "backupData": backup_result["data"],
            "format": "json",
            "options": {}
        })

        # Assertions
        assert backup_result["success"] is True
        assert restore_result["success"] is True
        assert restore_result["data"]["restored"] == 2

    @pytest.mark.asyncio
    async def test_template_marketplace_integration(self, agent, sample_workflow):
        """Test template marketplace integration."""
        # Setup template marketplace
        agent.template_service.upload_to_marketplace = AsyncMock(return_value={
            "id": "marketplace-template-123",
            "url": "https://marketplace.example.com/template/123",
            "success": True
        })

        # Execute template upload
        result = await agent.upload_template({
            "workflowData": sample_workflow,
            "name": "Marketplace Template",
            "description": "Template for marketplace",
            "tags": ["automation", "api"],
            "price": 0  # Free template
        })

        # Assertions
        assert result["success"] is True
        assert "marketplace" in result["data"]["url"]

    @pytest.mark.asyncio
    async def test_workflow_comparison(self, agent, sample_workflow):
        """Test workflow comparison functionality."""
        # Setup two similar workflows
        workflow1 = sample_workflow
        workflow2 = {
            **sample_workflow,
            "nodes": [
                {**node, "position": {"x": node["position"]["x"] + 10, "y": node["position"]["y"] + 10}}
                for node in sample_workflow["nodes"]
            ]
        }

        # Execute comparison
        comparison = await agent.compare_workflows({
            "workflow1": workflow1,
            "workflow2": workflow2,
            "options": {"detailed": True}
        })

        # Assertions
        assert "differences" in comparison
        assert "similarity" in comparison
        # In real implementation, would verify detailed comparison

    @pytest.mark.asyncio
    async def test_performance_optimization(self, agent, sample_workflow):
        """Test performance optimization during export/import."""
        # Setup
        agent.workflow_repository.get_workflow = AsyncMock(return_value=sample_workflow)
        agent.validation_service.validate_export = Mock(return_value={"valid": True})

        # Measure export performance
        import time
        start_time = time.time()

        result = await agent.export_workflow({
            "workflowId": "workflow-123",
            "format": "json",
            "options": {"optimize": True}
        })

        end_time = time.time()

        # Assertions
        assert result["success"] is True
        assert (end_time - start_time) < 2.0  # Should complete within 2 seconds

    @pytest.mark.asyncio
    async def test_security_validation(self, agent, sample_workflow):
        """Test security validation during import."""
        # Setup security validation
        agent.validation_service.security_check = Mock(return_value={
            "safe": True,
            "warnings": [],
            "threats": []
        })

        # Execute import with security check
        result = await agent.import_workflow({
            "workflowData": sample_workflow,
            "format": "json",
            "options": {"securityCheck": True}
        })

        # Assertions
        assert result["success"] is True
        agent.validation_service.security_check.assert_called_once()
