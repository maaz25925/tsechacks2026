from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, EmailStr, Field

from app.errors import http_error
from app.supabase_client import get_supabase, utc_now_iso

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    role: str = Field(pattern="^(student|teacher)$")
    name: str
    bio: str | None = None


class AuthResponse(BaseModel):
    user_id: str
    access_token: str | None = None
    role: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/register", response_model=AuthResponse)
def register(req: RegisterRequest) -> AuthResponse:
    """
    Simple Supabase Auth register + profile insert.

    Frontend: call this once, then store access_token and use it as Bearer token.
    """
    sb = get_supabase()
    try:
        res = sb.client.auth.sign_up({"email": req.email, "password": req.password})
    except Exception as exc:
        import traceback
        traceback.print_exc()  # Log full stack trace
        raise http_error(400, f"Registration failed: {str(exc)}", code="REGISTER_FAILED")

    user = getattr(res, "user", None)
    session = getattr(res, "session", None)
    if not user:
        raise http_error(400, "Registration failed: No user returned", code="REGISTER_FAILED")

    profile: dict[str, Any] = {
        "id": user.id,
        "email": req.email,
        "role": req.role,
        "name": req.name,
        "bio": req.bio,
        "wallet_address": None,
        "created_at": utc_now_iso(),
    }
    sb.upsert("users", profile, on_conflict="id")

    return AuthResponse(
        user_id=user.id,
        access_token=getattr(session, "access_token", None) if session else None,
        role=req.role,
    )


@router.post("/login", response_model=AuthResponse)
def login(req: LoginRequest) -> AuthResponse:
    """
    Supabase Auth login. Returns access_token + role from profile row.
    """
    sb = get_supabase()
    try:
        res = sb.client.auth.sign_in_with_password({"email": req.email, "password": req.password})
    except Exception as exc:
        import traceback
        traceback.print_exc()
        print(f"Login error: {str(exc)}")
        raise http_error(401, f"Login failed: {str(exc)}", code="LOGIN_FAILED")

    session = getattr(res, "session", None)
    user = getattr(res, "user", None)
    if not session or not user:
        raise http_error(401, "Invalid credentials or user not confirmed", code="LOGIN_FAILED")

    profile = sb.maybe_single("users", "*", id=user.id)
    role = (profile or {}).get("role") or "student"

    return AuthResponse(user_id=user.id, access_token=session.access_token, role=role)

