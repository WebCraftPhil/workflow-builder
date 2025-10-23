"""
Mock implementation of n8n API for testing purposes.
"""

import asyncio
from typing import Dict, Any, List, Optional
from unittest.mock import Mock


class N8nApiMock:
    """Mock n8n API client for testing."""

    def __init__(self):
        self.workflows: Dict[str, Any] = {}
        self.executions: Dict[str, Any] = {}
        self.credentials: Dict[str, Any] = {}
        self.webhooks: List[Dict[str, Any]] = []
        self.request_history: List[Dict[str, Any]] = []

    def _record_request(self, method: str, endpoint: str, data: Any = None):
        """Record API request for testing."""
        self.request_history.append({
            "method": method,
            "endpoint": endpoint,
            "data": data,
            "timestamp": asyncio.get_event_loop().time()
        })

    async def create_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock workflow creation."""
        self._record_request("POST", "/workflows", workflow_data)

        workflow_id = f"workflow-{len(self.workflows) + 1}"
        self.workflows[workflow_id] = {
            **workflow_data,
            "id": workflow_id,
            "createdAt": "2024-01-01T00:00:00Z",
            "updatedAt": "2024-01-01T00:00:00Z"
        }

        return {
            "id": workflow_id,
            "success": True,
            "message": "Workflow created successfully"
        }

    async def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Mock workflow retrieval."""
        self._record_request("GET", f"/workflows/{workflow_id}")
        return self.workflows.get(workflow_id)

    async def update_workflow(self, workflow_id: str, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock workflow update."""
        self._record_request("PUT", f"/workflows/{workflow_id}", workflow_data)

        if workflow_id not in self.workflows:
            raise Exception(f"Workflow {workflow_id} not found")

        self.workflows[workflow_id] = {
            **self.workflows[workflow_id],
            **workflow_data,
            "updatedAt": "2024-01-01T00:00:00Z"
        }

        return {
            "id": workflow_id,
            "success": True,
            "message": "Workflow updated successfully"
        }

    async def delete_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Mock workflow deletion."""
        self._record_request("DELETE", f"/workflows/{workflow_id}")

        if workflow_id in self.workflows:
            del self.workflows[workflow_id]
            return {"success": True, "message": "Workflow deleted successfully"}
        else:
            raise Exception(f"Workflow {workflow_id} not found")

    async def execute_workflow(self, workflow_id: str, input_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Mock workflow execution."""
        self._record_request("POST", f"/workflows/{workflow_id}/execute", input_data)

        if workflow_id not in self.workflows:
            raise Exception(f"Workflow {workflow_id} not found")

        execution_id = f"exec-{len(self.executions) + 1}"
        self.executions[execution_id] = {
            "id": execution_id,
            "workflowId": workflow_id,
            "status": "running",
            "inputData": input_data or {},
            "startedAt": "2024-01-01T00:00:00Z"
        }

        # Simulate execution completion
        await asyncio.sleep(0.1)

        self.executions[execution_id].update({
            "status": "success",
            "finishedAt": "2024-01-01T00:00:01Z",
            "results": {"output": "mocked execution result"}
        })

        return {
            "executionId": execution_id,
            "status": "success",
            "results": {"output": "mocked execution result"},
            "executionTime": 1.0
        }

    async def get_execution(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Mock execution retrieval."""
        self._record_request("GET", f"/executions/{execution_id}")
        return self.executions.get(execution_id)

    async def stop_execution(self, execution_id: str) -> Dict[str, Any]:
        """Mock execution stopping."""
        self._record_request("POST", f"/executions/{execution_id}/stop")

        if execution_id in self.executions:
            self.executions[execution_id]["status"] = "cancelled"
            return {"success": True, "message": "Execution stopped"}

        raise Exception(f"Execution {execution_id} not found")

    async def create_credential(self, credential_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock credential creation."""
        self._record_request("POST", "/credentials", credential_data)

        credential_id = f"credential-{len(self.credentials) + 1}"
        self.credentials[credential_id] = {
            **credential_data,
            "id": credential_id,
            "createdAt": "2024-01-01T00:00:00Z"
        }

        return {
            "id": credential_id,
            "success": True,
            "message": "Credential created successfully"
        }

    async def test_credential(self, credential_id: str) -> Dict[str, Any]:
        """Mock credential testing."""
        self._record_request("POST", f"/credentials/{credential_id}/test")

        if credential_id in self.credentials:
            return {
                "success": True,
                "message": "Credential test successful",
                "connectionStatus": "connected"
            }
        else:
            return {
                "success": False,
                "message": "Credential not found",
                "connectionStatus": "failed"
            }

    async def register_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock webhook registration."""
        self._record_request("POST", "/webhooks", webhook_data)

        webhook_id = f"webhook-{len(self.webhooks) + 1}"
        webhook_info = {
            "id": webhook_id,
            "url": f"https://test.example.com/webhook/{webhook_id}",
            **webhook_data
        }
        self.webhooks.append(webhook_info)

        return webhook_info

    async def get_workflow_list(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Mock workflow listing."""
        self._record_request("GET", "/workflows", filters)
        return list(self.workflows.values())

    async def get_health_status(self) -> Dict[str, Any]:
        """Mock health check."""
        self._record_request("GET", "/health")
        return {
            "status": "healthy",
            "version": "1.0.0",
            "uptime": 3600,
            "database": "connected",
            "redis": "connected"
        }

    def clear_history(self):
        """Clear request history for clean test state."""
        self.request_history.clear()

    def get_request_count(self, method: str = None, endpoint: str = None) -> int:
        """Get count of requests matching criteria."""
        count = 0
        for request in self.request_history:
            if method and request["method"] != method:
                continue
            if endpoint and request["endpoint"] != endpoint:
                continue
            count += 1
        return count

    def get_last_request(self, method: str = None, endpoint: str = None) -> Optional[Dict[str, Any]]:
        """Get the last request matching criteria."""
        for request in reversed(self.request_history):
            if method and request["method"] != method:
                continue
            if endpoint and request["endpoint"] != endpoint:
                continue
            return request
        return None
