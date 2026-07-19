import secrets
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, Request, status
from pymongo.errors import DuplicateKeyError

from typing import Annotated, Any
from models.user import UserRegisterRequest, LoginRequest, ProfileUpdateRequest
from core.security import hash_password, verify_password, hash_session_token
from routers.responses import require_active_session
from fastapi import APIRouter, HTTPException, Request, status, Depends

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: UserRegisterRequest, request: Request):
    """Create a user account without phone verification."""
    db = request.app.state.db
    users = db.users

    if users.find_one({"phone_number": user.phone_number}, {"_id": 1}):
        raise HTTPException(status_code=409, detail="This phone number is already registered")

    now = datetime.now(timezone.utc)
    try:
        result = db.users.insert_one(
            {
                "name": user.name,
                "phone_number": user.phone_number,
                "password_hash": hash_password(user.password),
                "address": user.address,
                "email": None,
                "profile_picture_url": None,
                "farms": [],
                "created_at": now,
            }
        )
    except DuplicateKeyError:
        raise HTTPException(status_code=409, detail="This phone number is already registered")

    return {"message": "User registered successfully", "user_id": str(result.inserted_id)}


@router.post("/login")
async def login(payload: LoginRequest, request: Request):
    """Verify a phone number and password, then create a session."""
    db = request.app.state.db
    user = db.users.find_one({"phone_number": payload.phone_number})
    if not user or not verify_password(payload.password, user.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid phone number or password")

    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(days=30)
    db.sessions.insert_one(
        {
            "phone_number": user["phone_number"],
            "token_hash": hash_session_token(token),
            "expires_at": expires_at,
            "created_at": datetime.now(timezone.utc),
        }
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_at": expires_at,
    }


@router.get("/profile")
async def get_profile(
    session: Annotated[dict[str, Any], Depends(require_active_session)],
    request: Request,
):
    """Retrieve the profile data of the currently logged-in user."""
    db = request.app.state.db
    user = db.users.find_one({"phone_number": session["phone_number"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "name": user.get("name"),
        "phone_number": user["phone_number"],
        "address": user.get("address", ""),
        "email": user.get("email"),
        "profile_picture_url": user.get("profile_picture_url"),
        "farms": user.get("farms", []),
    }


@router.put("/profile")
async def update_profile(
    payload: ProfileUpdateRequest,
    session: Annotated[dict[str, Any], Depends(require_active_session)],
    request: Request,
):
    """Update user profile fields."""
    db = request.app.state.db

    update_data = {}
    if payload.name is not None:
        update_data["name"] = payload.name
    if payload.address is not None:
        update_data["address"] = payload.address
    if payload.email is not None:
        update_data["email"] = payload.email
    if payload.profile_picture_url is not None:
        update_data["profile_picture_url"] = payload.profile_picture_url
    if payload.farms is not None:
        update_data["farms"] = [farm.model_dump() for farm in payload.farms]

    if not update_data:
        return {"message": "No changes to update"}

    result = db.users.update_one(
        {"phone_number": session["phone_number"]},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "Profile updated successfully"}


@router.delete("/profile")
async def delete_account(
    session: Annotated[dict[str, Any], Depends(require_active_session)],
    request: Request,
):
    """Permanently delete user account and all associated data."""
    db = request.app.state.db
    phone_number = session["phone_number"]

    # 1. Delete user record
    db.users.delete_one({"phone_number": phone_number})

    # 2. Invalidate/delete sessions
    db.sessions.delete_many({"phone_number": phone_number})

    # 3. Delete saved responses
    db.saved_responses.delete_many({"phone_number": phone_number})

    return {"message": "Account deleted successfully"}

