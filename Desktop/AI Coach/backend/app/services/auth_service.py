from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.user import User, RefreshToken
from app.schemas.auth import SignupRequest, LoginRequest, TokenResponse
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.config import settings
from app.core.logger import get_logger
from fastapi import HTTPException, status

log = get_logger(__name__)


class AuthService:
    def signup(self, db: Session, data: SignupRequest) -> User:
        # Check if email already exists
        existing = db.scalar(select(User).where(User.email == data.email))
        if existing:
            log.warning("Signup failed — email already exists: {email}", email=data.email)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An account with this email already exists.",
            )

        user = User(
            email=data.email,
            name=data.name,
            password_hash=get_password_hash(data.password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        log.info("User signup successful: {email}", email=data.email)
        return user

    def login(self, db: Session, data: LoginRequest) -> TokenResponse:
        user = db.scalar(select(User).where(User.email == data.email))
        if not user or not verify_password(data.password, user.password_hash):
            log.warning("Login failed — invalid credentials: {email}", email=data.email)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
            )

        # Update last_active
        user.last_active = datetime.now(timezone.utc)
        db.commit()

        # Generate tokens
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token_str = create_refresh_token(data={"sub": str(user.id)})

        # Persist refresh token
        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
        rt = RefreshToken(
            user_id=user.id,
            token=refresh_token_str,
            expires_at=expires_at,
        )
        db.add(rt)
        db.commit()

        log.info("User login successful: {email}", email=data.email)
        return TokenResponse(access_token=access_token, refresh_token=refresh_token_str)

    def refresh_access_token(self, db: Session, refresh_token: str) -> str:
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            log.warning("Token refresh failed — invalid or expired token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token.",
            )

        # Verify token exists in DB and is not revoked
        rt = db.scalar(
            select(RefreshToken).where(
                RefreshToken.token == refresh_token,
                RefreshToken.is_revoked == False,
            )
        )
        if not rt:
            log.warning("Token refresh failed — token revoked or not found")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has been revoked or does not exist.",
            )

        # Check expiry
        if rt.expires_at < datetime.now(timezone.utc):
            log.warning("Token refresh failed — token expired for user_id={user_id}", user_id=rt.user_id)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired.",
            )

        new_access_token = create_access_token(data={"sub": payload["sub"]})
        log.info("Access token refreshed for user_id={user_id}", user_id=payload["sub"])
        return new_access_token

    def get_current_user(self, db: Session, token: str) -> User:
        payload = decode_token(token)
        if not payload or payload.get("type") != "access":
            log.warning("Authentication failed — invalid access token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = payload.get("sub")
        user = db.scalar(select(User).where(User.id == user_id))
        if not user:
            log.warning("Authentication failed — user not found: user_id={user_id}", user_id=user_id)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found.",
            )
        return user


auth_service = AuthService()
