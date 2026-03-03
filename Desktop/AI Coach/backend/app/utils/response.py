from typing import Any, Optional
from fastapi.responses import JSONResponse


def success_response(
    data: Any,
    message: Optional[str] = None,
    status_code: int = 200,
) -> JSONResponse:
    """Return a standardised success envelope."""
    content: dict = {"success": True, "data": data}
    if message:
        content["message"] = message
    return JSONResponse(status_code=status_code, content=content)


def error_response(message: str, status_code: int) -> JSONResponse:
    """Return a standardised error envelope."""
    return JSONResponse(
        status_code=status_code,
        content={"success": False, "error": message, "status_code": status_code},
    )
