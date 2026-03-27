from faststream.rabbit import RabbitBroker

broker = RabbitBroker(
    "amqp://guest:guest@localhost:5672/",
    queue_declare={
        "payments.new": {
            "x-dead-letter-exchange": "",
            "x-dead-letter-routing-key": "payments.dlq"
        }
    }
)