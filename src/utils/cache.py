import os
import json
import logging
from typing import Any, Optional
import numpy as np

logger = logging.getLogger("digikala_cache")

try:
    import redis
except ImportError:
    redis = None

class SafeJSONEncoder(json.JSONEncoder):
    """JSON Encoder that handles NumPy scalars, sets, and float special values."""
    def default(self, obj):
        if isinstance(obj, (np.integer, int)):
            return int(obj)
        if isinstance(obj, (np.floating, float)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (set, tuple)):
            return list(obj)
        return super().default(obj)

class RedisCacheManager:
    _instance: Optional["RedisCacheManager"] = None

    def __init__(self):
        self.host = os.getenv("REDIS_HOST", "localhost")
        self.port = int(os.getenv("REDIS_PORT", 6379))
        self.db = int(os.getenv("REDIS_DB", 0))
        self.redis_url = os.getenv("REDIS_URL", None)
        self.analytics_ttl = int(os.getenv("REDIS_CACHE_TTL_ANALYTICS", 3600))
        self.rec_ttl = int(os.getenv("REDIS_CACHE_TTL_RECOMMENDATION", 1800))
        self.client = None
        self._init_client()

    def _init_client(self):
        if redis is None:
            self.client = None
            return
        try:
            if self.redis_url:
                self.client = redis.Redis.from_url(
                    self.redis_url,
                    socket_connect_timeout=1,
                    socket_timeout=1,
                    decode_responses=True
                )
            else:
                self.client = redis.Redis(
                    host=self.host,
                    port=self.port,
                    db=self.db,
                    socket_connect_timeout=1,
                    socket_timeout=1,
                    decode_responses=True
                )
        except Exception as e:
            logger.warning(f"Redis initialization warning (fallback enabled): {e}")
            self.client = None

    def is_available(self) -> bool:
        if self.client is None:
            return False
        try:
            return bool(self.client.ping())
        except Exception:
            return False

    def get(self, key: str) -> Optional[Any]:
        if not self.client:
            return None
        try:
            data = self.client.get(key)
            if data is not None:
                return json.loads(data)
        except Exception as e:
            logger.debug(f"Redis get failed for key '{key}': {e}")
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        if not self.client:
            return False
        try:
            serialized = json.dumps(value, cls=SafeJSONEncoder, ensure_ascii=False)
            if ttl is not None and ttl > 0:
                self.client.setex(key, ttl, serialized)
            else:
                self.client.set(key, serialized)
            return True
        except Exception as e:
            logger.debug(f"Redis set failed for key '{key}': {e}")
            return False

# Global Singleton Instance
cache_manager = RedisCacheManager()

def make_cache_key(prefix: str, **kwargs) -> str:
    """Builds a deterministic, sorted, collision-resistant key."""
    parts = []
    for k in sorted(kwargs.keys()):
        val = kwargs[k]
        if val is None:
            normalized = "null"
        elif isinstance(val, str):
            normalized = val.strip().lower()
        else:
            normalized = str(val)
        parts.append(f"{k}:{normalized}")
    return f"{prefix}:{':'.join(parts)}" if parts else prefix
