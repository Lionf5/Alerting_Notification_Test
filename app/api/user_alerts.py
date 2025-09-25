from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, or_, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.models.alert import Alert, AlertTeamVisibility, AlertUserVisibility
from app.models.user import User
from app.models.user_alert_preference import ReadState, UserAlertPreference
from app.services.user_prefs_service import UserPreferenceService


router = APIRouter(prefix="/user/alerts", tags=["user-alerts"])


@router.get("", response_model=list[dict])
async def fetch_alerts(user_id: int = Query(...), session: AsyncSession = Depends(get_async_session)):
    # Fetch user for team context
    user = (await session.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    q = select(Alert).where(
        and_(
            Alert.archived.is_(False),
            or_(Alert.start_at.is_(None), Alert.start_at <= select(func.now())),
            or_(Alert.expire_at.is_(None), Alert.expire_at >= select(func.now())),
            or_(
                Alert.org_wide.is_(True),
                Alert.id.in_(select(AlertTeamVisibility.alert_id).where(AlertTeamVisibility.team_id == user.team_id)),
                Alert.id.in_(select(AlertUserVisibility.alert_id).where(AlertUserVisibility.user_id == user.id)),
            ),
        )
    )
    res = await session.execute(q)
    alerts = list(res.scalars().all())
    return [
        {
            "id": a.id,
            "title": a.title,
            "message": a.message,
            "severity": a.severity,
        }
        for a in alerts
    ]


@router.post("/{alert_id}/read")
async def mark_read(alert_id: int, user_id: int = Query(...), session: AsyncSession = Depends(get_async_session)):
    svc = UserPreferenceService(session)
    await svc.mark_read(user_id, alert_id)
    return {"status": "ok"}


@router.post("/{alert_id}/unread")
async def mark_unread(alert_id: int, user_id: int = Query(...), session: AsyncSession = Depends(get_async_session)):
    svc = UserPreferenceService(session)
    await svc.mark_unread(user_id, alert_id)
    return {"status": "ok"}


@router.post("/{alert_id}/snooze")
async def snooze(alert_id: int, user_id: int = Query(...), session: AsyncSession = Depends(get_async_session)):
    svc = UserPreferenceService(session)
    await svc.snooze_today(user_id, alert_id)
    return {"status": "ok"}


