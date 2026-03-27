# app/models/__init__.py
from .payment import Payment
from .outbox import Outbox

# 이제 app.models에서 바로 가져올 수 있습니다:
# from app.models import Payment, Outbox