from __future__ import annotations

from sqlalchemy import BigInteger, DateTime, Integer, String, UniqueConstraint, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

class Subscription(Base):
    __tablename__ = "subscriptions"
    __table_args__ = (
        UniqueConstraint("telegram_user_id", "channel_id", name="uq_user_channel"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    telegram_user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.telegram_user_id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    channel_identifier: Mapped[str] = mapped_column(String(255), nullable=False)
    channel_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
