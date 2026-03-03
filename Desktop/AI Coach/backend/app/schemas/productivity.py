from pydantic import BaseModel, ConfigDict

class ProductivityScoreResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    productivity_score: int
    tasks_completed_today: int
    study_hours_today: float
    habits_completed_today: int
