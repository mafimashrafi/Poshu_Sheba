import secrets
import os
import io
from datetime import datetime, timedelta, timezone
from pathlib import Path
from PIL import Image, UnidentifiedImageError
from fastapi import APIRouter, HTTPException, Request, status, Depends, UploadFile, File
from pymongo.errors import DuplicateKeyError

from typing import Annotated, Any
from models.user import UserRegisterRequest, LoginRequest, ProfileUpdateRequest
from core.security import hash_password, verify_password, hash_session_token
from routers.responses import require_active_session

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
    phone_number = payload.phone_number

    # 1. Rate limiting check
    now = datetime.now(timezone.utc)
    attempt_record = db.login_attempts.find_one({"phone_number": phone_number})
    if attempt_record:
        failed_attempts = attempt_record.get("attempts", 0)
        last_failed_at = attempt_record.get("last_failed_at")
        if failed_attempts >= 5:
            time_diff = now - last_failed_at
            if time_diff.total_seconds() < 15 * 60:
                raise HTTPException(
                    status_code=429,
                    detail="অনেকবার ভুল চেষ্টা করা হয়েছে, অনুগ্রহ করে ১৫ মিনিট পর আবার চেষ্টা করুন।"
                )

    user = db.users.find_one({"phone_number": phone_number})
    if not user or not verify_password(payload.password, user.get("password_hash", "")):
        # Record failed attempt
        if attempt_record:
            last_failed_at = attempt_record.get("last_failed_at")
            time_diff = now - last_failed_at
            if time_diff.total_seconds() >= 15 * 60:
                new_attempts = 1
            else:
                new_attempts = attempt_record.get("attempts", 0) + 1

            db.login_attempts.update_one(
                {"phone_number": phone_number},
                {"$set": {"attempts": new_attempts, "last_failed_at": now}}
            )
        else:
            db.login_attempts.insert_one(
                {
                    "phone_number": phone_number,
                    "attempts": 1,
                    "last_failed_at": now
                }
            )
        raise HTTPException(status_code=401, detail="Invalid phone number or password")

    # Reset attempts on success
    db.login_attempts.delete_one({"phone_number": phone_number})

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


@router.post("/logout")
async def logout(
    session: Annotated[dict[str, Any], Depends(require_active_session)],
    request: Request,
):
    """Log out the user globally, invalidating all sessions."""
    db = request.app.state.db
    phone_number = session["phone_number"]
    db.sessions.delete_many({"phone_number": phone_number})
    return {"message": "Logged out from all sessions successfully"}


@router.post("/profile/picture")
async def upload_profile_picture(
    request: Request,
    file: UploadFile = File(...),
    session: Annotated[dict[str, Any], Depends(require_active_session)] = None,
):
    """Upload a profile picture for the authenticated user, validating file type and size."""
    db = request.app.state.db

    # 1. Fetch user to obtain ID and check existing picture
    user = db.users.find_one({"phone_number": session["phone_number"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_id_str = str(user["_id"])

    # 2. Check extension and MIME type
    filename = file.filename or ""
    ext = os.path.splitext(filename)[1].lower()
    allowed_exts = {".jpg", ".jpeg", ".png", ".webp"}
    allowed_types = {"image/jpeg", "image/jpg", "image/png", "image/webp"}

    if ext not in allowed_exts or file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Only jpg, jpeg, png, and webp images are allowed")

    # 3. Read content to validate size (max 5 MB)
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds the 5 MB limit")

    # 4. Verify image integrity with Pillow
    try:
        img = Image.open(io.BytesIO(content))
        img.verify()
    except (UnidentifiedImageError, IOError, SyntaxError):
        raise HTTPException(status_code=400, detail="Invalid image file")

    # 5. Delete existing old profile picture if any
    old_url = user.get("profile_picture_url")
    if old_url and "/uploads/profile_pictures/" in old_url:
        old_filename = old_url.split("/uploads/profile_pictures/")[-1]
        old_filepath = Path(__file__).resolve().parent.parent / "uploads" / "profile_pictures" / old_filename
        if old_filepath.exists() and old_filepath.is_file():
            try:
                os.remove(old_filepath)
            except Exception as e:
                # Tolerate deletion error
                pass

    # 6. Save the new file uniquely
    new_filename = f"{user_id_str}{ext}"
    uploads_dir = Path(__file__).resolve().parent.parent / "uploads" / "profile_pictures"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    filepath = uploads_dir / new_filename

    try:
        with open(filepath, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save profile picture: {str(e)}")

    # 7. Update database with fully qualified URL
    full_url = f"{request.base_url}uploads/profile_pictures/{new_filename}"
    db.users.update_one(
        {"phone_number": session["phone_number"]},
        {"$set": {"profile_picture_url": full_url}}
    )

    return {"message": "Profile picture updated successfully", "profile_picture_url": full_url}



