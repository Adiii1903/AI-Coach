from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.study_plan import StudyPlanResponse
from app.services.auth_service import auth_service
from app.services.study_planner_service import study_planner_service
from app.utils.response import success_response

router = APIRouter(prefix="/study-plan", tags=["Study Plan"])
security = HTTPBearer()


@router.post("/generate", status_code=status.HTTP_201_CREATED)
def generate_study_plan(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Generate today's structured AI study plan."""
    current_user = auth_service.get_current_user(db, credentials.credentials)
    plan = study_planner_service.generate_study_plan(db, current_user.id)
    
    return success_response(
        StudyPlanResponse.model_validate(plan).model_dump(mode="json"),
        message="Study plan generated successfully.",
        status_code=status.HTTP_201_CREATED,
    )


@router.get("/today")
def get_today_plan(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Return today's study plan if one is generated."""
    current_user = auth_service.get_current_user(db, credentials.credentials)
    plan = study_planner_service.get_today_plan(db, current_user.id)
    
    if not plan:
        return success_response(None, message="No study plan generated for today yet.")
        
    return success_response(
        StudyPlanResponse.model_validate(plan).model_dump(mode="json")
    )


@router.get("/history")
def get_plan_history(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Return the last 5 historic study plans for the user."""
    current_user = auth_service.get_current_user(db, credentials.credentials)
    plans = study_planner_service.get_plan_history(db, current_user.id, limit=5)
    
    return success_response(
        [StudyPlanResponse.model_validate(p).model_dump(mode="json") for p in plans]
    )
