from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.channels.base import CHANNELS
from app.models.alert import Alert, AlertTeamVisibility, AlertUserVisibility
from app.models.user import User
from app.models.user_alert_preference import UserAlertPreference


class ReminderService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def trigger_due_reminders(self) -> int:
        now = datetime.now(timezone.utc)
        today = date.today()

        # Alerts that are active and have reminders enabled
        alerts_stmt = select(Alert).where(
            and_(
                Alert.reminders_enabled.is_(True),
                Alert.archived.is_(False),
                or_(Alert.start_at.is_(None), Alert.start_at <= now),
                or_(Alert.expire_at.is_(None), Alert.expire_at >= now),
            )
        )
        alerts = list((await self.session.execute(alerts_stmt)).scalars().all())

        sent = 0
        for alert in alerts:
            # audience: org, teams, users
            user_ids_stmt = select(User.id)
            if alert.org_wide:
                pass
            else:
                user_ids_stmt = user_ids_stmt.where(
                    or_(
                        User.id.in_(select(AlertUserVisibility.user_id).where(AlertUserVisibility.alert_id == alert.id)),
                        User.team_id.in_(select(AlertTeamVisibility.team_id).where(AlertTeamVisibility.alert_id == alert.id)),
                    )
                )
            user_ids = [uid for (uid,) in (await self.session.execute(user_ids_stmt)).all()]

            channel = CHANNELS.get(alert.delivery_type)
            if not channel:
                continue

            for uid in user_ids:
                pref_stmt = select(UserAlertPreference).where(
                    and_(UserAlertPreference.user_id == uid, UserAlertPreference.alert_id == alert.id)
                )
                pref = (await self.session.execute(pref_stmt)).scalars().first()

                # Create default preference if none
                if not pref:
                    pref = UserAlertPreference(user_id=uid, alert_id=alert.id)
                    self.session.add(pref)
                    await self.session.flush()

                # Skip if snoozed today
                if pref.snoozed_for_day == today:
                    continue

                prev = pref.last_reminded_at
                if prev is not None and prev.tzinfo is None:
                    prev = prev.replace(tzinfo=timezone.utc)

                # due if never reminded or remind_every_minutes passed
                due = prev is None or (now - prev) >= timedelta(minutes=alert.remind_every_minutes)
                if not due:
                    continue

                await channel.send(self.session, alert=alert, user_id=uid)
                pref.last_reminded_at = now
                sent += 1

        await self.session.commit()
        return sent


