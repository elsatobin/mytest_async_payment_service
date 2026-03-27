from faststream.rabbit import RabbitBroker

from app.core.config import RABBITMQ_URL

broker = RabbitBroker(
    RABBITMQ_URL,
)