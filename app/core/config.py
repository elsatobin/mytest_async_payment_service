import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@postgres:5432/payments",
)
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
API_KEY = os.getenv("API_KEY", "testkey")
OUTBOX_POLL_INTERVAL_SEC = float(os.getenv("OUTBOX_POLL_INTERVAL_SEC", "1.0"))
PAYMENTS_QUEUE = "payments.new"
PAYMENTS_DLQ = "payments.dlq"