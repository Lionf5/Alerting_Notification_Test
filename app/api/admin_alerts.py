from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.schemas.alert import AlertCreate, AlertRead, AlertUpdate
from app.services.alert_service import AlertService


router = APIRouter(prefix="/admin/alerts", tags=["admin-alerts"])


@router.post("", response_model=AlertRead)
async def create_alert(payload: AlertCreate, session: AsyncSession = Depends(get_async_session)):
    service = AlertService(session)
    alert = await service.create_alert(payload)
    return alert


@router.put("/{alert_id}", response_model=AlertRead)
async def update_alert(alert_id: int, payload: AlertUpdate, session: AsyncSession = Depends(get_async_session)):
    service = AlertService(session)
    alert = await service.update_alert(alert_id, payload)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.get("", response_model=list[AlertRead])
async def list_alerts(session: AsyncSession = Depends(get_async_session)):
    service = AlertService(session)
    alerts = await service.list_alerts()
    return list(alerts)


