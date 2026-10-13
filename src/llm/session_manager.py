import json
import hashlib
import os
import redis
from typing import Dict, Any, Optional

class RedisConversationManager:
    def __init__(self, host: str = None, port: int = None, db: int = None):
        self.host = host or os.getenv("REDIS_HOST", "localhost")
        self.port = int(port or os.getenv("REDIS_PORT", 6379))
        self.db = int(db or os.getenv("REDIS_DB", 0))
        self.client = redis.Redis(host=self.host, port=self.port, db=self.db, decode_responses=True)

    def _hash_key(self, raw_key: str) -> str:
        clean = (raw_key or "").strip().encode("utf-8", errors="ignore")
        return hashlib.md5(clean).hexdigest()

    def get_cached_search(self, query_key: str) -> Optional[Any]:
        safe_key = self._hash_key(query_key)
        try:
            data = self.client.get(f"cache:search:{safe_key}")
            return json.loads(data) if data else None
        except Exception:
            return None

    def set_cached_search(self, query_key: str, data: Any, ttl: int = 3600):
        safe_key = self._hash_key(query_key)
        try:
            self.client.setex(f"cache:search:{safe_key}", ttl, json.dumps(data, ensure_ascii=False))
        except Exception:
            pass

    def get_state(self, session_id: str) -> Dict[str, Any]:
        try:
            data = self.client.get(f"session:{session_id}")
            return json.loads(data) if data else {"history": [], "sentiment": "neutral", "category": None}
        except Exception:
            return {"history": [], "sentiment": "neutral", "category": None}

    def save_state(self, session_id: str, state: Dict[str, Any], ttl: int = 86400):
        try:
            self.client.setex(f"session:{session_id}", ttl, json.dumps(state, ensure_ascii=False))
        except Exception:
            pass

    def clear_session(self, session_id: str):
        try:
            self.client.delete(f"session:{session_id}")
        except Exception:
            pass
