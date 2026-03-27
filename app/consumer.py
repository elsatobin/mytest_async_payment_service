import time
import random
import requests

from app.db.session import SessionLocal
from app.models.payment import Payment
from app.models.outbox import Outbox


def process_payment():
    db = SessionLocal()

    try:
        # 1. 아직 처리 안 된 이벤트 가져오기
        events = db.query(Outbox).filter(Outbox.processed == False).all()

        for event in events:
            payment_id = event.payload["payment_id"]

            payment = db.query(Payment).get(payment_id)

            if not payment:
                continue

            # 2. 결제 처리 시뮬레이션
            time.sleep(random.randint(2, 5))

            success = random.random() < 0.9

            if success:
                payment.status = "succeeded"
            else:
                payment.status = "failed"

            # 3. webhook 호출
            try:
                requests.post(payment.webhook_url, json={
                    "payment_id": str(payment.id),
                    "status": payment.status
                })
            except Exception:
                print("Webhook failed")

            # 4. outbox 처리 완료
            event.processed = True

            db.commit()

    finally:
        db.close()


if __name__ == "__main__":
    while True:
        process_payment()
        time.sleep(5)