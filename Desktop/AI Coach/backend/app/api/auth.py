from fastapi import APIRouter, Depends, Request, Response, status
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
    """
    Returns an async dependency that applies rate limiting only when Redis is
    available.  The Redis check is deferred to *request time* (not import/decoration
    time) so that it correctly reflects the lifespan-initialised state.
    """
    rate_limiter = RateLimiter(times=times, seconds=seconds)

    async def _dependency(request: Request):
        try:
            # FastAPILimiter.redis is None until lifespan calls FastAPILimiter.init()
            if FastAPILimiter.redis is None:
                return  # Redis not available — skip rate limiting gracefully
        except Exception:
            return
        await rate_limiter(request)  # delegate to the real limiter

    return _dependency


@router.post(
    "/signup",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(optional_rate_limiter(times=5, seconds=60))],
)
def signup(data: SignupRequest, response: Response, db: Session = Depends(get_db)) -> MessageResponse:
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
