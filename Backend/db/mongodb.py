from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, AsyncIterator, Optional
from fastapi import FastAPI
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from Backend.core.config import MONGODB_URI, MONGODB_DB


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    if not MONGODB_URI or not MONGODB_DB:
        raise RuntimeError("MONGODB_URI and MONGODB_DB must be set in .env")

    client = MongoClient(MONGODB_URI, server_api=ServerApi("1"), tz_aware=True)
    try:
        # Verify Atlas access on startup so configuration errors are immediate.
        client.admin.command("ping")
        app.state.mongo_client = client
        app.state.db = client[MONGODB_DB]
        app.state.db.users.create_index("phone_number", unique=True)
        app.state.db.sessions.create_index("token_hash", unique=True)
        app.state.db.sessions.create_index("expires_at", expireAfterSeconds=0)
        app.state.db.saved_responses.create_index([("phone_number", 1), ("created_at", -1)])
        yield
    finally:
        client.close()


def save_user_response(
    db: Any,
    phone_number: str,
    response: str,
    prompt: Optional[str] = None,
    had_image: bool = False,
    had_audio: bool = False,
) -> str:
    """Store a generated response (and the prompt that produced it) under the
    authenticated user's phone number. Images/audio are not stored — MongoDB
    only keeps a note that they were part of the original prompt.
    """
    result = db.saved_responses.insert_one(
        {
            "phone_number": phone_number,
            "response": response,
            "prompt": prompt,
            "had_image": had_image,
            "had_audio": had_audio,
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
            "prompt": saved_response.get("prompt"),
            "had_image": saved_response.get("had_image", False),
            "had_audio": saved_response.get("had_audio", False),
            "created_at": saved_response["created_at"],
        }
        for saved_response in saved_responses
    ]
