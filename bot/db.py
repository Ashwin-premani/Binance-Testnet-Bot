import logging
from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy import JSON, Column, DateTime, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


class OrderRecord(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    side: Mapped[str] = mapped_column(String(8), nullable=False)
    type: Mapped[str] = mapped_column(String(16), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    order_id: Mapped[str] = mapped_column(String(64), nullable=False)
    raw_response: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)


def get_engine(db_url: str = "sqlite:///trading_bot.db"):
    return create_engine(db_url, echo=False, future=True)


def init_db() -> None:
    engine = get_engine()
    Base.metadata.create_all(engine)
    logger.info("Database initialized.")


def save_order(response: Dict[str, Any]) -> None:
    engine = get_engine()
    with Session(engine) as session:
        record = OrderRecord(
            symbol=response.get("symbol", ""),
            side=response.get("side", ""),
            type=response.get("type", ""),
            status=response.get("status", ""),
            order_id=str(response.get("orderId", "")),
            raw_response=response,
        )
        session.add(record)
        session.commit()


def get_recent_orders(limit: int = 20) -> List[OrderRecord]:
    engine = get_engine()
    with Session(engine) as session:
        stmt = (
            session.query(OrderRecord)
            .order_by(OrderRecord.created_at.desc())
            .limit(limit)
        )
        return list(stmt)

