from app.db.session import SessionLocal
from app.models.outbox import Outbox
from app.broker import broker


async def publish_events():
    db = SessionLocal()

    events = db.query(Outbox).filter(Outbox.processed == False).all()

    for event in events:
        await broker.publish(
            event.payload,
            queue="payments.new"
        )

        event.processed = True

    db.commit()
    db.close()