from typing import Any, Optional
import json
from redis.asyncio import Redis
from fastapi.encoders import jsonable_encoder
from config.settings import settings

class RedisCache:
    def __init__(self):
        self.redis_url = settings.get_redis_url
        self._redis: Optional[Redis] = None

    async def init(self):
        """Initialize Redis connection"""
        if not self._redis:
            self._redis = Redis.from_url(
                self.redis_url,
                decode_responses=True,
                encoding="utf-8"
            )

    async def close(self):
        """Close Redis connection"""
        if self._redis:
            await self._redis.close()
            self._redis = None

    async def get(self, key: str) -> Any:
        """Get value from cache"""
        if not self._redis:
            await self.init()
        
        value = await self._redis.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None

    async def set(
        self,
        key: str,
        value: Any,
        expire: int = settings.CACHE_EXPIRE_IN_SECONDS
    ):
        """Set value in cache"""
        if not self._redis:
            await self.init()
        
        try:
            serialized_value = (
                json.dumps(value)
                if not isinstance(value, (str, int, float))
                else str(value)
            )
            await self._redis.set(key, serialized_value, ex=expire)
        except (TypeError, ValueError) as e:
            raise ValueError(f"Unable to serialize value: {str(e)}")

    async def delete(self, key: str):
        """Delete value from cache"""
        if not self._redis:
            await self.init()
        
        await self._redis.delete(key)

    async def clear_all(self):
        """Clear all cache"""
        if not self._redis:
            await self.init()
        
        await self._redis.flushall(asynchronous=True)

    async def invalidate_pattern(self, pattern: str):
        """Invalidate all keys matching pattern"""
        if not self._redis:
            await self.init()
        
        keys = await self._redis.keys(pattern)
        if keys:
            await self._redis.delete(*keys)

# Create a global cache instance
cache = RedisCache()