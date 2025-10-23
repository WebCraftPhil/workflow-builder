"""
Mock implementation of WebSocket client for testing purposes.
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from unittest.mock import Mock


class WebSocketMock:
    """Mock WebSocket client for testing."""

    def __init__(self, url: str = "ws://test.example.com"):
        self.url = url
        self.connected = False
        self.messages_sent: List[Dict[str, Any]] = []
        self.messages_received: List[Dict[str, Any]] = []
        self.connection_history: List[Dict[str, Any]] = []
        self.error_simulation: Optional[Exception] = None

    async def connect(self, url: str = None) -> bool:
        """Mock WebSocket connection."""
        connection_url = url or self.url

        if self.error_simulation:
            raise self.error_simulation

        self.connected = True
        self.connection_history.append({
            "action": "connect",
            "url": connection_url,
            "timestamp": asyncio.get_event_loop().time(),
            "success": True
        })

        return True

    async def disconnect(self, code: int = 1000, reason: str = "") -> None:
        """Mock WebSocket disconnection."""
        self.connected = False
        self.connection_history.append({
            "action": "disconnect",
            "code": code,
            "reason": reason,
            "timestamp": asyncio.get_event_loop().time(),
            "success": True
        })

    async def send(self, message: Any) -> bool:
        """Mock sending message through WebSocket."""
        if not self.connected:
            raise Exception("WebSocket is not connected")

        if self.error_simulation:
            raise self.error_simulation

        # Convert message to JSON string if it's a dict
        if isinstance(message, dict):
            message_str = json.dumps(message)
        else:
            message_str = str(message)

        sent_message = {
            "message": message_str,
            "timestamp": asyncio.get_event_loop().time(),
            "direction": "sent"
        }

        self.messages_sent.append(sent_message)

        return True

    async def receive(self, timeout: float = 1.0) -> Optional[str]:
        """Mock receiving message through WebSocket."""
        if not self.connected:
            raise Exception("WebSocket is not connected")

        if self.error_simulation:
            raise self.error_simulation

        # Check if there are queued messages to receive
        if self.messages_received:
            received_message = self.messages_received.pop(0)
            return received_message["message"]

        # Simulate timeout
        await asyncio.sleep(0.1)
        return None

    def queue_message(self, message: Any) -> None:
        """Queue a message to be received."""
        if isinstance(message, dict):
            message_str = json.dumps(message)
        else:
            message_str = str(message)

        self.messages_received.append({
            "message": message_str,
            "timestamp": asyncio.get_event_loop().time(),
            "direction": "received"
        })

    async def ping(self, data: bytes = b"") -> bool:
        """Mock WebSocket ping."""
        if not self.connected:
            return False

        self.connection_history.append({
            "action": "ping",
            "data": data,
            "timestamp": asyncio.get_event_loop().time(),
            "success": True
        })

        return True

    def set_error_simulation(self, error: Exception) -> None:
        """Set error to simulate during operations."""
        self.error_simulation = error

    def clear_error_simulation(self) -> None:
        """Clear error simulation."""
        self.error_simulation = None

    def get_message_count(self, direction: str = None) -> int:
        """Get count of messages sent or received."""
        if direction == "sent":
            return len(self.messages_sent)
        elif direction == "received":
            return len(self.messages_received)
        else:
            return len(self.messages_sent) + len(self.messages_received)

    def get_connection_count(self) -> int:
        """Get number of connection attempts."""
        return len([h for h in self.connection_history if h["action"] == "connect"])

    def clear_history(self) -> None:
        """Clear all history for clean test state."""
        self.messages_sent.clear()
        self.messages_received.clear()
        self.connection_history.clear()


class WebSocketServerMock:
    """Mock WebSocket server for testing."""

    def __init__(self):
        self.connections: List[WebSocketMock] = []
        self.broadcast_messages: List[Dict[str, Any]] = []
        self.url = "ws://localhost:8765"

    async def start_server(self, host: str = "localhost", port: int = 8765) -> None:
        """Mock starting WebSocket server."""
        self.url = f"ws://{host}:{port}"

    async def stop_server(self) -> None:
        """Mock stopping WebSocket server."""
        for connection in self.connections:
            await connection.disconnect()
        self.connections.clear()

    async def broadcast(self, message: Any) -> int:
        """Broadcast message to all connected clients."""
        if isinstance(message, dict):
            message_str = json.dumps(message)
        else:
            message_str = str(message)

        broadcast_info = {
            "message": message_str,
            "timestamp": asyncio.get_event_loop().time(),
            "recipient_count": len(self.connections)
        }

        self.broadcast_messages.append(broadcast_info)

        # Send to all connected clients
        for connection in self.connections:
            connection.queue_message(message)

        return len(self.connections)

    def create_connection(self) -> WebSocketMock:
        """Create a new mock connection."""
        connection = WebSocketMock(self.url)
        self.connections.append(connection)
        return connection

    def remove_connection(self, connection: WebSocketMock) -> None:
        """Remove a connection."""
        if connection in self.connections:
            self.connections.remove(connection)

    def get_connection_count(self) -> int:
        """Get number of active connections."""
        return len([c for c in self.connections if c.connected])

    def clear_all(self) -> None:
        """Clear all connections and history."""
        self.connections.clear()
        self.broadcast_messages.clear()
