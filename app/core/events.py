import logging
from app.utils.redis_cache import cache
from app.utils.rabbitmq import rabbitmq

logger = logging.getLogger(__name__)

async def init_redis() -> None:
    """Initialize Redis connection"""
    try:
        await cache.init()
        logger.info("Redis connection established")
    except Exception as e:
        logger.error(f"Failed to initialize Redis: {e}")
        raise

async def close_redis() -> None:
    """Close Redis connection"""
    try:
        await cache.close()
        logger.info("Redis connection closed")
    except Exception as e:
        logger.error(f"Failed to close Redis connection: {e}")
        raise

async def init_rabbitmq() -> None:
    """Initialize RabbitMQ connection"""
    try:
        await rabbitmq.connect()
        logger.info("RabbitMQ connection established")
    except Exception as e:
        logger.error(f"Failed to initialize RabbitMQ: {e}")
        raise

async def close_rabbitmq() -> None:
    """Close RabbitMQ connection"""
    try:
        await rabbitmq.close()
        logger.info("RabbitMQ connection closed")
    except Exception as e:
        logger.error(f"Failed to close RabbitMQ connection: {e}")
        raise