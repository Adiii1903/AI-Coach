from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.ai_coach import AIInsightResponse
from app.services.auth_service import auth_service
from app.services.ai_coach_service import ai_coach_service
from app.utils.response import success_response

router = APIRouter(prefix="/ai-coach", tags=["AI Coach"])
security = HTTPBearer()


@router.post("/generate", status_code=status.HTTP_201_CREATED)
def generate_ai_insight(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Generate a new AI insight based on today's productivity and save it."""
    current_user = auth_service.get_current_user(db, credentials.credentials)
    insight = ai_coach_service.generate_ai_advice(db, current_user.id)
    return success_response(
        AIInsightResponse.model_validate(insight).model_dump(mode="json"),
        message="AI insight generated successfully.",
        status_code=status.HTTP_201_CREATED,
    )


@router.get("/advice")
def get_latest_advice(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Return the latest AI insight for the user."""
    current_user = auth_service.get_current_user(db, credentials.credentials)
    insight = ai_coach_service.get_latest_advice(db, current_user.id)
    
    if not insight:
        return success_response(None, message="No insights found. Try generating one.")
        
    return success_response(
        AIInsightResponse.model_validate(insight).model_dump(mode="json")
    )


@router.get("/history")
def get_advice_history(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Return the last 5 insights for the user."""
    current_user = auth_service.get_current_user(db, credentials.credentials)
    insights = ai_coach_service.get_advice_history(db, current_user.id, limit=5)
    
    return success_response(
        [AIInsightResponse.model_validate(i).model_dump(mode="json") for i in insights]
    )
