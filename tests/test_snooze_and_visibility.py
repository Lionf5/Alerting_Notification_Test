from __future__ import annotations

import pytest
from datetime import date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db.base import Base
from app.models.alert import Alert, AlertTeamVisibility, AlertUserVisibility, Severity
from app.models.user import Team, User
from app.services.reminder_service import ReminderService
from app.services.user_prefs_service import UserPreferenceService


@pytest.mark.asyncio
async def test_team_and_user_visibility_and_snooze():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    Session = async_sessionmaker(engine, expire_on_commit=False)

    async with Session() as session:
        eng = Team(name="Engineering")
        mkt = Team(name="Marketing")
        session.add_all([eng, mkt])
        await session.flush()
        alice = User(name="Alice", team_id=eng.id)
        bob = User(name="Bob", team_id=mkt.id)
        session.add_all([alice, bob])
        await session.flush()

        alert_team = Alert(
            title="Team Alert",
            message="Eng only",
            severity=Severity.info,
            org_wide=False,
            remind_every_minutes=1,
            reminders_enabled=True,
        )
        session.add(alert_team)
        await session.flush()
        session.add(AlertTeamVisibility(alert_id=alert_team.id, team_id=eng.id))

        alert_user = Alert(
            title="User Alert",
            message="Alice only",
            severity=Severity.info,
            org_wide=False,
            remind_every_minutes=1,
            reminders_enabled=True,
        )
        session.add(alert_user)
        await session.flush()
        session.add(AlertUserVisibility(alert_id=alert_user.id, user_id=alice.id))

        await session.commit()

    async with Session() as session:
        svc = ReminderService(session)
        sent = await svc.trigger_due_reminders()
        assert sent == 2

        # Snooze team alert for Alice via service
        pref_svc = UserPreferenceService(session)
        await pref_svc.snooze_today(user_id=alice.id, alert_id=alert_team.id)
        sent2 = await svc.trigger_due_reminders()
        assert sent2 == 0  # immediate re-trigger blocked by frequency and snooze


