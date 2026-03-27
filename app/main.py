from fastapi import FastAPI
from app.api.payments import router as payment_router
from app.db.init_db import init_db

app = FastAPI()


@app.on_event("startup")
def startup():
    init_db()


app.include_router(payment_router)