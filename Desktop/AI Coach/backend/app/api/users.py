from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import UserPublic
from app.services.auth_service import auth_service

router = APIRouter(prefix="/users", tags=["Users"])
security = HTTPBearer()


@router.get("/me", response_model=UserPublic)
def get_me(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Get the currently authenticated user's profile."""
    token = credentials.credentials
    user = auth_service.get_current_user(db, token)
    return user
