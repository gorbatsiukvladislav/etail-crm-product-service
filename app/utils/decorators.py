from functools import wraps
from app.utils.redis_cache import cache

def cached(key_prefix: str, expire: int = None):
    """
    Decorator for caching function results
    
    Usage:
    @cached("product:{id}")
    async def get_product(id: int):
        ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key = key_prefix.format(**kwargs)
            
            # Try to get from cache
            cached_value = await cache.get(key)
            if cached_value is not None:
                return cached_value
            
            # If not in cache, execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            await cache.set(key, result, expire=expire)
            
            return result
        return wrapper
    return decorator