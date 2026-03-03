from datetime import date, datetime, timezone
from uuid import UUID

from sqlalchemy import select, func, text
from sqlalchemy.orm import Session

from app.models.task import Task
from app.models.habit import Habit
from app.models.habit_log import HabitLog
from app.models.study_session import StudySession
from app.core.logger import get_logger

log = get_logger(__name__)


class ProductivityService:
    # ─── Data Gathering Queries (using aggregations) ──────────────────────────

    def get_tasks_completed_today(self, db: Session, user_id: UUID) -> int:
        """Return the number of tasks completed today by the user."""
        today_start = datetime.combine(date.today(), datetime.min.time()).replace(
            tzinfo=timezone.utc
        )
        stmt = select(func.count()).where(
            Task.user_id == user_id,
            Task.is_completed == True,  # noqa: E712
            Task.created_at >= today_start,
        )
        result = db.scalar(stmt)
        return int(result) if result else 0

    def get_habits_completed_today(self, db: Session, user_id: UUID) -> int:
        """Return the number of habits logged as completed today by the user."""
        today = date.today()
        stmt = (
            select(func.count())
            .select_from(HabitLog)
            .join(Habit, HabitLog.habit_id == Habit.id)
            .where(
                Habit.user_id == user_id,
                HabitLog.log_date == today,
                HabitLog.is_completed == True,  # noqa: E712
            )
        )
        result = db.scalar(stmt)
        return int(result) if result else 0

    def get_study_hours_today(self, db: Session, user_id: UUID) -> float:
        """Return the hours studied today by the user (minutes / 60.0)."""
        today = date.today()
        stmt = select(func.sum(StudySession.duration_minutes)).where(
            StudySession.user_id == user_id,
            StudySession.session_date == today,
        )
        result = db.scalar(stmt)
        minutes = int(result) if result else 0
        return round(minutes / 60.0, 2)

    # ─── Scoring Engine ───────────────────────────────────────────────────────

    def calculate_productivity_score(self, db: Session, user_id: UUID) -> dict:
        """
        Calculate daily productivity score.
        - Tasks: 10 points each (max 40)
        - Study: 10 points per hour (max 30)
        - Habits: 10 points each (max 30)
        Returns the score and component metrics.
        """
        tasks = self.get_tasks_completed_today(db, user_id)
        habits = self.get_habits_completed_today(db, user_id)
        study_hours = self.get_study_hours_today(db, user_id)

        task_score = min(tasks * 10, 40)
        study_score = min(int(study_hours * 10), 30)
        habit_score = min(habits * 10, 30)

        score = min(task_score + study_score + habit_score, 100)

        return {
            "productivity_score": score,
            "tasks_completed_today": tasks,
            "study_hours_today": study_hours,
            "habits_completed_today": habits,
        }


productivity_service = ProductivityService()
