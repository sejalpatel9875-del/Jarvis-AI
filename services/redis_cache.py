"""
Purpose:
Redis Caching & Distributed Queue Subsystem for Jarvis AI OS.

Responsibilities:
- Fast O(1) query response caching and session state storage
- Automatic fallback to thread-safe local memory cache if Redis is unavailable

Dependencies:
- json, time, threading, typing
"""

import json
import time
import threading
from typing import Any, Optional, Dict
from services.logger import logger

class LocalFallbackCache:
    """Thread-safe Local Memory Fallback Cache."""
    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def set(self, key: str, value: Any, ttl_seconds: int = 300):
        with self._lock:
            self._store[key] = {
                "val": value,
                "expires_at": time.time() + ttl_seconds
            }

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            item = self._store.get(key)
            if not item:
                return None
            if time.time() > item["expires_at"]:
                del self._store[key]
                return None
            return item["val"]

    def delete(self, key: str):
        with self._lock:
            self._store.pop(key, None)

class RedisCacheService:
    """Redis Caching Service with Automatic Local Fallback."""

    def __init__(self):
        self.fallback = LocalFallbackCache()
        self.is_redis_active = False
        # Redis client connection attempt
        try:
            import redis
            from core.config import settings
            self.r = redis.Redis.from_url(settings.redis_url, socket_timeout=1.0)
            self.r.ping()
            self.is_redis_active = True
            logger.info("REDIS_CACHE", "Connected to Redis Cache server successfully.")
        except Exception:
            self.is_redis_active = False

    def set_cache(self, key: str, value: Any, ttl_seconds: int = 300):
        """Sets cache key with expiration TTL."""
        serialized = json.dumps(value) if not isinstance(value, str) else value
        if self.is_redis_active:
            try:
                self.r.setex(key, ttl_seconds, serialized)
                return
            except Exception as e:
                logger.warning("REDIS_CACHE", f"Redis error, switching to fallback: {e}")
                self.is_redis_active = False
        
        self.fallback.set(key, serialized, ttl_seconds)

    def get_cache(self, key: str) -> Optional[Any]:
        """Gets cache value for key."""
        if self.is_redis_active:
            try:
                val = self.r.get(key)
                if val:
                    data = val.decode("utf-8") if isinstance(val, bytes) else str(val)
                    try:
                        return json.loads(data)
                    except Exception:
                        return data
            except Exception:
                self.is_redis_active = False

        val = self.fallback.get(key)
        if val and isinstance(val, str):
            try:
                return json.loads(val)
            except Exception:
                return val
        return val

# Global Redis Cache Singleton
redis_cache = RedisCacheService()
