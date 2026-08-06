import logging
import os
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, selectinload

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    filename: Mapped[str] = mapped_column(String)
    jurisdiction: Mapped[str] = mapped_column(String)
    risk_score: Mapped[int] = mapped_column(Integer)
    risk_category: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    clauses: Mapped[List["ClauseResult"]] = relationship(back_populates="run", cascade="all, delete-orphan")


class ClauseResult(Base):
    __tablename__ = "clause_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("analysis_runs.id"))
    original_text: Mapped[str] = mapped_column(Text)
    classification: Mapped[str] = mapped_column(String)
    explanation: Mapped[str] = mapped_column(Text)
    statute_cited: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    analysis_failed: Mapped[bool] = mapped_column(Boolean, default=False)

    run: Mapped["AnalysisRun"] = relationship(back_populates="clauses")


def _normalize_url(url: str) -> str:
    """Neon/most providers hand out postgres://... or postgresql://... - SQLAlchemy's async
    engine needs the asyncpg driver spelled out explicitly."""
    if url.startswith("postgres://"):
        return "postgresql+asyncpg://" + url[len("postgres://"):]
    if url.startswith("postgresql://") and "+asyncpg" not in url:
        return "postgresql+asyncpg://" + url[len("postgresql://"):]
    return url


class Database:
    """Wraps the async engine/session. If DATABASE_URL isn't set (or the DB is unreachable),
    every method degrades to a no-op with a logged warning rather than raising - analysis
    history is a nice-to-have, the core analyze pipeline must never depend on it being up."""

    def __init__(self):
        raw_url = os.getenv("DATABASE_URL")
        self.enabled = bool(raw_url)
        self.engine = None
        self.session_maker = None
        if self.enabled:
            self.engine = create_async_engine(_normalize_url(raw_url), pool_pre_ping=True)
            self.session_maker = async_sessionmaker(self.engine, expire_on_commit=False)
        else:
            logger.warning("DATABASE_URL not set - analysis history persistence is disabled.")

    async def init(self) -> None:
        if not self.enabled:
            return
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        except Exception as e:
            logger.warning(f"Database unreachable at startup ({e}); disabling history persistence.")
            self.enabled = False

    async def save_run(self, session_id: str, filename: str, jurisdiction: str, risk_score: int,
                        risk_category: str, clauses: list) -> None:
        if not self.enabled:
            return
        try:
            async with self.session_maker() as session:
                run = AnalysisRun(
                    session_id=session_id,
                    filename=filename,
                    jurisdiction=jurisdiction,
                    risk_score=risk_score,
                    risk_category=risk_category,
                    clauses=[
                        ClauseResult(
                            original_text=c["original_text"],
                            classification=c["classification"],
                            explanation=c["explanation"],
                            statute_cited=c.get("statute_cited"),
                            analysis_failed=c.get("analysis_failed", False),
                        )
                        for c in clauses
                    ],
                )
                session.add(run)
                await session.commit()
        except Exception as e:
            logger.warning(f"Failed to persist analysis run {session_id}: {e}")

    async def list_recent_runs(self, limit: int = 20) -> List[AnalysisRun]:
        if not self.enabled:
            return []
        try:
            async with self.session_maker() as session:
                result = await session.execute(
                    select(AnalysisRun).order_by(AnalysisRun.created_at.desc()).limit(limit)
                )
                return list(result.scalars().all())
        except Exception as e:
            logger.warning(f"Failed to list analysis history: {e}")
            return []

    async def get_run(self, session_id: str) -> Optional[AnalysisRun]:
        if not self.enabled:
            return None
        try:
            async with self.session_maker() as session:
                result = await session.execute(
                    select(AnalysisRun)
                    .options(selectinload(AnalysisRun.clauses))
                    .where(AnalysisRun.session_id == session_id)
                )
                return result.scalar_one_or_none()
        except Exception as e:
            logger.warning(f"Failed to fetch analysis run {session_id}: {e}")
            return None
