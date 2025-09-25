from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert
from app.repositories.alert_repo import AlertRepository
from app.schemas.alert import AlertCreate, AlertUpdate


class AlertService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = AlertRepository(session)

    async def create_alert(self, data: AlertCreate) -> Alert:
        alert = Alert(
            title=data.title,
            message=data.message,
            severity=data.severity,
            delivery_type=data.delivery_type,
            remind_every_minutes=data.remind_every_minutes,
            reminders_enabled=data.reminders_enabled,
            start_at=data.start_at,
            expire_at=data.expire_at,
            archived=data.archived,
            org_wide=data.org_wide,
        )
        alert = await self.repo.create(alert, data.team_ids, data.user_ids)
        await self.session.commit()
        await self.session.refresh(alert)
        return alert

    async def update_alert(self, alert_id: int, data: AlertUpdate) -> Alert | None:
        alert = await self.repo.get(alert_id)
        if not alert:
            return None
        for field in (
            "title",
            "message",
            "severity",
            "delivery_type",
            "remind_every_minutes",
            "reminders_enabled",
            "start_at",
            "expire_at",
            "archived",
            "org_wide",
        ):
            value = getattr(data, field)
            if value is not None:
                setattr(alert, field, value)
        await self.repo.update_visibility(alert_id, data.team_ids, data.user_ids)
        await self.session.commit()
        await self.session.refresh(alert)
        return alert

    async def list_alerts(self):
        return await self.repo.list_all()


