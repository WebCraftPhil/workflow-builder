"""
Mock implementation of Redis client for testing purposes.
"""

import asyncio
import time
import json
from typing import Dict, Any, Optional, List, Union
from unittest.mock import Mock


class RedisMock:
    """Mock Redis client for testing."""

    def __init__(self):
        self.data: Dict[str, Dict[str, Any]] = {}
        self.pubsub_channels: Dict[str, List] = {}
        self.expiration_times: Dict[str, float] = {}
        self.operation_history: List[Dict[str, Any]] = []

    def _record_operation(self, operation: str, key: str, value: Any = None):
        """Record Redis operation for testing."""
        self.operation_history.append({
            "operation": operation,
            "key": key,
            "value": value,
            "timestamp": time.time()
        })

    async def set(self, key: str, value: Union[str, bytes, int, float], ex: int = None,
                  px: int = None, nx: bool = False, xx: bool = False) -> bool:
        """Mock Redis SET operation."""
        self._record_operation("SET", key, value)

        # Check NX (only set if key doesn't exist) and XX (only set if key exists)
        if nx and key in self.data:
            return False
        if xx and key not in self.data:
            return False

        # Set expiration time
        expiration = None
        if ex:
            expiration = time.time() + ex
        elif px:
            expiration = time.time() + (px / 1000)

        if expiration:
            self.expiration_times[key] = expiration

        self.data[key] = {
            "value": value,
            "type": type(value).__name__
        }

        return True

    async def get(self, key: str) -> Optional[str]:
        """Mock Redis GET operation."""
        self._record_operation("GET", key)

        # Check if key exists and hasn't expired
        if key not in self.data:
            return None

        if key in self.expiration_times:
            if time.time() > self.expiration_times[key]:
                await self.delete(key)
                return None

        data = self.data[key]
        if data["type"] == "str":
            return data["value"]
        elif data["type"] in ["int", "float"]:
            return str(data["value"])
        else:
            return json.dumps(data["value"])

    async def delete(self, *keys: str) -> int:
        """Mock Redis DEL operation."""
        deleted_count = 0
        for key in keys:
            self._record_operation("DEL", key)
            if key in self.data:
                del self.data[key]
                deleted_count += 1
            if key in self.expiration_times:
                del self.expiration_times[key]

        return deleted_count

    async def exists(self, *keys: str) -> int:
        """Mock Redis EXISTS operation."""
        count = 0
        for key in keys:
            self._record_operation("EXISTS", key)
            if key in self.data:
                if key in self.expiration_times:
                    if time.time() <= self.expiration_times[key]:
                        count += 1
                else:
                    count += 1
        return count

    async def expire(self, key: str, seconds: int) -> bool:
        """Mock Redis EXPIRE operation."""
        self._record_operation("EXPIRE", key, seconds)

        if key in self.data:
            self.expiration_times[key] = time.time() + seconds
            return True
        return False

    async def ttl(self, key: str) -> int:
        """Mock Redis TTL operation."""
        self._record_operation("TTL", key)

        if key not in self.expiration_times:
            return -1

        remaining = self.expiration_times[key] - time.time()
        return max(-1, int(remaining))

    async def keys(self, pattern: str = "*") -> List[str]:
        """Mock Redis KEYS operation."""
        self._record_operation("KEYS", pattern)

        import fnmatch
        matching_keys = []
        for key in self.data.keys():
            if fnmatch.fnmatch(key, pattern):
                # Check if key hasn't expired
                if key not in self.expiration_times or time.time() <= self.expiration_times[key]:
                    matching_keys.append(key)

        return matching_keys

    async def hset(self, key: str, field: str, value: Union[str, int, float]) -> int:
        """Mock Redis HSET operation."""
        self._record_operation("HSET", f"{key}:{field}", value)

        if key not in self.data:
            self.data[key] = {"value": {}, "type": "hash"}

        if self.data[key]["type"] != "hash":
            raise Exception("Key is not a hash")

        self.data[key]["value"][field] = value
        return 1

    async def hget(self, key: str, field: str) -> Optional[str]:
        """Mock Redis HGET operation."""
        self._record_operation("HGET", f"{key}:{field}")

        if key not in self.data or self.data[key]["type"] != "hash":
            return None

        return str(self.data[key]["value"].get(field, ""))

    async def hgetall(self, key: str) -> Dict[str, str]:
        """Mock Redis HGETALL operation."""
        self._record_operation("HGETALL", key)

        if key not in self.data or self.data[key]["type"] != "hash":
            return {}

        result = {}
        for field, value in self.data[key]["value"].items():
            result[field] = str(value)

        return result

    async def publish(self, channel: str, message: str) -> int:
        """Mock Redis PUBLISH operation."""
        self._record_operation("PUBLISH", channel, message)

        # Simulate subscribers receiving the message
        if channel in self.pubsub_channels:
            for subscriber in self.pubsub_channels[channel]:
                if hasattr(subscriber, 'put_nowait'):
                    subscriber.put_nowait(message)

        return len(self.pubsub_channels.get(channel, []))

    async def subscribe(self, *channels: str) -> 'PubSubMock':
        """Mock Redis SUBSCRIBE operation."""
        self._record_operation("SUBSCRIBE", ",".join(channels))

        pubsub = PubSubMock()
        for channel in channels:
            if channel not in self.pubsub_channels:
                self.pubsub_channels[channel] = []
            self.pubsub_channels[channel].append(pubsub)

        return pubsub

    async def lpush(self, key: str, *values: str) -> int:
        """Mock Redis LPUSH operation."""
        self._record_operation("LPUSH", key, values)

        if key not in self.data:
            self.data[key] = {"value": [], "type": "list"}

        if self.data[key]["type"] != "list":
            raise Exception("Key is not a list")

        self.data[key]["value"].extend(values)
        return len(self.data[key]["value"])

    async def rpop(self, key: str) -> Optional[str]:
        """Mock Redis RPOP operation."""
        self._record_operation("RPOP", key)

        if key not in self.data or self.data[key]["type"] != "list":
            return None

        if self.data[key]["value"]:
            return self.data[key]["value"].pop()

        return None

    def clear_all(self):
        """Clear all data for clean test state."""
        self.data.clear()
        self.expiration_times.clear()
        self.pubsub_channels.clear()
        self.operation_history.clear()

    def get_operation_count(self, operation: str = None) -> int:
        """Get count of operations matching criteria."""
        if operation:
            return len([op for op in self.operation_history if op["operation"] == operation])
        return len(self.operation_history)

    def get_keys_count(self) -> int:
        """Get total number of keys."""
        return len(self.data)


class PubSubMock:
    """Mock Redis PubSub for testing."""

    def __init__(self):
        self.channels: List[str] = []
        self.messages: asyncio.Queue = asyncio.Queue()

    async def get_message(self, timeout: float = 1.0) -> Optional[Dict[str, Any]]:
        """Mock get message from pubsub."""
        try:
            return await asyncio.wait_for(self.messages.get(), timeout=timeout)
        except asyncio.TimeoutError:
            return None

    def put_nowait(self, message: str):
        """Put message in queue."""
        self.messages.put_nowait({
            "type": "message",
            "data": message.encode('utf-8')
        })

    async def close(self):
        """Mock close pubsub connection."""
        pass
