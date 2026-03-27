# app/models/__init__.py
from .payment import Payment
from .outbox import Outbox

# Теперь можно импортировать прямо из app.models:
# from app.models import Payment, Outbox