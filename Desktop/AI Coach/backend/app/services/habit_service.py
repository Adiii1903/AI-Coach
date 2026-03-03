from datetime import date, timedelta
from typing import List
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.habit import Habit
from app.models.habit_log import HabitLog
from app.services.base_service import BaseService
from app.core.logger import get_logger

log = get_logger(__name__)


class HabitService(BaseService[Habit]):
    model = Habit

    # ─── Habit-specific queries ───────────────────────────────────────────────

    def get_user_habits(self, db: Session, user_id: UUID) -> List[Habit]:
        """Return all habits for a user, newest first."""
        stmt = (
            select(Habit)
            .where(Habit.user_id == user_id)
            .order_by(Habit.created_at.desc())
        )
        return list(db.scalars(stmt).all())

    # ─── Logging / Streak Logic ───────────────────────────────────────────────

    def log_habit(self, db: Session, habit_id: UUID, user_id: UUID) -> Habit:
        """
        Log today's completion for a habit, enforcing ownership, 
        preventing duplicate daily logs, and calculating streak logic.
        """
        # 1. Fetch and verify ownership
        habit = self.get_by_id(db, habit_id)
        if habit.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to modify this habit.",
            )

        today = date.today()
        yesterday = today - timedelta(days=1)

        # 2. Check if already logged today
        existing_log = db.scalar(
            select(HabitLog).where(
                HabitLog.habit_id == habit_id,
                HabitLog.log_date == today,
            )
        )
        if existing_log:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Habit already logged for today.",
            )

        # 3. Check yesterday's log to determine streak continuity
        yesterday_log = db.scalar(
            select(HabitLog).where(
                HabitLog.habit_id == habit_id,
                HabitLog.log_date == yesterday,
                HabitLog.is_completed == True,  # noqa: E712
            )
        )

        if yesterday_log:
            habit.current_streak += 1
        else:
            # Streak broken (or first time logging)
            habit.current_streak = 1

        habit.longest_streak = max(habit.longest_streak, habit.current_streak)

        # 4. Create new log
        new_log = HabitLog(
            habit_id=habit_id,
            log_date=today,
            is_completed=True,
        )
        db.add(new_log)

        try:
            db.commit()
            db.refresh(habit)
            log.info("Habit logged correctly: id={habit_id} date={date}", habit_id=habit_id, date=today)
            return habit
        except IntegrityError:
            db.rollback()
            log.warning("Concurrent duplicate habit log detected for id={habit_id}", habit_id=habit_id)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Habit already logged for today.",
            )


habit_service = HabitService()
