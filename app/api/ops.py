from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.services.reminder_service import ReminderService


router = APIRouter(prefix="/ops", tags=["ops"])


@router.post("/trigger-reminders")
async def trigger_reminders(session: AsyncSession = Depends(get_async_session)):
    svc = ReminderService(session)
    count = await svc.trigger_due_reminders()
    return {"sent": count}


