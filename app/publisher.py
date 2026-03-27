import asyncio
import logging

from sqlalchemy import select

from app.broker import broker
from app.core.config import OUTBOX_POLL_INTERVAL_SEC, PAYMENTS_QUEUE
from app.db.session import SessionLocal
from app.models.outbox import Outbox

logger = logging.getLogger(__name__)


async def publish_pending_outbox_events():
    async with SessionLocal() as db:
        events = (
            await db.execute(
                select(Outbox)
                .where(Outbox.status == "pending")
                .with_for_update(skip_locked=True)
            )
        ).scalars().all()

        for event in events:
            try:
                await broker.publish(event.payload, queue=PAYMENTS_QUEUE)
                event.status = "sent"
            except Exception:
                event.retry_count += 1
                logger.exception("Failed to publish outbox event id=%s", event.id)

        await db.commit()


async def run_outbox_publisher(stop_event: asyncio.Event):
    while not stop_event.is_set():
        try:
            await publish_pending_outbox_events()
        except Exception:
            logger.exception("Outbox publisher loop error")
        await asyncio.sleep(OUTBOX_POLL_INTERVAL_SEC)