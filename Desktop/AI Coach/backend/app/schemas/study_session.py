import uuid
from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel, ConfigDict


# ─── Request Schemas ──────────────────────────────────────────────────────────

class StudySessionCreate(BaseModel):
    subject: str
    topic: Optional[str] = None
    duration_minutes: int
    session_date: Optional[date] = None
    notes: Optional[str] = None


class StudySessionUpdate(BaseModel):
    subject: Optional[str] = None
    topic: Optional[str] = None
    duration_minutes: Optional[int] = None
    session_date: Optional[date] = None
    notes: Optional[str] = None


# ─── Response Schemas ─────────────────────────────────────────────────────────

class StudySessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    subject: str
    topic: Optional[str] = None
    duration_minutes: int
    session_date: date
    notes: Optional[str] = None
    created_at: datetime
