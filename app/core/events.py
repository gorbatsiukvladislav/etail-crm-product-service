import logging
from app.utils.rabbitmq import rabbitmq
from app.utils.redis_cache import cache

logger = logging.getLogger(__name__)

async def handle_product_event(message):
    """
    Handle product events from RabbitMQ
    """
    async with message.process():
        event = message.body.decode()
        logger.info(f"Received product event: {event}")
        
        # Invalidate cache for the product
        if "product_id" in event:
            await cache.delete(f"product:{event['product_id']}")

async def setup_event_handlers():
    """
    Setup RabbitMQ event handlers
    """
    await rabbitmq.subscribe("product.*", handle_product_event)