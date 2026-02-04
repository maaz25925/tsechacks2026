from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter

from app.errors import http_error
from app.schemas import UserCreateRequest, UserListResponse, UserResponse, UserUpdateRequest
from app.supabase_client import get_supabase, utc_now_iso

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse)
def create_user(req: UserCreateRequest) -> UserResponse:
    """
    Create a new user (student or teacher).
    Note: Password handling should integrate with Supabase Auth.
    """
    sb = get_supabase()

    # Check if user already exists
    existing = sb.maybe_single("users", "*", email=req.email)
    if existing:
        raise http_error(409, "User with this email already exists", code="EMAIL_EXISTS")

    user_id = f"user_{uuid4().hex}"
    user_row = {
        "id": user_id,
        "email": req.email,
        "name": req.name,
        "role": req.role,
        "bio": req.bio or None,
        "wallet_address": None,
        "created_at": utc_now_iso(),
    }

    try:
        sb.insert("users", user_row)
    except Exception as e:
        raise http_error(400, f"Failed to create user: {str(e)}", code="CREATE_FAILED")

    return UserResponse(
        id=user_id,
        email=req.email,
        name=req.name,
        role=req.role,
        bio=req.bio,
        wallet_address=None,
        created_at=user_row["created_at"],
    )


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: str) -> UserResponse:
    """
    Retrieve a user by ID.
    """
    sb = get_supabase()
    user = sb.maybe_single("users", "*", id=user_id)
    if not user:
        raise http_error(404, "User not found", code="USER_NOT_FOUND")

    return UserResponse(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        role=user["role"],
        bio=user.get("bio"),
        wallet_address=user.get("wallet_address"),
        created_at=user.get("created_at"),
    )


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: str, req: UserUpdateRequest) -> UserResponse:
    """
    Update a user's profile (name, bio).
    """
    sb = get_supabase()
    user = sb.maybe_single("users", "*", id=user_id)
    if not user:
        raise http_error(404, "User not found", code="USER_NOT_FOUND")

    update_data = {}
    if req.name is not None:
        update_data["name"] = req.name
    if req.bio is not None:
        update_data["bio"] = req.bio

    if update_data:
        try:
            sb.update("users", update_data, id=user_id)
        except Exception as e:
            raise http_error(400, f"Failed to update user: {str(e)}", code="UPDATE_FAILED")

    # Fetch updated user
    updated_user = sb.maybe_single("users", "*", id=user_id)
    return UserResponse(
        id=updated_user["id"],
        email=updated_user["email"],
        name=updated_user["name"],
        role=updated_user["role"],
        bio=updated_user.get("bio"),
        wallet_address=updated_user.get("wallet_address"),
        created_at=updated_user.get("created_at"),
    )


@router.delete("/{user_id}")
def delete_user(user_id: str) -> dict:
    """
    Delete a user by ID.
    """
    sb = get_supabase()
    user = sb.maybe_single("users", "*", id=user_id)
    if not user:
        raise http_error(404, "User not found", code="USER_NOT_FOUND")

    try:
        sb.delete("users", id=user_id)
    except Exception as e:
        raise http_error(400, f"Failed to delete user: {str(e)}", code="DELETE_FAILED")

    return {"message": "User deleted successfully", "user_id": user_id}


@router.get("", response_model=UserListResponse)
def list_users(role: str | None = None, limit: int = 50, offset: int = 0) -> UserListResponse:
    """
    List users with optional role filter.
    """
    sb = get_supabase()

    query = sb.client.table("users").select("*", count="exact")
    if role:
        query = query.eq("role", role)
    query = query.range(offset, offset + limit - 1).order("created_at", desc=True)

    try:
        result = query.execute()
        users = result.data or []
        total = result.count or 0
    except Exception as e:
        raise http_error(400, f"Failed to list users: {str(e)}", code="LIST_FAILED")

    user_responses = [
        UserResponse(
            id=u["id"],
            email=u["email"],
            name=u["name"],
            role=u["role"],
            bio=u.get("bio"),
            wallet_address=u.get("wallet_address"),
            created_at=u.get("created_at"),
        )
        for u in users
    ]

    return UserListResponse(users=user_responses, total=total)
