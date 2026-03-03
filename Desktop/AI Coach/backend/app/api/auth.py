from fastapi import APIRouter, Depends, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import (
    SignupRequest,
    LoginRequest,
    TokenResponse,
    RefreshRequest,
    AccessTokenResponse,
    MessageResponse,
)
from app.services.auth_service import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


def optional_rate_limiter(times: int, seconds: int):
    """Returns a RateLimiter dependency only when Redis is available, else a no-op."""
    async def _no_op(request: Request):
        pass  # Redis not available — rate limiting skipped

    try:
        # FastAPILimiter.redis is set only after a successful .init()
        if FastAPILimiter.redis is None:
            return _no_op
    except Exception:
        return _no_op

    return RateLimiter(times=times, seconds=seconds)


@router.post(
    "/signup",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(optional_rate_limiter(times=5, seconds=60))],
)
def signup(data: SignupRequest, db: Session = Depends(get_db)):
    """Register a new student account. Rate limited to 5 requests/minute per IP (when Redis is available)."""
    auth_service.signup(db, data)
    return MessageResponse(message="Account created successfully. Please log in.")


@router.post(
    "/login",
    response_model=TokenResponse,
    dependencies=[Depends(optional_rate_limiter(times=5, seconds=60))],
)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate and receive access + refresh tokens. Rate limited to 5 requests/minute per IP (when Redis is available)."""
    return auth_service.login(db, data)


@router.post(
    "/refresh",
    response_model=AccessTokenResponse,
    dependencies=[Depends(optional_rate_limiter(times=10, seconds=60))],
)
def refresh_token(data: RefreshRequest, db: Session = Depends(get_db)):
    """Exchange a valid refresh token for a new access token. Rate limited to 10 requests/minute (when Redis is available)."""
    new_access_token = auth_service.refresh_access_token(db, data.refresh_token)
    return AccessTokenResponse(access_token=new_access_token)
