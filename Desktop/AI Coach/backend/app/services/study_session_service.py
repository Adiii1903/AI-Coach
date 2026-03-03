from datetime import date, timedelta
from typing import List
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.study_session import StudySession
from app.services.base_service import BaseService
from app.core.logger import get_logger

log = get_logger(__name__)


class StudySessionService(BaseService[StudySession]):
    model = StudySession

    def get_user_sessions(self, db: Session, user_id: UUID) -> List[StudySession]:
        """Return all study sessions for a user, newest first."""
        stmt = (
            select(StudySession)
            .where(StudySession.user_id == user_id)
            .order_by(StudySession.created_at.desc())
        )
        return list(db.scalars(stmt).all())

    # ─── Aggregation Methods ──────────────────────────────────────────────────

    def get_total_study_time(self, db: Session, user_id: UUID) -> int:
        """Return total minutes studied by the user across all time."""
        stmt = select(func.sum(StudySession.duration_minutes)).where(
            StudySession.user_id == user_id
        )
        result = db.scalar(stmt)
        return int(result) if result else 0

    def get_today_study_time(self, db: Session, user_id: UUID) -> int:
        """Return total minutes studied by the user exactly today."""
        today = date.today()
        stmt = select(func.sum(StudySession.duration_minutes)).where(
            StudySession.user_id == user_id,
            StudySession.session_date == today,
        )
        result = db.scalar(stmt)
        return int(result) if result else 0

    def get_weekly_study_time(self, db: Session, user_id: UUID) -> int:
        """Return total minutes studied by the user in the last 7 days (including today)."""
        seven_days_ago = date.today() - timedelta(days=7)
        stmt = select(func.sum(StudySession.duration_minutes)).where(
            StudySession.user_id == user_id,
            StudySession.session_date >= seven_days_ago,
        )
        result = db.scalar(stmt)
        return int(result) if result else 0


study_session_service = StudySessionService()
