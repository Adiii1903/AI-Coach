from typing import Any, Optional
from pydantic import BaseModel


class SuccessResponse(BaseModel):
    success: bool = True
    data: Any
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    status_code: int
