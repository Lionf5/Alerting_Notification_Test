from __future__ import annotations

from datetime import date, datetime

from enum import Enum as PyEnum
from sqlalchemy import Boolean, Date, DateTime, Enum as SAEnum, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ReadState(str, PyEnum):
    unread = "unread"
    read = "read"


class UserAlertPreference(Base):
    __tablename__ = "user_alert_preferences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    alert_id: Mapped[int] = mapped_column(ForeignKey("alerts.id", ondelete="CASCADE"), index=True)

    read_state: Mapped[ReadState] = mapped_column(SAEnum(ReadState), default=ReadState.unread, nullable=False)
    snoozed_for_day: Mapped[date | None] = mapped_column(Date, nullable=True)
    last_reminded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    muted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


