import uuid
from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel, ConfigDict


# ─── Request Schemas ──────────────────────────────────────────────────────────

class HabitCreate(BaseModel):
    name: str
    description: Optional[str] = None
    target_frequency: Optional[str] = "daily"


class HabitUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    target_frequency: Optional[str] = None


# ─── Response Schemas ─────────────────────────────────────────────────────────

class HabitResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: Optional[str] = None
    target_frequency: str
    current_streak: int
    longest_streak: int
    created_at: datetime


class HabitLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    habit_id: uuid.UUID
    log_date: date
    is_completed: bool
