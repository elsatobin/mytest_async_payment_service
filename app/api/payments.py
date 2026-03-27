from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.payment import PaymentCreate
from app.db.deps import get_db
from app.services.payment_service import create_payment

router = APIRouter(prefix="/api/v1/payments")


@router.post("")
def create_payment_endpoint(
    data: PaymentCreate,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    db = Depends(get_db),
):
    payment = create_payment(db, data, idempotency_key)

    return {
        "payment_id": str(payment.id),
        "status": payment.status,
        "created_at": payment.created_at,
    }
    
from sqlalchemy import select
from app.models.payment import Payment

@router.get("/{payment_id}")
async def get_payment(payment_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Payment).where(Payment.id == payment_id)
    )
    payment = result.scalar_one_or_none()

    if not payment:
        raise HTTPException(status_code=404, detail="Not found")

    return payment