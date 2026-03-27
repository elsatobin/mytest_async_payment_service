import asyncio
from fastapi import FastAPI

from app.api.payments import router as payment_router
from app.broker import broker
from app.publisher import run_outbox_publisher

app = FastAPI()
app.include_router(payment_router)

_publisher_task: asyncio.Task | None = None
_stop_event = asyncio.Event()


@app.on_event("startup")
async def startup():
    await broker.connect()
    global _publisher_task
    _publisher_task = asyncio.create_task(run_outbox_publisher(_stop_event))


@app.on_event("shutdown")
async def shutdown():
    _stop_event.set()
    if _publisher_task:
        await _publisher_task
    await broker.close()