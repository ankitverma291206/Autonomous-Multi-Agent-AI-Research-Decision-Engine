"""SQLAlchemy engine, report persistence, and request-scoped sessions."""

from collections.abc import Generator
from datetime import datetime
from pathlib import Path

from sqlalchemy import JSON, DateTime, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker
from sqlalchemy.pool import StaticPool

from research_engine.config import DATABASE_URL


if DATABASE_URL.startswith("sqlite:"):
    db_path = DATABASE_URL.removeprefix("sqlite:///")
    if db_path and db_path != ":memory:":
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    sqlite_options = {"connect_args": {"check_same_thread": False}}
    if DATABASE_URL in {"sqlite://", "sqlite:///:memory:"}:
        sqlite_options["poolclass"] = StaticPool
    engine = create_engine(DATABASE_URL, **sqlite_options)
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class ReportRecord(Base):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    query: Mapped[str] = mapped_column(String(2000), nullable=False)
    report: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)


def get_session() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session


def list_reports(session: Session, limit: int = 50) -> list[ReportRecord]:
    return list(session.scalars(select(ReportRecord).order_by(ReportRecord.created_at.desc()).limit(limit)))
