from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# PostgreSQL 연결 문자열
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/payments"

# Base 모델 생성
Base = declarative_base()

# 엔진 생성
engine = create_engine(DATABASE_URL, echo=True)  # echo=True로 쿼리 로그 확인 가능

# 세션 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 테이블 생성 함수
def init_db():
    # models.py에서 Base를 상속받은 모델들을 임포트해야 metadata.create_all이 작동
    import app.models  # 반드시 Base를 상속한 Payment, Outbox 모델 포함
    Base.metadata.create_all(bind=engine)