from datetime import datetime, timezone
from typing import Annotated, Any
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status

from models.response import SaveResponseRequest
from db.mongodb import save_user_response, get_user_saved_responses
from core.security import hash_session_token

router = APIRouter()


def require_active_session(
    request: Request,
    authorization: Annotated[str | None, Header()] = None,
) -> dict[str, Any]:
    """Return the active session represented by a Bearer access token."""
    db = request.app.state.db
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Log in before saving responses")

    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise HTTPException(status_code=401, detail="Log in before saving responses")

    session = db.sessions.find_one({"token_hash": hash_session_token(token)})
    if not session or session["expires_at"] <= datetime.now(timezone.utc):
        if session:
            db.sessions.delete_one({"_id": session["_id"]})
        raise HTTPException(status_code=401, detail="Your login session has expired")
    return session


@router.post("/save-response", status_code=status.HTTP_201_CREATED)
async def save_response(
    payload: SaveResponseRequest,
    session: Annotated[dict[str, Any], Depends(require_active_session)],
    request: Request,
):
    """Save a generated response for the phone number associated with the login."""
    db = request.app.state.db
    response_id = save_user_response(
        db, session["phone_number"], payload.response
    )
    return {"message": "Response saved successfully", "response_id": response_id}


@router.get("/saved-responses")
async def get_saved_responses(
    session: Annotated[dict[str, Any], Depends(require_active_session)],
    request: Request,
):
    """Return all responses saved by the logged-in user."""
    db = request.app.state.db
    phone_number = session["phone_number"]
    return {
        "phone_number": phone_number,
        "responses": get_user_saved_responses(db, phone_number),
    }
