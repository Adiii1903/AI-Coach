from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.auth_service import auth_service
from app.services.productivity_service import productivity_service
from app.utils.response import success_response
from app.schemas.productivity import ProductivityScoreResponse

router = APIRouter(prefix="/productivity", tags=["Productivity"])
security = HTTPBearer()


@router.get("/score")
def get_productivity_score(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Return the calculated 0-100 productivity score for today based on tasks, study time, and habits."""
    current_user = auth_service.get_current_user(db, credentials.credentials)
    
    score_data = productivity_service.calculate_productivity_score(db, current_user.id)
    
    return success_response(
        ProductivityScoreResponse.model_validate(score_data).model_dump(mode="json"),
        message="Productivity score calculated successfully."
    )
