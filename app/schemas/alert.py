from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from app.models.alert import Severity, DeliveryType


class AlertBase(BaseModel):
    title: str
    message: str
    severity: Severity
    delivery_type: DeliveryType = DeliveryType.in_app
    remind_every_minutes: int = 120
    reminders_enabled: bool = True
    start_at: Optional[datetime] = None
    expire_at: Optional[datetime] = None
    archived: bool = False
    org_wide: bool = False
    team_ids: List[int] = []
    user_ids: List[int] = []


class AlertCreate(AlertBase):
    pass


class AlertUpdate(BaseModel):
    title: Optional[str] = None
    message: Optional[str] = None
    severity: Optional[Severity] = None
    delivery_type: Optional[DeliveryType] = None
    remind_every_minutes: Optional[int] = None
    reminders_enabled: Optional[bool] = None
    start_at: Optional[datetime] = None
    expire_at: Optional[datetime] = None
    archived: Optional[bool] = None
    org_wide: Optional[bool] = None
    team_ids: Optional[List[int]] = None
    user_ids: Optional[List[int]] = None


class AlertRead(AlertBase):
    id: int

    class Config:
        from_attributes = True


