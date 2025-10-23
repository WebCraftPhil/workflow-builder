"""
Sample workflows and test data for testing purposes.
"""

from typing import Dict, Any, List


# Simple workflow with basic trigger and action
SIMPLE_WORKFLOW = {
    "nodes": [
        {
            "id": "manual-trigger",
            "type": "n8n-nodes-base.manualTrigger",
            "position": [100, 100],
            "parameters": {
                "description": "Manual trigger for testing"
            }
        },
        {
            "id": "http-request",
            "type": "n8n-nodes-base.httpRequest",
            "position": [300, 100],
            "parameters": {
                "method": "GET",
                "url": "https://jsonplaceholder.typicode.com/posts/1",
                "options": {}
            }
        }
    ],
    "connections": [
        {
            "id": "manual-trigger->http-request",
            "source": "manual-trigger",
            "target": "http-request",
            "sourceOutput": 0,
            "targetInput": 0
        }
    ]
}

# Complex workflow with branching logic
COMPLEX_WORKFLOW = {
    "nodes": [
        {
            "id": "webhook-trigger",
            "type": "n8n-nodes-base.webhook",
            "position": [50, 50],
            "parameters": {
                "httpMethod": "POST",
                "path": "test-webhook"
            }
        },
        {
            "id": "if-condition",
            "type": "n8n-nodes-base.if",
            "position": [200, 50],
            "parameters": {
                "conditions": {
                    "boolean": [
                        {
                            "value1": "={{ $json.status }}",
                            "value2": "active"
                        }
                    ]
                }
            }
        },
        {
            "id": "email-success",
            "type": "n8n-nodes-base.gmail",
            "position": [350, 20],
            "parameters": {
                "to": "success@example.com",
                "subject": "Success notification",
                "text": "={{ $json.message }}"
            }
        },
        {
            "id": "email-failure",
            "type": "n8n-nodes-base.gmail",
            "position": [350, 80],
            "parameters": {
                "to": "admin@example.com",
                "subject": "Failure alert",
                "text": "={{ $json.error }}"
            }
        },
        {
            "id": "database-save",
            "type": "n8n-nodes-base.postgres",
            "position": [500, 50],
            "parameters": {
                "query": "INSERT INTO logs (status, message) VALUES ({{ $json.status }}, {{ $json.message }})"
            }
        }
    ],
    "connections": [
        {
            "id": "webhook->if",
            "source": "webhook-trigger",
            "target": "if-condition",
            "sourceOutput": 0,
            "targetInput": 0
        },
        {
            "id": "if-true->email-success",
            "source": "if-condition",
            "target": "email-success",
            "sourceOutput": 0,
            "targetInput": 0
        },
        {
            "id": "if-false->email-failure",
            "source": "if-condition",
            "target": "email-failure",
            "sourceOutput": 1,
            "targetInput": 0
        },
        {
            "id": "email-success->database",
            "source": "email-success",
            "target": "database-save",
            "sourceOutput": 0,
            "targetInput": 0
        },
        {
            "id": "email-failure->database",
            "source": "email-failure",
            "target": "database-save",
            "sourceOutput": 0,
            "targetInput": 0
        }
    ]
}

# Workflow with loops and iterations
LOOP_WORKFLOW = {
    "nodes": [
        {
            "id": "manual-trigger",
            "type": "n8n-nodes-base.manualTrigger",
            "position": [100, 100]
        },
        {
            "id": "split-in-batches",
            "type": "n8n-nodes-base.splitInBatches",
            "position": [300, 100],
            "parameters": {
                "batchSize": 2,
                "options": {
                    "reset": True
                }
            }
        },
        {
            "id": "process-batch",
            "type": "n8n-nodes-base.set",
            "position": [500, 100],
            "parameters": {
                "values": {
                    "string": [
                        {
                            "name": "processed",
                            "value": "={{ $json.item * 2 }}"
                        }
                    ]
                }
            }
        }
    ],
    "connections": [
        {
            "id": "trigger->split",
            "source": "manual-trigger",
            "target": "split-in-batches",
            "sourceOutput": 0,
            "targetInput": 0
        },
        {
            "id": "split->process",
            "source": "split-in-batches",
            "target": "process-batch",
            "sourceOutput": 0,
            "targetInput": 0
        }
    ]
}

# Error handling workflow
ERROR_HANDLING_WORKFLOW = {
    "nodes": [
        {
            "id": "trigger",
            "type": "n8n-nodes-base.manualTrigger",
            "position": [100, 100]
        },
        {
            "id": "error-prone-action",
            "type": "n8n-nodes-base.httpRequest",
            "position": [300, 100],
            "parameters": {
                "method": "GET",
                "url": "https://httpstat.us/500",  # Always returns 500 error
                "options": {
                    "timeout": 1
                }
            }
        },
        {
            "id": "error-handler",
            "type": "n8n-nodes-base.errorTrigger",
            "position": [300, 200],
            "parameters": {}
        },
        {
            "id": "fallback-action",
            "type": "n8n-nodes-base.set",
            "position": [500, 200],
            "parameters": {
                "values": {
                    "string": [
                        {
                            "name": "fallback",
                            "value": "Fallback executed"
                        }
                    ]
                }
            }
        }
    ],
    "connections": [
        {
            "id": "trigger->error-prone",
            "source": "trigger",
            "target": "error-prone-action",
            "sourceOutput": 0,
            "targetInput": 0
        },
        {
            "id": "error-prone->error-handler",
            "source": "error-prone-action",
            "target": "error-handler",
            "sourceOutput": 1,  # Error output
            "targetInput": 0
        },
        {
            "id": "error-handler->fallback",
            "source": "error-handler",
            "target": "fallback-action",
            "sourceOutput": 0,
            "targetInput": 0
        }
    ]
}

# AI workflow with multiple AI nodes
AI_WORKFLOW = {
    "nodes": [
        {
            "id": "input-trigger",
            "type": "n8n-nodes-base.manualTrigger",
            "position": [100, 100],
            "parameters": {
                "description": "Input text for AI processing"
            }
        },
        {
            "id": "text-analysis",
            "type": "n8n-nodes-base.openAI",
            "position": [300, 100],
            "parameters": {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "system",
                        "content": "Analyze the sentiment of the input text."
                    },
                    {
                        "role": "user",
                        "content": "={{ $json.text }}"
                    }
                ]
            }
        },
        {
            "id": "text-summarization",
            "type": "n8n-nodes-base.anthropic",
            "position": [500, 100],
            "parameters": {
                "model": "claude-2",
                "prompt": "Summarize the following text: {{ $json.analysis }}"
            }
        }
    ],
    "connections": [
        {
            "id": "trigger->analysis",
            "source": "input-trigger",
            "target": "text-analysis",
            "sourceOutput": 0,
            "targetInput": 0
        },
        {
            "id": "analysis->summarization",
            "source": "text-analysis",
            "target": "text-summarization",
            "sourceOutput": 0,
            "targetInput": 0
        }
    ]
}

# Large workflow for performance testing
LARGE_WORKFLOW = {
    "nodes": [],
    "connections": []
}

# Generate 50 nodes for performance testing
for i in range(50):
    node_id = f"node-{i}"
    node_type = "n8n-nodes-base.set" if i % 5 != 0 else "n8n-nodes-base.if"

    LARGE_WORKFLOW["nodes"].append({
        "id": node_id,
        "type": node_type,
        "position": [100 + (i % 10) * 150, 100 + (i // 10) * 100],
        "parameters": {
            "values": {
                "string": [
                    {
                        "name": f"field-{i}",
                        "value": f"value-{i}"
                    }
                ]
            }
        }
    })

# Create connections in a chain pattern
for i in range(49):
    LARGE_WORKFLOW["connections"].append({
        "id": f"connection-{i}",
        "source": f"node-{i}",
        "target": f"node-{i+1}",
        "sourceOutput": 0,
        "targetInput": 0
    })


# Invalid workflows for testing error handling
INVALID_WORKFLOW_MISSING_NODES = {
    "nodes": [],
    "connections": [
        {
            "source": "non-existent-node",
            "target": "another-non-existent-node"
        }
    ]
}

INVALID_WORKFLOW_CIRCULAR_DEPENDENCY = {
    "nodes": [
        {"id": "node-1", "type": "n8n-nodes-base.set", "position": [100, 100]},
        {"id": "node-2", "type": "n8n-nodes-base.set", "position": [300, 100]},
        {"id": "node-3", "type": "n8n-nodes-base.set", "position": [500, 100]}
    ],
    "connections": [
        {"source": "node-1", "target": "node-2"},
        {"source": "node-2", "target": "node-3"},
        {"source": "node-3", "target": "node-1"}  # Creates circular dependency
    ]
}

INVALID_WORKFLOW_INVALID_NODE_TYPE = {
    "nodes": [
        {
            "id": "invalid-node",
            "type": "non-existent-node-type",
            "position": [100, 100]
        }
    ],
    "connections": []
}


# Workflow templates for testing import/export
WORKFLOW_TEMPLATES = {
    "email-automation": {
        "name": "Email Automation Template",
        "description": "Automated email processing workflow",
        "category": "Communication",
        "workflow": SIMPLE_WORKFLOW
    },
    "data-processing": {
        "name": "Data Processing Template",
        "description": "Batch data processing pipeline",
        "category": "Data",
        "workflow": LOOP_WORKFLOW
    },
    "error-handling": {
        "name": "Error Handling Template",
        "description": "Robust error handling pattern",
        "category": "Logic",
        "workflow": ERROR_HANDLING_WORKFLOW
    }
}


def get_workflow_by_name(name: str) -> Dict[str, Any]:
    """Get workflow by name."""
    workflows = {
        "simple": SIMPLE_WORKFLOW,
        "complex": COMPLEX_WORKFLOW,
        "loop": LOOP_WORKFLOW,
        "error-handling": ERROR_HANDLING_WORKFLOW,
        "ai": AI_WORKFLOW,
        "large": LARGE_WORKFLOW,
        "invalid-missing": INVALID_WORKFLOW_MISSING_NODES,
        "invalid-circular": INVALID_WORKFLOW_CIRCULAR_DEPENDENCY,
        "invalid-type": INVALID_WORKFLOW_INVALID_NODE_TYPE
    }
    return workflows.get(name, SIMPLE_WORKFLOW)


def get_template_by_name(name: str) -> Dict[str, Any]:
    """Get workflow template by name."""
    return WORKFLOW_TEMPLATES.get(name, WORKFLOW_TEMPLATES["email-automation"])
