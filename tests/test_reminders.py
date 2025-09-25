from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.db.base import Base
from app.models.alert import Alert, Severity
from app.models.notification import NotificationDelivery
from app.models.user import Team, User
from app.services.reminder_service import ReminderService


@pytest.mark.asyncio
async def test_reminder_sends_and_respects_frequency(tmp_path):
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    Session = async_sessionmaker(engine, expire_on_commit=False)

    async with Session() as session:
        eng = Team(name="Engineering")
        user = User(name="A", team_id=None)
        session.add_all([eng, user])
        await session.flush()

        alert = Alert(
            title="Test",
            message="Hi",
            severity=Severity.info,
            org_wide=True,
            remind_every_minutes=120,
            reminders_enabled=True,
        )
        session.add(alert)
        await session.commit()

    async with Session() as session:
        svc = ReminderService(session)
        sent1 = await svc.trigger_due_reminders()
        assert sent1 == 1

        # immediately trigger again; should be zero due to frequency
        sent2 = await svc.trigger_due_reminders()
        assert sent2 == 0

        # verify a delivery exists
        deliveries = (await session.execute(
            NotificationDelivery.__table__.select()
        )).all()
        assert len(deliveries) == 1


