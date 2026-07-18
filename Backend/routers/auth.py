import secrets
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, Request, status
from pymongo.errors import DuplicateKeyError

from models.user import UserRegisterRequest, LoginRequest
from core.security import hash_password, verify_password, hash_session_token

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
