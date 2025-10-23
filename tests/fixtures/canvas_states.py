"""
Canvas states and UI test data for testing purposes.
"""

from typing import Dict, Any, List


# Empty canvas state
EMPTY_CANVAS = {
    "nodes": [],
    "edges": [],
    "viewport": {
        "x": 0,
        "y": 0,
        "zoom": 1.0
    },
    "selection": {
        "nodes": [],
        "edges": []
    }
}

# Canvas with basic workflow loaded
LOADED_CANVAS = {
    "nodes": [
        {
            "id": "node-1",
            "type": "n8n-nodes-base.manualTrigger",
            "position": {"x": 100, "y": 100},
            "data": {
                "label": "Manual Trigger",
                "parameters": {}
            }
        },
        {
            "id": "node-2",
            "type": "n8n-nodes-base.httpRequest",
            "position": {"x": 300, "y": 100},
            "data": {
                "label": "HTTP Request",
                "parameters": {
                    "method": "GET",
                    "url": "https://api.example.com"
                }
            }
        },
        {
            "id": "node-3",
            "type": "n8n-nodes-base.set",
            "position": {"x": 500, "y": 100},
            "data": {
                "label": "Set Data",
                "parameters": {
                    "values": {
                        "string": [
                            {"name": "result", "value": "success"}
                        ]
                    }
                }
            }
        }
    ],
    "edges": [
        {
            "id": "edge-1-2",
            "source": "node-1",
            "target": "node-2",
            "sourceHandle": "output-0",
            "targetHandle": "input-0"
        },
        {
            "id": "edge-2-3",
            "source": "node-2",
            "target": "node-3",
            "sourceHandle": "output-0",
            "targetHandle": "input-0"
        }
    ],
    "viewport": {
        "x": -50,
        "y": -50,
        "zoom": 1.0
    },
    "selection": {
        "nodes": [],
        "edges": []
    }
}

# Canvas with complex layout
COMPLEX_CANVAS = {
    "nodes": [
        {
            "id": "trigger",
            "type": "n8n-nodes-base.webhook",
            "position": {"x": 50, "y": 50},
            "data": {"label": "Webhook"}
        },
        {
            "id": "if-node",
            "type": "n8n-nodes-base.if",
            "position": {"x": 250, "y": 50},
            "data": {"label": "Condition"}
        },
        {
            "id": "success-action",
            "type": "n8n-nodes-base.gmail",
            "position": {"x": 450, "y": 20},
            "data": {"label": "Success Email"}
        },
        {
            "id": "failure-action",
            "type": "n8n-nodes-base.slack",
            "position": {"x": 450, "y": 80},
            "data": {"label": "Failure Notification"}
        },
        {
            "id": "database",
            "type": "n8n-nodes-base.postgres",
            "position": {"x": 650, "y": 50},
            "data": {"label": "Save to DB"}
        },
        {
            "id": "error-handler",
            "type": "n8n-nodes-base.errorTrigger",
            "position": {"x": 250, "y": 150},
            "data": {"label": "Error Handler"}
        }
    ],
    "edges": [
        {"id": "webhook-if", "source": "trigger", "target": "if-node"},
        {"id": "if-success", "source": "if-node", "target": "success-action", "sourceHandle": "output-0"},
        {"id": "if-failure", "source": "if-node", "target": "failure-action", "sourceHandle": "output-1"},
        {"id": "success-db", "source": "success-action", "target": "database"},
        {"id": "failure-db", "source": "failure-action", "target": "database"},
        {"id": "error-handler", "source": "if-node", "target": "error-handler", "sourceHandle": "error"}
    ],
    "viewport": {"x": 0, "y": 0, "zoom": 0.8},
    "selection": {"nodes": ["if-node"], "edges": []}
}

# Canvas with zoom and pan applied
ZOOMED_CANVAS = {
    "nodes": [
        {
            "id": "node-1",
            "type": "n8n-nodes-base.manualTrigger",
            "position": {"x": 1000, "y": 1000},
            "data": {"label": "Trigger"}
        },
        {
            "id": "node-2",
            "type": "n8n-nodes-base.httpRequest",
            "position": {"x": 1200, "y": 1000},
            "data": {"label": "HTTP"}
        }
    ],
    "edges": [
        {"id": "edge-1-2", "source": "node-1", "target": "node-2"}
    ],
    "viewport": {
        "x": -800,
        "y": -800,
        "zoom": 0.5
    },
    "selection": {"nodes": [], "edges": []}
}

# Canvas with multi-selection
MULTI_SELECTED_CANVAS = {
    "nodes": [
        {"id": "node-1", "type": "n8n-nodes-base.set", "position": {"x": 100, "y": 100}, "data": {"label": "Set 1"}},
        {"id": "node-2", "type": "n8n-nodes-base.set", "position": {"x": 300, "y": 100}, "data": {"label": "Set 2"}},
        {"id": "node-3", "type": "n8n-nodes-base.set", "position": {"x": 500, "y": 100}, "data": {"label": "Set 3"}},
        {"id": "node-4", "type": "n8n-nodes-base.set", "position": {"x": 700, "y": 100}, "data": {"label": "Set 4"}}
    ],
    "edges": [
        {"id": "edge-1-2", "source": "node-1", "target": "node-2"},
        {"id": "edge-2-3", "source": "node-2", "target": "node-3"},
        {"id": "edge-3-4", "source": "node-3", "target": "node-4"}
    ],
    "viewport": {"x": 0, "y": 0, "zoom": 1.0},
    "selection": {
        "nodes": ["node-1", "node-3"],
        "edges": ["edge-1-2"]
    }
}

# Invalid canvas states for testing error handling
INVALID_CANVAS_MISSING_POSITIONS = {
    "nodes": [
        {"id": "node-1", "type": "n8n-nodes-base.set"}  # Missing position
    ],
    "edges": [],
    "viewport": {"x": 0, "y": 0, "zoom": 1.0}
}

INVALID_CANVAS_INVALID_CONNECTIONS = {
    "nodes": [
        {"id": "node-1", "type": "n8n-nodes-base.set", "position": {"x": 100, "y": 100}},
        {"id": "node-2", "type": "n8n-nodes-base.set", "position": {"x": 300, "y": 100}}
    ],
    "edges": [
        {"id": "invalid-edge", "source": "node-1", "target": "non-existent-node"}
    ],
    "viewport": {"x": 0, "y": 0, "zoom": 1.0}
}

# Node positions for testing movement operations
NODE_POSITIONS = {
    "top_left": {"x": 50, "y": 50},
    "top_right": {"x": 750, "y": 50},
    "bottom_left": {"x": 50, "y": 550},
    "bottom_right": {"x": 750, "y": 550},
    "center": {"x": 400, "y": 300}
}

# Viewport configurations for testing zoom and pan
VIEWPORT_CONFIGS = {
    "zoomed_in": {"x": 0, "y": 0, "zoom": 2.0},
    "zoomed_out": {"x": 0, "y": 0, "zoom": 0.25},
    "panned": {"x": -200, "y": -100, "zoom": 1.0},
    "zoomed_and_panned": {"x": -300, "y": -200, "zoom": 1.5}
}

# Selection states for testing multi-selection
SELECTION_STATES = {
    "none": {"nodes": [], "edges": []},
    "single_node": {"nodes": ["node-1"], "edges": []},
    "single_edge": {"nodes": [], "edges": ["edge-1"]},
    "multiple_nodes": {"nodes": ["node-1", "node-2", "node-3"], "edges": []},
    "mixed": {"nodes": ["node-1"], "edges": ["edge-1", "edge-2"]}
}

# Collaborative editing scenarios
COLLABORATION_SCENARIOS = {
    "user_a_editing": {
        "user_id": "user-a",
        "action": "node_move",
        "node_id": "node-1",
        "from_position": {"x": 100, "y": 100},
        "to_position": {"x": 200, "y": 150}
    },
    "user_b_editing": {
        "user_id": "user-b",
        "action": "node_add",
        "node_type": "n8n-nodes-base.set",
        "position": {"x": 300, "y": 200}
    },
    "conflict_scenario": {
        "user_a": {"node_id": "node-1", "position": {"x": 100, "y": 100}},
        "user_b": {"node_id": "node-1", "position": {"x": 400, "y": 400}},
        "expected_resolution": "merge"  # or "latest_wins", "user_priority"
    }
}


def get_canvas_by_name(name: str) -> Dict[str, Any]:
    """Get canvas state by name."""
    canvases = {
        "empty": EMPTY_CANVAS,
        "loaded": LOADED_CANVAS,
        "complex": COMPLEX_CANVAS,
        "zoomed": ZOOMED_CANVAS,
        "multi_selected": MULTI_SELECTED_CANVAS,
        "invalid_missing": INVALID_CANVAS_MISSING_POSITIONS,
        "invalid_connections": INVALID_CANVAS_INVALID_CONNECTIONS
    }
    return canvases.get(name, EMPTY_CANVAS)


def get_position(name: str) -> Dict[str, int]:
    """Get predefined position by name."""
    return NODE_POSITIONS.get(name, NODE_POSITIONS["center"])


def get_viewport_config(name: str) -> Dict[str, Any]:
    """Get viewport configuration by name."""
    return VIEWPORT_CONFIGS.get(name, VIEWPORT_CONFIGS["zoomed_in"])


def get_selection_state(name: str) -> Dict[str, List[str]]:
    """Get selection state by name."""
    return SELECTION_STATES.get(name, SELECTION_STATES["none"])
