from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import API_KEY
from app.schemas.payment import PaymentAccepted, PaymentCreate, PaymentResponse
from app.db.deps import get_db
from app.services.payment_service import create_payment, get_payment

router = APIRouter(prefix="/api/v1/payments")


def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")) -> None:
    if x_api_key != API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")


@router.post(
    "",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=PaymentAccepted,
    dependencies=[Depends(verify_api_key)],
)
async def create_payment_endpoint(
    data: PaymentCreate,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    db: AsyncSession = Depends(get_db),
):
    payment = await create_payment(db, data, idempotency_key)

    return PaymentAccepted(
        payment_id=str(payment.id),
        status=payment.status,
        created_at=payment.created_at,
    )


@router.get(
    "/{payment_id}",
    response_model=PaymentResponse,
    dependencies=[Depends(verify_api_key)],
)
async def get_payment_endpoint(payment_id: str, db: AsyncSession = Depends(get_db)):
    payment = await get_payment(db, payment_id)

    if not payment:
        raise HTTPException(status_code=404, detail="Not found")

    return PaymentResponse.model_validate(payment)