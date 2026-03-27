from sqlalchemy import select
from app.models.payment import Payment
from app.models.outbox import Outbox


def create_payment(db, data, idempotency_key):
    result = db.execute(
        select(Payment).where(Payment.idempotency_key == idempotency_key)
    )
    existing = result.scalar_one_or_none()

    if existing:
        return existing

    payment = Payment(
        amount=data.amount,
        currency=data.currency,
        description=data.description,
        meta=data.metadata,  # 여기 변경
        idempotency_key=idempotency_key,
        webhook_url=data.webhook_url,
    )

    outbox = Outbox(
        event_type="payment.created",
        payload={"payment_id": str(payment.id)},
    )

    db.add(payment)
    db.add(outbox)

    db.commit()
    db.refresh(payment)

    return payment