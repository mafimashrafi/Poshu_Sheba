"""Database operations for user-saved generated responses."""

from datetime import datetime, timezone
from typing import Any


def save_user_response(db: Any, phone_number: str, response: str) -> str:
    """Store a generated response under the authenticated user's phone number."""
    result = db.saved_responses.insert_one(
        {
            "phone_number": phone_number,
            "response": response,
            "created_at": datetime.now(timezone.utc),
        }
    )
    return str(result.inserted_id)


def get_user_saved_responses(db: Any, phone_number: str) -> list[dict[str, Any]]:
    """Return a user's saved responses, most recently saved first."""
    saved_responses = db.saved_responses.find(
        {"phone_number": phone_number}
    ).sort("created_at", -1)
    return [
        {
            "response_id": str(saved_response["_id"]),
            "response": saved_response["response"],
            "created_at": saved_response["created_at"],
        }
        for saved_response in saved_responses
    ]
