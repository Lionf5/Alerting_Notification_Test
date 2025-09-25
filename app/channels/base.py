from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert, DeliveryType
from app.models.notification import NotificationDelivery


class NotificationChannel(ABC):
    @property
    @abstractmethod
    def channel_type(self) -> DeliveryType:  # pragma: no cover
        raise NotImplementedError

    @abstractmethod
    async def send(self, session: AsyncSession, *, alert: Alert, user_id: int) -> None:  # pragma: no cover
        raise NotImplementedError


class InAppChannel(NotificationChannel):
    @property
    def channel_type(self) -> DeliveryType:
        return DeliveryType.in_app

    async def send(self, session: AsyncSession, *, alert: Alert, user_id: int) -> None:
        session.add(
            NotificationDelivery(
                alert_id=alert.id,
                user_id=user_id,
                channel=self.channel_type,
                delivered_at=datetime.now(timezone.utc),
                status="delivered",
            )
        )
        await session.flush()


CHANNELS: dict[DeliveryType, NotificationChannel] = {
    DeliveryType.in_app: InAppChannel(),
}


