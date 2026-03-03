from typing import Optional

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.services.auth_service import auth_service
from app.services import dashboard_service
from app.utils.response import success_response

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
security = HTTPBearer()


async def get_redis() -> Optional[aioredis.Redis]:
    """Dependency that provides a Redis client, or None if unavailable."""
    try:
        client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
        return client
    except Exception:
        return None


@router.get("", response_class=JSONResponse)
async def get_dashboard(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
    redis: Optional[aioredis.Redis] = Depends(get_redis),
):
    """
    Aggregated dashboard endpoint.

    Returns productivity score, task summary, study hours,
    habit progress and the latest AI coach message for the
    authenticated user. Results are cached in Redis for 60 seconds.

    Response shape:
        {"success": true, "data": { ...dashboard fields... }}
    """
    user = auth_service.get_current_user(db, credentials.credentials)
    data = await dashboard_service.get_dashboard(db, user.id, redis)
    return success_response(data.model_dump())
