from pydantic import BaseModel
from typing import Optional


class TasksSummary(BaseModel):
    pending: int
    completed_today: int


class StudySummary(BaseModel):
    hours_today: float
    hours_this_week: float


class HabitsSummary(BaseModel):
    active: int
    completed_today: int


class AICoachSummary(BaseModel):
    latest_message: Optional[str] = None


class DashboardResponse(BaseModel):
    productivity_score: int
    tasks_completed_today: int
    study_hours_today: float
    habits_completed_today: int
    tasks: TasksSummary
    study: StudySummary
    habits: HabitsSummary
    ai_coach: AICoachSummary
