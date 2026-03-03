import uuid
from typing import Optional
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.study_session import (
    StudySessionCreate,
    StudySessionUpdate,
    StudySessionResponse,
)
from app.services.auth_service import auth_service
from app.services.study_session_service import study_session_service
from app.utils.response import success_response

router = APIRouter(prefix="/study-sessions", tags=["Study Sessions"])
security = HTTPBearer()


# ─── Helper: Resolve & authorise study session ────────────────────────────────

def _get_owned_session(session_id: uuid.UUID, current_user_id: uuid.UUID, db: Session):
    """Fetch study session by id and raise 403 if it doesn't belong to current_user."""
    session_obj = study_session_service.get_by_id(db, session_id)  # raises 404 if not found
    if session_obj.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this study session.",
        )
    return session_obj


# ─── Routes ───────────────────────────────────────────────────────────────────

@router.get("")
def get_study_sessions(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Return all study sessions for the authenticated user."""
    current_user = auth_service.get_current_user(db, credentials.credentials)
    sessions = study_session_service.get_user_sessions(db, current_user.id)
    return success_response(
        [StudySessionResponse.model_validate(s).model_dump(mode="json") for s in sessions]
    )


@router.get("/stats")
def get_study_stats(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Return aggregated productivity statistics for the authenticated user."""
    current_user = auth_service.get_current_user(db, credentials.credentials)
    
    total = study_session_service.get_total_study_time(db, current_user.id)
    today = study_session_service.get_today_study_time(db, current_user.id)
    weekly = study_session_service.get_weekly_study_time(db, current_user.id)
    
    return success_response({
        "total_minutes": total,
        "today_minutes": today,
        "weekly_minutes": weekly,
    })


@router.post("", status_code=status.HTTP_201_CREATED)
def create_study_session(
    data: StudySessionCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Create a new study session for the authenticated user."""
    current_user = auth_service.get_current_user(db, credentials.credentials)
    
    create_data = {
        "user_id": current_user.id,
        "subject": data.subject,
        "topic": data.topic,
        "duration_minutes": data.duration_minutes,
        "notes": data.notes,
    }
    if data.session_date:
        create_data["session_date"] = data.session_date
        
    session_obj = study_session_service.create(db, create_data)
    
    return success_response(
        StudySessionResponse.model_validate(session_obj).model_dump(mode="json"),
        message="Study session created successfully.",
        status_code=status.HTTP_201_CREATED,
    )


@router.put("/{session_id}")
def update_study_session(
    session_id: uuid.UUID,
    data: StudySessionUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Update a study session (must be the owner)."""
    current_user = auth_service.get_current_user(db, credentials.credentials)
    _get_owned_session(session_id, current_user.id, db)

    updates = data.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided to update.",
        )

    updated_session = study_session_service.update(db, session_id, updates)
    return success_response(
        StudySessionResponse.model_validate(updated_session).model_dump(mode="json"),
        message="Study session updated successfully.",
    )


@router.delete("/{session_id}")
def delete_study_session(
    session_id: uuid.UUID,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Delete a study session (must be the owner)."""
    current_user = auth_service.get_current_user(db, credentials.credentials)
    _get_owned_session(session_id, current_user.id, db)
    
    study_session_service.delete(db, session_id)
    return success_response(None, message="Study session deleted successfully.")
