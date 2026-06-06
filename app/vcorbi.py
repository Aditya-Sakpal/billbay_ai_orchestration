from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings

settings = get_settings()

VCORBI_CONNECT_TIMEOUT_SECONDS = 5

engine = create_engine(
    settings.vcorbi_url,
    echo=False,
    pool_pre_ping=True,
    connect_args={"connect_timeout": VCORBI_CONNECT_TIMEOUT_SECONDS},
    pool_timeout=VCORBI_CONNECT_TIMEOUT_SECONDS,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_vcorbi_session() -> Session:
    return SessionLocal()
