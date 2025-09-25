from __future__ import annotations

from typing import Iterable, Sequence

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert, AlertTeamVisibility, AlertUserVisibility


class AlertRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, alert: Alert, team_ids: Iterable[int], user_ids: Iterable[int]) -> Alert:
        self.session.add(alert)
        await self.session.flush()
        if team_ids:
            self.session.add_all(
                [AlertTeamVisibility(alert_id=alert.id, team_id=tid) for tid in team_ids]
            )
        if user_ids:
            self.session.add_all(
                [AlertUserVisibility(alert_id=alert.id, user_id=uid) for uid in user_ids]
            )
        await self.session.flush()
        return alert

    async def update_visibility(self, alert_id: int, team_ids: Iterable[int] | None, user_ids: Iterable[int] | None) -> None:
        if team_ids is not None:
            await self.session.execute(
                delete(AlertTeamVisibility).where(AlertTeamVisibility.alert_id == alert_id)
            )
            self.session.add_all([AlertTeamVisibility(alert_id=alert_id, team_id=tid) for tid in team_ids])
        if user_ids is not None:
            await self.session.execute(
                delete(AlertUserVisibility).where(AlertUserVisibility.alert_id == alert_id)
            )
            self.session.add_all([AlertUserVisibility(alert_id=alert_id, user_id=uid) for uid in user_ids])

    async def get(self, alert_id: int) -> Alert | None:
        res = await self.session.execute(select(Alert).where(Alert.id == alert_id))
        return res.scalar_one_or_none()

    async def list_all(self) -> Sequence[Alert]:
        res = await self.session.execute(select(Alert))
        return list(res.scalars().all())


