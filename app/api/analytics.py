from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.models.alert import Alert
from app.models.notification import NotificationDelivery
from app.models.user_alert_preference import UserAlertPreference, ReadState


router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary")
async def summary(session: AsyncSession = Depends(get_async_session)):
    total_alerts = (await session.execute(select(func.count(Alert.id)))).scalar_one()
    delivered = (await session.execute(select(func.count(NotificationDelivery.id)))).scalar_one()
    read = (
        await session.execute(
            select(func.count(UserAlertPreference.id)).where(UserAlertPreference.read_state == ReadState.read)
        )
    ).scalar_one()
    unread = (
        await session.execute(
            select(func.count(UserAlertPreference.id)).where(UserAlertPreference.read_state == ReadState.unread)
        )
    ).scalar_one()

    by_severity = (
        await session.execute(
            select(Alert.severity, func.count(Alert.id)).group_by(Alert.severity)
        )
    ).all()

    return {
        "total_alerts": total_alerts,
        "delivered": delivered,
        "read": read,
        "unread": unread,
        "by_severity": {str(k): v for k, v in by_severity},
    }


