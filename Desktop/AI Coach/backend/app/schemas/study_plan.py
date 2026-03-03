import uuid
from datetime import datetime, date
from pydantic import BaseModel, ConfigDict


class StudyPlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    plan_text: str
    plan_date: date
    created_at: datetime
