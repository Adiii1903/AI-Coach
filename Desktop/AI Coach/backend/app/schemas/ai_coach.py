import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


# ─── Response Schemas ─────────────────────────────────────────────────────────

class AIInsightResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    insight_text: str
    insight_type: str
    created_at: datetime
