# Async Payment Processing Service

## 📌 Overview
This project implements an asynchronous payment processing microservice.

The service:
- Accepts payment requests
- Processes them asynchronously via a simulated payment gateway
- Sends results back to clients using webhooks

---

## 🏗 Architecture

Components:

- **API (FastAPI)** – Handles incoming requests
- **PostgreSQL** – Stores payments and outbox events
- **RabbitMQ** – Message broker for async processing
- **Consumer (Worker)** – Processes payments and sends webhooks

---

## 📊 Data Models

### Payment
- id (UUID)
- amount (decimal)
- currency (RUB, USD, EUR)
- description (string)
- metadata (JSON)
- status (pending, succeeded, failed)
- idempotency_key (unique)
- webhook_url (string)
- created_at (datetime)
- processed_at (datetime)

### Outbox
- id (UUID)
- event_type (string)
- payload (JSON)
- status (pending, sent, failed)
- created_at (datetime)

---

## 🚀 API Endpoints

### Create Payment
**POST /api/v1/payments**

Headers:
```
Idempotency-Key: <unique-key>
X-API-Key: <your-api-key>
```

Body:
```json
{
  "amount": 100.5,
  "currency": "USD",
  "description": "Test payment",
  "metadata": {"order_id": "123"},
  "webhook_url": "http://example.com/webhook"
}
```

Response:
```
202 Accepted
```

---

### Get Payment
**GET /api/v1/payments/{payment_id}**

Headers:
```
X-API-Key: <your-api-key>
```

---

## 🔄 Processing Flow

1. Client sends payment request
2. API saves payment + outbox event
3. Outbox publisher sends event to RabbitMQ
4. Consumer processes payment (2–5 sec delay)
5. Status updated in DB
6. Webhook sent to client

---

## 🔁 Retry Logic

- Webhook delivery retried up to **3 times**
- Exponential backoff: 1s → 2s → 4s
- Failed messages go to **Dead Letter Queue (DLQ)**

---

## 📬 Messaging

- Queue: `payments.new`
- Dead Letter Queue: `payments.dlq`

---

## 🔐 Authentication

All endpoints require:
```
X-API-Key: <your-api-key>
```

---

## 🧪 Payment Simulation

- Processing time: 2–5 seconds
- Success rate: 90%
- Failure rate: 10%

---

## 🐳 Running the Project

### 1. Clone repository
```
git clone <repo>
cd project
```

### 2. Start services
```
docker-compose up --build
```

### 3. Apply migrations
```
alembic upgrade head
```

---

## 📌 Example Request

```bash
curl -X POST http://localhost:8000/api/v1/payments \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: abc123" \
  -H "X-API-Key: testkey" \
  -d '{
    "amount": 50,
    "currency": "USD",
    "description": "Demo",
    "metadata": {},
    "webhook_url": "http://localhost:9000/webhook"
  }'
```

---

## 🧠 Key Features

- Asynchronous processing via RabbitMQ
- Outbox pattern for reliable event delivery
- Idempotency protection
- Retry mechanism with exponential backoff
- Dead Letter Queue support

---

## 📈 Evaluation Focus

- Clean architecture
- Proper Outbox pattern implementation
- Reliable messaging (RabbitMQ)
- Error handling & retries
- Docker setup

---

## 📎 Notes

- Ensure webhook endpoint is reachable
- Use unique idempotency keys per request

---

## 👨‍💻 Author

Test task implementation

