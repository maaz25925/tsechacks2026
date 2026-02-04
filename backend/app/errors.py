from __future__ import annotations

from fastapi import HTTPException


def http_error(status_code: int, message: str, *, code: str | None = None) -> HTTPException:
    """
    Consistent JSON error shape for frontend:
    {
      "error": { "message": "...", "code": "..." }
    }
    """
    detail = {"error": {"message": message}}
    if code:
        detail["error"]["code"] = code
    return HTTPException(status_code=status_code, detail=detail)

