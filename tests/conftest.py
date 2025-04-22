import sys
import pytest
from typing import AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import fakeredis.aioredis

from app.main import app
from app.core.database import Base, get_db
from app.utils.redis_cache import cache
from app.utils.rabbitmq import rabbitmq

# Create test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    echo=True
)

AsyncTestingSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Удаляем фикстуру event_loop, так как она больше не нужна
# и используем параметр loop_scope в декораторе pytest.mark.asyncio

@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create tables and return session"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncTestingSessionLocal() as session:
        yield session
        
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[TestClient, None]:
    """Create test client"""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
async def redis_mock() -> AsyncGenerator[fakeredis.aioredis.FakeRedis, None]:
    """Create Redis mock"""
    fake_redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
    original_redis = cache._redis
    cache._redis = fake_redis
    yield fake_redis
    cache._redis = original_redis

@pytest.fixture(scope="function")
def mock_rabbitmq(mocker):
    """Create RabbitMQ mock"""
    async def mock_publish(*args, **kwargs):
        pass
    
    mocker.patch.object(rabbitmq, 'publish_event', mock_publish)
    return rabbitmq