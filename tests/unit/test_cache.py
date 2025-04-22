import pytest
import json

# Добавляем параметр loop_scope к декоратору
@pytest.mark.asyncio(loop_scope="function")
async def test_cache_set_get(redis_mock):
    test_key = "test_key"
    test_value = {"name": "Test Product", "price": 100}
    
    # Set value in cache
    await redis_mock.set(test_key, json.dumps(test_value))
    
    # Get value from cache
    cached_value = await redis_mock.get(test_key)
    assert json.loads(cached_value) == test_value

@pytest.mark.asyncio(loop_scope="function")
async def test_cache_delete(redis_mock):
    test_key = "test_key"
    test_value = {"name": "Test Product", "price": 100}
    
    # Set and then delete value
    await redis_mock.set(test_key, json.dumps(test_value))
    await redis_mock.delete(test_key)
    
    # Value should not exist
    cached_value = await redis_mock.get(test_key)
    assert cached_value is None

@pytest.mark.asyncio(loop_scope="function")
async def test_cache_clear_all(redis_mock):
    # Set multiple values
    test_data = {
        "key1": {"name": "Product 1", "price": 100},
        "key2": {"name": "Product 2", "price": 200}
    }
    
    for key, value in test_data.items():
        await redis_mock.set(key, json.dumps(value))
    
    # Clear all cache
    await redis_mock.flushall()
    
    # Verify all values are cleared
    for key in test_data:
        assert await redis_mock.get(key) is None

@pytest.mark.asyncio(loop_scope="function")
async def test_cache_invalidate_pattern(redis_mock):
    # Set multiple values with pattern
    test_data = {
        "product:1": {"name": "Product 1", "price": 100},
        "product:2": {"name": "Product 2", "price": 200},
        "category:1": {"name": "Category 1"}
    }
    
    for key, value in test_data.items():
        await redis_mock.set(key, json.dumps(value))
    
    # Invalidate only product keys
    product_keys = await redis_mock.keys("product:*")
    if product_keys:
        await redis_mock.delete(*product_keys)
    
    # Verify product keys are deleted but category remains
    assert await redis_mock.get("product:1") is None
    assert await redis_mock.get("product:2") is None
    assert await redis_mock.get("category:1") is not None