import pytest
import asyncio
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import fakeredis.aioredis

from app.main import app
from app.core.database import Base, get_db
from app.utils.redis_cache import cache
from app.utils.rabbitmq import rabbitmq

# Create test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def event_loop_policy():
    return asyncio.get_event_loop_policy()

@pytest.fixture(scope="session")
def event_loop(event_loop_policy: asyncio.AbstractEventLoopPolicy) -> Generator:
    loop = event_loop_policy.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def db_session():
    Base.metadata.create_all(bind=engine)
    
    async with TestingSessionLocal() as session:
        yield session
    
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
async def redis_mock():
    fake_redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
    original_redis = cache._redis
    cache._redis = fake_redis
    yield fake_redis
    cache._redis = original_redis

@pytest.fixture(scope="function")
def mock_rabbitmq(mocker):
    async def mock_publish(*args, **kwargs):
        pass
    
    mocker.patch.object(rabbitmq, 'publish_event', mock_publish)
    return rabbitmq