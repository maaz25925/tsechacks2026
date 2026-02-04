from __future__ import annotations

from typing import Annotated, Any

from fastapi import Depends, Header

from app.errors import http_error
from app.supabase_client import get_supabase


async def get_current_user(
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> dict[str, Any]:
    """
    Simple Supabase Auth JWT validator.

    Frontend should send:
      Authorization: Bearer <access_token>
    """
    if not authorization:
        raise http_error(401, "Missing Authorization header", code="UNAUTHENTICATED")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise http_error(401, "Invalid Authorization header", code="UNAUTHENTICATED")

    token = parts[1]
    sb = get_supabase()
    try:
        res = sb.client.auth.get_user(jwt=token)
    except Exception:
        raise http_error(401, "Invalid or expired token", code="UNAUTHENTICATED")
    if not res or not getattr(res, "user", None):
        raise http_error(401, "Invalid or expired token", code="UNAUTHENTICATED")

    user_id = res.user.id
    row = sb.maybe_single("users", "*", id=user_id)
    if not row:
        # Allow auth user without profile row
        row = {"id": user_id, "email": res.user.email, "role": "student"}
    return row


async def require_student(user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    if user.get("role") != "student":
        raise http_error(403, "Student role required", code="FORBIDDEN")
    return user


async def require_teacher(user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    if user.get("role") != "teacher":
        raise http_error(403, "Teacher role required", code="FORBIDDEN")
    return user

