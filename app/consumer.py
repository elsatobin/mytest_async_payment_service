import json
import logging
from sqlalchemy.orm import Session
from app.db import get_db  # SQLAlchemy 2.x generator
from app.models.payment import Payment
from app.models.outbox import Outbox

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)  # 로그 레벨 설정

def process_events():
    # generator 기반 DB 세션 안전하게 사용
    for db in get_db():  # get_db()는 generator
        try:
            # 처리되지 않은 Outbox 조회
            outbox_events = db.query(Outbox).filter(Outbox.processed == False).all()

            for outbox_event in outbox_events:
                try:
                    payload = outbox_event.payload

                    # payload가 str이면 json으로 변환
                    if isinstance(payload, str):
                        payload = json.loads(payload)

                    # payment_id 추출
                    payment_id = payload.get("payment_id") if isinstance(payload, dict) else None

                    if not payment_id:
                        logger.warning(f"[Outbox {outbox_event.id}] payment_id 없음, 처리 건너뜀")
                        continue

                    # SQLAlchemy 2.x 방식으로 Payment 조회
                    payment = db.get(Payment, payment_id)
                    if not payment:
                        logger.error(f"[Outbox {outbox_event.id}] Payment {payment_id} 존재하지 않음")
                        continue

                    # 여기서 payment 처리 로직 수행
                    logger.info(f"[Outbox {outbox_event.id}] Payment {payment_id} 처리 완료")
                    outbox_event.processed = True
                    db.commit()

                except Exception as e:
                    logger.exception(f"[Outbox {outbox_event.id}] 처리 중 에러 발생: {e}")
                    db.rollback()

        finally:
            db.close()  # 세션 안전하게 종료

if __name__ == "__main__":
    process_events()