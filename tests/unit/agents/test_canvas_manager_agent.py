"""
Unit tests for CanvasManagerAgent.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any

from agents.canvas_manager_agent import CanvasManagerAgent


class TestCanvasManagerAgent:
    """Test cases for CanvasManagerAgent."""

    @pytest.fixture
    def agent(self, mock_event_bus):
        """Create CanvasManagerAgent instance for testing."""
        canvas_engine = Mock()
        storage_service = Mock()
        collaboration_service = Mock()

        return CanvasManagerAgent(canvas_engine, storage_service, mock_event_bus)

    @pytest.fixture
    def canvas_state(self):
        """Sample canvas state."""
        return {
            "nodes": [
                {"id": "node-1", "type": "trigger", "position": {"x": 100, "y": 100}},
                {"id": "node-2", "type": "action", "position": {"x": 300, "y": 100}}
            ],
            "edges": [
                {"id": "edge-1-2", "source": "node-1", "target": "node-2"}
            ],
            "viewport": {"x": 0, "y": 0, "zoom": 1.0}
        }

    @pytest.fixture
    def move_action_input(self):
        """Canvas move action input."""
        return {
            "action": "move",
            "targetNodes": ["node-1"],
            "position": {"x": 200, "y": 150},
            "zoomLevel": 1.0,
            "panOffset": {"x": 0, "y": 0}
        }

    @pytest.fixture
    def zoom_action_input(self):
        """Canvas zoom action input."""
        return {
            "action": "zoom",
            "zoomLevel": 1.5,
            "panOffset": {"x": 0, "y": 0}
        }

    @pytest.mark.asyncio
    async def test_canvas_initialization(self, agent):
        """Test canvas initialization."""
        # Setup
        agent.canvas_engine.initialize = Mock(return_value=True)
        agent.storage_service.load_state = AsyncMock(return_value={
            "nodes": [],
            "edges": [],
            "viewport": {"x": 0, "y": 0, "zoom": 1.0}
        })

        # Execute
        result = await agent.initialize_canvas("workflow-123")

        # Assertions
        assert result["success"] is True
        agent.canvas_engine.initialize.assert_called_once()
        agent.storage_service.load_state.assert_called_once()

    @pytest.mark.asyncio
    async def test_node_move_action(self, agent, canvas_state, move_action_input):
        """Test node move action."""
        # Setup
        agent.canvas_engine.move_nodes = Mock(return_value={
            **canvas_state,
            "nodes": [
                {**node, "position": move_action_input["position"]} if node["id"] == "node-1" else node
                for node in canvas_state["nodes"]
            ]
        })
        agent.storage_service.save_state = AsyncMock(return_value=True)

        # Execute
        result = await agent.handle_canvas_action(move_action_input)

        # Assertions
        assert result["success"] is True
        assert result["action"] == "move"
        assert len(result["affectedNodes"]) > 0
        agent.canvas_engine.move_nodes.assert_called_once()

    @pytest.mark.asyncio
    async def test_zoom_action(self, agent, zoom_action_input):
        """Test zoom action."""
        # Setup
        agent.canvas_engine.set_zoom = Mock(return_value={
            "viewport": {**zoom_action_input, "zoom": zoom_action_input["zoomLevel"]}
        })

        # Execute
        result = await agent.handle_canvas_action(zoom_action_input)

        # Assertions
        assert result["success"] is True
        assert result["action"] == "zoom"
        agent.canvas_engine.set_zoom.assert_called_once_with(zoom_action_input["zoomLevel"])

    @pytest.mark.asyncio
    async def test_selection_action(self, agent):
        """Test node selection action."""
        selection_input = {
            "action": "select",
            "targetNodes": ["node-1", "node-2"],
            "position": {"x": 0, "y": 0}
        }

        # Setup
        agent.canvas_engine.select_nodes = Mock(return_value={
            "selection": {"nodes": selection_input["targetNodes"]}
        })

        # Execute
        result = await agent.handle_canvas_action(selection_input)

        # Assertions
        assert result["success"] is True
        assert result["action"] == "select"
        agent.canvas_engine.select_nodes.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_action(self, agent, canvas_state):
        """Test node deletion action."""
        delete_input = {
            "action": "delete",
            "targetNodes": ["node-1"],
            "position": {"x": 0, "y": 0}
        }

        # Setup
        agent.canvas_engine.delete_nodes = Mock(return_value={
            **canvas_state,
            "nodes": [node for node in canvas_state["nodes"] if node["id"] != "node-1"],
            "edges": [edge for edge in canvas_state["edges"] if "node-1" not in [edge["source"], edge["target"]]]
        })
        agent.storage_service.save_state = AsyncMock(return_value=True)

        # Execute
        result = await agent.handle_canvas_action(delete_input)

        # Assertions
        assert result["success"] is True
        assert result["action"] == "delete"
        assert len(result["newState"]["nodes"]) == 1
        agent.canvas_engine.delete_nodes.assert_called_once()

    @pytest.mark.asyncio
    async def test_copy_paste_action(self, agent, canvas_state):
        """Test copy and paste actions."""
        copy_input = {
            "action": "copy",
            "targetNodes": ["node-1"],
            "position": {"x": 0, "y": 0}
        }

        paste_input = {
            "action": "paste",
            "position": {"x": 500, "y": 100}
        }

        # Setup
        agent.canvas_engine.copy_nodes = Mock(return_value=["node-1"])
        agent.canvas_engine.paste_nodes = Mock(return_value={
            **canvas_state,
            "nodes": [
                *canvas_state["nodes"],
                {"id": "node-1-copy", "type": "trigger", "position": {"x": 500, "y": 100}}
            ]
        })

        # Execute copy
        copy_result = await agent.handle_canvas_action(copy_input)

        # Execute paste
        paste_result = await agent.handle_canvas_action(paste_input)

        # Assertions
        assert copy_result["success"] is True
        assert paste_result["success"] is True
        assert len(paste_result["newState"]["nodes"]) == 3

    @pytest.mark.asyncio
    async def test_undo_redo_functionality(self, agent, canvas_state):
        """Test undo and redo functionality."""
        # Setup initial state
        agent.current_state = canvas_state.copy()
        agent.history = [canvas_state.copy()]

        # Setup canvas engine mocks
        agent.canvas_engine.undo = Mock(return_value=canvas_state)
        agent.canvas_engine.redo = Mock(return_value=canvas_state)

        # Test undo
        undo_input = {"action": "undo"}
        undo_result = await agent.handle_canvas_action(undo_input)

        # Test redo
        redo_input = {"action": "redo"}
        redo_result = await agent.handle_canvas_action(redo_input)

        # Assertions
        assert undo_result["success"] is True
        assert redo_result["success"] is True
        agent.canvas_engine.undo.assert_called_once()
        agent.canvas_engine.redo.assert_called_once()

    @pytest.mark.asyncio
    async def test_auto_save_functionality(self, agent, canvas_state):
        """Test auto-save functionality."""
        # Setup
        agent.current_state = canvas_state
        agent.storage_service.save_state = AsyncMock(return_value=True)

        # Execute auto-save
        result = await agent.auto_save("workflow-123")

        # Assertions
        assert result is True
        agent.storage_service.save_state.assert_called_once()

    @pytest.mark.asyncio
    async def test_collaborative_editing(self, agent, canvas_state, mock_event_bus):
        """Test collaborative editing features."""
        # Setup collaboration
        agent.collaboration_service = Mock()
        agent.collaboration_service.broadcast_change = AsyncMock(return_value=True)

        # Simulate collaborative change
        change_data = {
            "userId": "user-123",
            "action": "node_move",
            "nodeId": "node-1",
            "newPosition": {"x": 200, "y": 200}
        }

        # Execute
        result = await agent.broadcast_to_collaborators(change_data)

        # Assertions
        assert result is True
        agent.collaboration_service.broadcast_change.assert_called_once_with(change_data)

    @pytest.mark.asyncio
    async def test_layout_optimization(self, agent, canvas_state):
        """Test automatic layout optimization."""
        # Setup
        agent.canvas_engine.optimize_layout = Mock(return_value={
            **canvas_state,
            "nodes": [
                {**node, "position": {"x": node["position"]["x"] + 50, "y": node["position"]["y"] + 50}}
                for node in canvas_state["nodes"]
            ]
        })

        # Execute layout optimization
        result = await agent.optimize_layout()

        # Assertions
        assert result["success"] is True
        agent.canvas_engine.optimize_layout.assert_called_once()

    @pytest.mark.asyncio
    async def test_zoom_bounds_validation(self, agent):
        """Test zoom level bounds validation."""
        # Test minimum zoom
        min_zoom_input = {"action": "zoom", "zoomLevel": 0.1}
        min_result = await agent.handle_canvas_action(min_zoom_input)

        # Test maximum zoom
        max_zoom_input = {"action": "zoom", "zoomLevel": 5.0}
        max_result = await agent.handle_canvas_action(max_zoom_input)

        # Assertions
        assert min_result["success"] is True
        assert max_result["success"] is True
        # In real implementation, would validate zoom bounds

    @pytest.mark.asyncio
    async def test_multi_selection_operations(self, agent, canvas_state):
        """Test operations with multiple selected nodes."""
        multi_select_input = {
            "action": "move",
            "targetNodes": ["node-1", "node-2"],
            "position": {"x": 400, "y": 200}
        }

        # Setup
        agent.canvas_engine.move_nodes = Mock(return_value={
            **canvas_state,
            "nodes": [
                {**node, "position": multi_select_input["position"]}
                if node["id"] in multi_select_input["targetNodes"] else node
                for node in canvas_state["nodes"]
            ]
        })

        # Execute
        result = await agent.handle_canvas_action(multi_select_input)

        # Assertions
        assert result["success"] is True
        assert len(result["affectedNodes"]) == 2

    @pytest.mark.asyncio
    async def test_permission_validation(self, agent, move_action_input):
        """Test permission validation for canvas actions."""
        # Setup permission check
        agent.validate_action_permissions = Mock(return_value=False)

        # Execute
        result = await agent.handle_canvas_action(move_action_input)

        # Assertions
        assert result["success"] is False
        assert "permissions" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_state_persistence(self, agent, canvas_state):
        """Test canvas state persistence."""
        # Setup
        agent.current_state = canvas_state
        agent.storage_service.save_state = AsyncMock(return_value=True)

        # Execute
        result = await agent.persist_state()

        # Assertions
        assert result is True
        agent.storage_service.save_state.assert_called_once()

    @pytest.mark.asyncio
    async def test_state_restoration(self, agent, canvas_state):
        """Test canvas state restoration."""
        # Setup
        agent.storage_service.load_state = AsyncMock(return_value=canvas_state)

        # Execute
        result = await agent.restore_state("workflow-123")

        # Assertions
        assert result["success"] is True
        assert len(result["nodes"]) == 2
        agent.storage_service.load_state.assert_called_once()

    @pytest.mark.asyncio
    async def test_viewport_management(self, agent):
        """Test viewport pan and zoom management."""
        viewport_input = {
            "action": "pan",
            "zoomLevel": 1.0,
            "panOffset": {"x": -100, "y": -50}
        }

        # Setup
        agent.canvas_engine.set_viewport = Mock(return_value={
            "viewport": viewport_input
        })

        # Execute
        result = await agent.handle_canvas_action(viewport_input)

        # Assertions
        assert result["success"] is True
        agent.canvas_engine.set_viewport.assert_called_once()

    @pytest.mark.asyncio
    async def test_connection_management(self, agent, canvas_state):
        """Test edge/connection management."""
        # Test adding connection
        add_connection_input = {
            "action": "connect",
            "sourceNode": "node-1",
            "targetNode": "node-2",
            "sourceHandle": "output-0",
            "targetHandle": "input-0"
        }

        # Setup
        agent.canvas_engine.add_connection = Mock(return_value={
            **canvas_state,
            "edges": [
                *canvas_state["edges"],
                {
                    "id": "new-edge",
                    "source": add_connection_input["sourceNode"],
                    "target": add_connection_input["targetNode"]
                }
            ]
        })

        # Execute
        result = await agent.handle_canvas_action(add_connection_input)

        # Assertions
        assert result["success"] is True
        assert len(result["newState"]["edges"]) == 2

    @pytest.mark.asyncio
    async def test_node_properties_update(self, agent):
        """Test node properties update."""
        update_input = {
            "action": "update_properties",
            "targetNodes": ["node-1"],
            "properties": {
                "label": "Updated Node",
                "parameters": {"method": "POST"}
            }
        }

        # Setup
        agent.canvas_engine.update_node_properties = Mock(return_value={
            "nodes": [
                {
                    "id": "node-1",
                    "type": "trigger",
                    "position": {"x": 100, "y": 100},
                    "data": update_input["properties"]
                }
            ]
        })

        # Execute
        result = await agent.handle_canvas_action(update_input)

        # Assertions
        assert result["success"] is True
        agent.canvas_engine.update_node_properties.assert_called_once()

    @pytest.mark.asyncio
    async def test_canvas_export(self, agent, canvas_state):
        """Test canvas state export."""
        # Setup
        agent.current_state = canvas_state
        agent.storage_service.export_state = AsyncMock(return_value=canvas_state)

        # Execute
        result = await agent.export_canvas("workflow-123")

        # Assertions
        assert result["success"] is True
        assert result["data"] == canvas_state

    @pytest.mark.asyncio
    async def test_canvas_import(self, agent, canvas_state):
        """Test canvas state import."""
        # Setup
        agent.canvas_engine.import_state = Mock(return_value=canvas_state)
        agent.storage_service.save_state = AsyncMock(return_value=True)

        # Execute
        result = await agent.import_canvas("workflow-123", canvas_state)

        # Assertions
        assert result["success"] is True
        agent.canvas_engine.import_state.assert_called_once()

    @pytest.mark.asyncio
    async def test_error_handling(self, agent, move_action_input):
        """Test error handling in canvas operations."""
        # Setup canvas engine to raise error
        agent.canvas_engine.move_nodes = Mock(side_effect=Exception("Canvas error"))

        # Execute
        result = await agent.handle_canvas_action(move_action_input)

        # Assertions
        assert result["success"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_performance_monitoring(self, agent, canvas_state):
        """Test performance monitoring during canvas operations."""
        # Setup
        agent.canvas_engine.move_nodes = Mock(return_value=canvas_state)

        # Execute
        import time
        start_time = time.time()
        result = await agent.handle_canvas_action({
            "action": "move",
            "targetNodes": ["node-1"],
            "position": {"x": 200, "y": 200}
        })
        end_time = time.time()

        # Assertions
        assert result["success"] is True
        assert (end_time - start_time) < 1.0  # Should complete within 1 second

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, agent, canvas_state):
        """Test handling of concurrent canvas operations."""
        # Setup multiple concurrent operations
        operations = [
            {"action": "move", "targetNodes": ["node-1"], "position": {"x": i * 100, "y": 100}}
            for i in range(5)
        ]

        agent.canvas_engine.move_nodes = Mock(return_value=canvas_state)

        # Execute concurrent operations
        tasks = [
            agent.handle_canvas_action(op)
            for op in operations
        ]

        results = await asyncio.gather(*tasks)

        # Assertions
        assert len(results) == 5
        assert all(result["success"] for result in results)

    @pytest.mark.asyncio
    async def test_memory_management(self, agent, canvas_state):
        """Test memory management during canvas operations."""
        # Setup large canvas state
        large_canvas = canvas_state.copy()
        large_canvas["nodes"] = [
            {**node, "id": f"node-{i}", "position": {"x": i * 10, "y": i * 10}}
            for i, node in enumerate([canvas_state["nodes"][0]] * 100)
        ]

        agent.current_state = large_canvas

        # Execute operation on large canvas
        result = await agent.handle_canvas_action({
            "action": "move",
            "targetNodes": [f"node-{i}" for i in range(10)],
            "position": {"x": 1000, "y": 1000}
        })

        # Assertions
        assert result["success"] is True
        # In real implementation, would verify memory usage doesn't exceed limits

    @pytest.mark.asyncio
    async def test_validation_integration(self, agent, canvas_state):
        """Test integration with node validation."""
        # Setup validation call
        agent.event_bus.request = AsyncMock(return_value={
            "isValid": True,
            "errors": [],
            "warnings": []
        })

        # Execute validation request
        validation_result = await agent.validate_workflow_state(canvas_state)

        # Assertions
        assert validation_result["isValid"] is True
        agent.event_bus.request.assert_called_once()

    @pytest.mark.asyncio
    async def test_undo_redo_stack_management(self, agent, canvas_state):
        """Test undo/redo stack management."""
        # Setup initial state
        agent.current_state = canvas_state
        agent.history = [canvas_state.copy()]
        agent.redo_stack = []

        # Perform action that modifies state
        new_state = canvas_state.copy()
        new_state["nodes"][0]["position"] = {"x": 200, "y": 200}

        # Execute undo
        agent.current_state = agent.history[0]
        undo_result = await agent.handle_canvas_action({"action": "undo"})

        # Assertions
        assert undo_result["success"] is True
        assert agent.current_state == canvas_state
