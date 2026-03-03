import json
import uuid
from datetime import datetime, date, timedelta, timezone
from typing import Optional

import redis.asyncio as aioredis
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.config import settings
from app.core.logger import get_logger
from app.schemas.dashboard import (
    DashboardResponse,
    TasksSummary,
    StudySummary,
    HabitsSummary,
    AICoachSummary,
)

log = get_logger(__name__)

# Cache TTL: 60 seconds
CACHE_TTL = 60


def _cache_key(user_id: uuid.UUID) -> str:
    return f"dashboard:{user_id}"


# ─── Individual query helpers ─────────────────────────────────────────────────

def _get_tasks_summary(db: Session, user_id: uuid.UUID) -> TasksSummary:
    """Count pending and today-completed tasks."""
    try:
        today_start = datetime.combine(date.today(), datetime.min.time()).replace(
            tzinfo=timezone.utc
        )

        pending = db.execute(
            text(
                "SELECT COUNT(*) FROM tasks "
                "WHERE user_id = :uid AND is_completed = false"
            ),
            {"uid": str(user_id)},
        ).scalar() or 0

        completed_today = db.execute(
            text(
                "SELECT COUNT(*) FROM tasks "
                "WHERE user_id = :uid AND is_completed = true "
                "AND created_at >= :today"
            ),
            {"uid": str(user_id), "today": today_start},
        ).scalar() or 0

        return TasksSummary(pending=int(pending), completed_today=int(completed_today))
    except Exception:
        # Table doesn't exist yet (Phase 2 will create it)
        return TasksSummary(pending=0, completed_today=0)


def _get_study_summary(db: Session, user_id: uuid.UUID) -> StudySummary:
    """Sum study minutes for today and the current ISO week."""
    try:
        today = date.today()
        week_start = today - timedelta(days=today.weekday())  # Monday

        hours_today_raw = db.execute(
            text(
                "SELECT COALESCE(SUM(duration_minutes), 0) FROM study_sessions "
                "WHERE user_id = :uid AND session_date::date = :today"
            ),
            {"uid": str(user_id), "today": today},
        ).scalar() or 0

        hours_week_raw = db.execute(
            text(
                "SELECT COALESCE(SUM(duration_minutes), 0) FROM study_sessions "
                "WHERE user_id = :uid AND session_date::date >= :week_start"
            ),
            {"uid": str(user_id), "week_start": week_start},
        ).scalar() or 0

        def _to_hours(minutes: int) -> float:
            return int(minutes * 100 // 60) / 100.0

        return StudySummary(
            hours_today=_to_hours(int(hours_today_raw)),
            hours_this_week=_to_hours(int(hours_week_raw)),
        )
    except Exception:
        return StudySummary(hours_today=0.0, hours_this_week=0.0)


def _get_habits_summary(db: Session, user_id: uuid.UUID) -> HabitsSummary:
    """Count active habits and how many were logged completed today."""
    try:
        today = date.today()

        active = db.execute(
            text("SELECT COUNT(*) FROM habits WHERE user_id = :uid"),
            {"uid": str(user_id)},
        ).scalar() or 0

        completed_today = db.execute(
            text(
                "SELECT COUNT(*) FROM habit_logs hl "
                "JOIN habits h ON hl.habit_id = h.id "
                "WHERE h.user_id = :uid "
                "AND hl.log_date = :today "
                "AND hl.is_completed = true"
            ),
            {"uid": str(user_id), "today": today},
        ).scalar() or 0

        return HabitsSummary(active=int(active), completed_today=int(completed_today))
    except Exception:
        return HabitsSummary(active=0, completed_today=0)


def _get_ai_insight(db: Session, user_id: uuid.UUID) -> AICoachSummary:
    """Fetch the most recent AI coach insight for the user."""
    try:
        row = db.execute(
            text(
                "SELECT insight_text FROM ai_insights "
                "WHERE user_id = :uid "
                "ORDER BY created_at DESC LIMIT 1"
            ),
            {"uid": str(user_id)},
        ).fetchone()

        return AICoachSummary(latest_message=row[0] if row else None)
    except Exception:
        return AICoachSummary(latest_message=None)


def _calculate_productivity_score(
    tasks: TasksSummary,
    study: StudySummary,
    habits: HabitsSummary,
) -> int:
    """
    Weighted productivity score (0–100):
      - Tasks completed today : 40 pts max  (10 pts each, cap 4)
      - Study hours today      : 30 pts max  (10 pts/hr, cap 3h)
      - Habits completed today : 30 pts max  (10 pts each, cap 3)
    """
    task_score = min(tasks.completed_today * 10, 40)
    study_score = min(int(study.hours_today * 10), 30)
    habit_score = min(habits.completed_today * 10, 30)
    return task_score + study_score + habit_score


# ─── Main service function ────────────────────────────────────────────────────

async def get_dashboard(
    db: Session,
    user_id: uuid.UUID,
    redis: Optional[aioredis.Redis],
) -> DashboardResponse:
    """
    Return aggregated dashboard data for a user.
    Checks Redis cache first (60s TTL) before hitting the database.
    """
    cache_key = _cache_key(user_id)

    # ── 1. Try cache ──────────────────────────────────────────────────────────
    if redis:
        try:
            cached = await redis.get(cache_key)
            if cached:
                log.info(
                    "Dashboard cache hit for user_id={user_id}", user_id=user_id
                )
                return DashboardResponse(**json.loads(cached))
        except Exception as e:
            log.warning("Redis cache read failed: {error}", error=str(e))

    # ── 2. Compute from DB ────────────────────────────────────────────────────
    tasks = _get_tasks_summary(db, user_id)
    study = _get_study_summary(db, user_id)
    habits = _get_habits_summary(db, user_id)
    ai_coach = _get_ai_insight(db, user_id)
    score = _calculate_productivity_score(tasks, study, habits)

    response = DashboardResponse(
        productivity_score=score,
        tasks=tasks,
        study=study,
        habits=habits,
        ai_coach=ai_coach,
    )

    log.info("Dashboard generated for user_id={user_id}", user_id=user_id)

    # ── 3. Store in cache ─────────────────────────────────────────────────────
    if redis:
        try:
            await redis.setex(
                cache_key,
                CACHE_TTL,
                json.dumps(response.model_dump()),
            )
        except Exception as e:
            log.warning("Redis cache write failed: {error}", error=str(e))

    return response
