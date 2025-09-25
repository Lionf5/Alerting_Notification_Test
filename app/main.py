from fastapi import FastAPI

from app.core.config import settings
from app.api.admin_alerts import router as admin_alerts_router
from app.api.user_alerts import router as user_alerts_router
from app.api.ops import router as ops_router
from app.api.analytics import router as analytics_router


app = FastAPI(title=settings.app_name)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}

app.include_router(admin_alerts_router, prefix=settings.api_prefix)
app.include_router(user_alerts_router, prefix=settings.api_prefix)
app.include_router(ops_router, prefix=settings.api_prefix)
app.include_router(analytics_router, prefix=settings.api_prefix)


