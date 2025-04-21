import json
from typing import Any, Optional
import aio_pika
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class RabbitMQ:
    def __init__(self):
        self.connection_url = (
            f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASS}"
            f"@{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}/"
        )
        self._connection: Optional[aio_pika.Connection] = None
        self._channel: Optional[aio_pika.Channel] = None
        self.exchange_name = "product_events"
        self._exchange: Optional[aio_pika.Exchange] = None

    async def connect(self):
        """Initialize RabbitMQ connection"""
        if not self._connection:
            try:
                self._connection = await aio_pika.connect_robust(self.connection_url)
                self._channel = await self._connection.channel()
                
                # Declare exchange
                self._exchange = await self._channel.declare_exchange(
                    self.exchange_name,
                    aio_pika.ExchangeType.TOPIC,
                    durable=True
                )
                
                logger.info("Successfully connected to RabbitMQ")
            except Exception as e:
                logger.error(f"Failed to connect to RabbitMQ: {e}")
                raise

    async def close(self):
        """Close RabbitMQ connection"""
        if self._connection:
            await self._connection.close()
            self._connection = None
            self._channel = None
            self._exchange = None
            logger.info("RabbitMQ connection closed")

    async def publish_event(self, routing_key: str, data: Any):
        """
        Publish event to RabbitMQ
        
        :param routing_key: Event type (e.g., "product.created", "product.updated")
        :param data: Event data to publish
        """
        if not self._connection or not self._exchange:
            await self.connect()

        try:
            message = aio_pika.Message(
                body=json.dumps({
                    "event": routing_key,
                    "data": data,
                    "timestamp": settings.get_current_timestamp()
                }).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            )

            await self._exchange.publish(
                message,
                routing_key=routing_key
            )
            
            logger.info(f"Published event {routing_key} with data: {data}")
        except Exception as e:
            logger.error(f"Failed to publish event {routing_key}: {e}")
            raise

    async def subscribe(self, routing_key: str, callback):
        """
        Subscribe to events from RabbitMQ
        
        :param routing_key: Event type to subscribe to (e.g., "product.*")
        :param callback: Async function to handle received messages
        """
        if not self._connection:
            await self.connect()

        # Declare queue
        queue = await self._channel.declare_queue(exclusive=True)
        
        # Bind queue to exchange with routing key
        await queue.bind(self._exchange, routing_key)
        
        # Start consuming messages
        await queue.consume(callback)
        
        logger.info(f"Subscribed to events with routing key: {routing_key}")

# Create a global RabbitMQ instance
rabbitmq = RabbitMQ()

# Helper function for publishing events
async def publish_event(routing_key: str, data: Any):
    """Helper function to publish events to RabbitMQ"""
    await rabbitmq.publish_event(routing_key, data)