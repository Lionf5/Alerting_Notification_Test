from __future__ import annotations

from datetime import date

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_alert_preference import ReadState, UserAlertPreference


class UserPreferenceService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def _get_or_create(self, user_id: int, alert_id: int) -> UserAlertPreference:
        stmt = select(UserAlertPreference).where(
            and_(UserAlertPreference.user_id == user_id, UserAlertPreference.alert_id == alert_id)
        )
        pref = (await self.session.execute(stmt)).scalar_one_or_none()
        if not pref:
            pref = UserAlertPreference(user_id=user_id, alert_id=alert_id)
            self.session.add(pref)
            await self.session.flush()
        return pref

    async def mark_read(self, user_id: int, alert_id: int) -> None:
        pref = await self._get_or_create(user_id, alert_id)
        pref.read_state = ReadState.read
        await self.session.commit()

    async def mark_unread(self, user_id: int, alert_id: int) -> None:
        pref = await self._get_or_create(user_id, alert_id)
        pref.read_state = ReadState.unread
        await self.session.commit()

    async def snooze_today(self, user_id: int, alert_id: int) -> None:
        pref = await self._get_or_create(user_id, alert_id)
        pref.snoozed_for_day = date.today()
        await self.session.commit()


