import json
from typing import Any, Optional
from backend.config.settings import settings

_store: dict = {}
_redis = None
USE_REDIS = False

try:
    if settings.REDIS_URL:
        import redis
        _redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
        _redis.ping()
        USE_REDIS = True
except Exception:
    pass

def set_key(key: str, value: Any, ttl: int = 86400):
    if USE_REDIS:
        _redis.setex(key, ttl, json.dumps(value))
    else:
        _store[key] = value

def get_key(key: str) -> Optional[Any]:
    if USE_REDIS:
        v = _redis.get(key)
        return json.loads(v) if v else None
    return _store.get(key)

def delete_key(key: str):
    if USE_REDIS:
        _redis.delete(key)
    else:
        _store.pop(key, None)

def list_keys(prefix: str = "") -> list:
    if USE_REDIS:
        return _redis.keys(f"{prefix}*")
    return [k for k in _store if k.startswith(prefix)]