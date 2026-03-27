import asyncio
from datetime import datetime, timezone
import logging
import random

import httpx
from faststream import FastStream
from faststream.rabbit import RabbitRouter
from sqlalchemy import select

from app.broker import broker
from app.core.config import PAYMENTS_DLQ, PAYMENTS_QUEUE
from app.db.session import SessionLocal
from app.models.outbox import Outbox
from app.models.payment import Payment

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)  # Уровень логирования
router = RabbitRouter()
app = FastStream(broker)


async def simulate_gateway() -> bool:
    await asyncio.sleep(random.uniform(2, 5))
    return random.random() < 0.9


async def send_webhook_with_retry(webhook_url: str, body: dict):
    last_error = None
    async with httpx.AsyncClient(timeout=10.0) as client:
        for attempt in range(3):
            try:
                response = await client.post(webhook_url, json=body)
                response.raise_for_status()
                return
            except Exception as exc:
                last_error = exc
                if attempt < 2:
                    await asyncio.sleep(2**attempt)
    raise RuntimeError(f"Webhook failed after retries: {last_error}") from last_error


@router.subscriber(PAYMENTS_QUEUE)
async def process_payment_event(message: dict):
    payment_id = message.get("payment_id")
    attempt = int(message.get("attempt", 0))
    if not payment_id:
        logger.warning("Message without payment_id: %s", message)
        return

    try:
        async with SessionLocal() as db:
            payment = (
                await db.execute(select(Payment).where(Payment.id == payment_id))
            ).scalar_one_or_none()
            if not payment:
                logger.warning("Payment not found for id=%s", payment_id)
                return

            gateway_ok = await simulate_gateway()
            payment.status = "succeeded" if gateway_ok else "failed"
            payment.processed_at = datetime.now(timezone.utc).replace(tzinfo=None)

            webhook_payload = {
                "payment_id": str(payment.id),
                "status": payment.status,
                "processed_at": payment.processed_at.isoformat(),
            }
            await send_webhook_with_retry(payment.webhook_url, webhook_payload)
            await db.commit()
            logger.info("Payment %s processed successfully", payment_id)
    except Exception:
        logger.exception("Payment processing failed id=%s attempt=%s", payment_id, attempt)
        if attempt < 2:
            await asyncio.sleep(2**attempt)
            retry_message = {"payment_id": payment_id, "attempt": attempt + 1}
            await broker.publish(retry_message, queue=PAYMENTS_QUEUE)
        else:
            await broker.publish(
                {"payment_id": payment_id, "reason": "max_attempts_exceeded"},
                queue=PAYMENTS_DLQ,
            )
            async with SessionLocal() as db:
                payment = (
                    await db.execute(select(Payment).where(Payment.id == payment_id))
                ).scalar_one_or_none()
                if payment:
                    payment.status = "failed"
                    payment.processed_at = datetime.now(timezone.utc).replace(tzinfo=None)
                dlq_outbox = Outbox(
                    event_type="payment.to_dlq",
                    payload={"payment_id": payment_id},
                    status="failed",
                    retry_count=3,
                )
                db.add(dlq_outbox)
                await db.commit()


broker.include_router(router)