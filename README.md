# Async Payment Processing Service

Микросервис для асинхронной обработки платежей по ТЗ:
- FastAPI + Pydantic v2
- SQLAlchemy 2.0 async + PostgreSQL
- RabbitMQ + FastStream
- Outbox pattern
- Retry (3 попытки, экспоненциальная задержка)
- DLQ

## Запуск

```bash
docker compose up --build
```

Сервис API: `http://localhost:8000`  
RabbitMQ UI: `http://localhost:15672` (guest/guest)

## Миграции

Миграции применяются в контейнере `api` автоматически командой:

```bash
alembic upgrade head
```

## API

### 1) Создание платежа

`POST /api/v1/payments`  
Headers:
- `X-API-Key: testkey`
- `Idempotency-Key: <unique>`

Body:
```json
{
  "amount": 100.50,
  "currency": "USD",
  "description": "Test payment",
  "metadata": {"order_id": "123"},
  "webhook_url": "http://host.docker.internal:9000/webhook"
}
```

Response: `202 Accepted`
```json
{
  "payment_id": "uuid",
  "status": "pending",
  "created_at": "2026-03-27T00:00:00"
}
```

### 2) Получение платежа

`GET /api/v1/payments/{payment_id}`  
Header:
- `X-API-Key: testkey`

## Поток обработки

1. API сохраняет `payments` + `outbox` в одной транзакции.
2. Фоновый outbox publisher отправляет `pending` события в очередь `payments.new`.
3. Consumer:
   - эмулирует шлюз (2-5 сек, 90% success),
   - обновляет статус платежа,
   - отправляет webhook с retry (1s, 2s, 4s),
   - при окончательной ошибке отправляет сообщение в `payments.dlq`.

## Очереди

- Основная: `payments.new`
- Dead Letter Queue: `payments.dlq`

