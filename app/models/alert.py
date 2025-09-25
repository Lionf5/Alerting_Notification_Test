from __future__ import annotations

import enum
from datetime import datetime, timedelta

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, Interval, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Severity(str, enum.Enum):
    info = "Info"
    warning = "Warning"
    critical = "Critical"


class DeliveryType(str, enum.Enum):
    in_app = "InApp"
    email = "Email"
    sms = "SMS"


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[Severity] = mapped_column(Enum(Severity), nullable=False)
    delivery_type: Mapped[DeliveryType] = mapped_column(Enum(DeliveryType), default=DeliveryType.in_app, nullable=False)
    remind_every_minutes: Mapped[int] = mapped_column(Integer, default=120, nullable=False)
    reminders_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    start_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expire_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # visibility scope
    org_wide: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # relationships
    teams: Mapped[list[AlertTeamVisibility]] = relationship("AlertTeamVisibility", cascade="all, delete-orphan", back_populates="alert")
    users: Mapped[list[AlertUserVisibility]] = relationship("AlertUserVisibility", cascade="all, delete-orphan", back_populates="alert")


class AlertTeamVisibility(Base):
    __tablename__ = "alert_team_visibility"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    alert_id: Mapped[int] = mapped_column(ForeignKey("alerts.id", ondelete="CASCADE"), nullable=False, index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)

    alert: Mapped[Alert] = relationship("Alert", back_populates="teams")


class AlertUserVisibility(Base):
    __tablename__ = "alert_user_visibility"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    alert_id: Mapped[int] = mapped_column(ForeignKey("alerts.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    alert: Mapped[Alert] = relationship("Alert", back_populates="users")


