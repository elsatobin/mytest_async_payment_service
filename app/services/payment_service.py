from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payment import Payment
from app.models.outbox import Outbox


async def create_payment(db: AsyncSession, data, idempotency_key: str) -> Payment:
    result = await db.execute(
        select(Payment).where(Payment.idempotency_key == idempotency_key)
    )
    existing = result.scalar_one_or_none()

    if existing:
        return existing

    payment = Payment(
        amount=data.amount,
        currency=data.currency.value,
        description=data.description,
        meta=data.metadata,
        idempotency_key=idempotency_key,
        webhook_url=str(data.webhook_url),
    )

    outbox = Outbox(
        event_type="payment.created",
        payload={"payment_id": str(payment.id), "attempt": 0},
    )

    db.add(payment)
    db.add(outbox)

    try:
        await db.commit()
        await db.refresh(payment)
    except IntegrityError:
        await db.rollback()
        result = await db.execute(
            select(Payment).where(Payment.idempotency_key == idempotency_key)
        )
        payment = result.scalar_one()

    return payment


async def get_payment(db: AsyncSession, payment_id: str) -> Payment | None:
    result = await db.execute(select(Payment).where(Payment.id == payment_id))
    return result.scalar_one_or_none()