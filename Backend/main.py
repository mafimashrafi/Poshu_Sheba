import base64
import os
import secrets
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Annotated, Any, AsyncIterator, Optional

from dotenv import load_dotenv
from Middleware.Audio2Text import AudioConversionError, transcribe_audio
from Middleware.SavedResponses import get_user_saved_responses, save_user_response
from Middleware.Security import hash_password, hash_session_token, verify_password
from Middleware.UserSchemas import LoginRequest, SaveResponseRequest, UserRegisterRequest
from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, UploadFile, status
import ollama
from pymongo.errors import DuplicateKeyError
from pymongo import MongoClient
from pymongo.server_api import ServerApi


# Explicitly load the repository's .env, including when Uvicorn is run from Backend/.
load_dotenv(Path(__file__).resolve().parents[1] / ".env")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    mongodb_uri = os.getenv("MONGODB_URI")
    mongodb_db_name = os.getenv("MONGODB_DB")
    if not mongodb_uri or not mongodb_db_name:
        raise RuntimeError("MONGODB_URI and MONGODB_DB must be set in .env")

    client = MongoClient(mongodb_uri, server_api=ServerApi("1"), tz_aware=True)
    try:
        # Verify Atlas access on startup so configuration errors are immediate.
        client.admin.command("ping")
        app.state.mongo_client = client
        app.state.db = client[mongodb_db_name]
        app.state.db.users.create_index("phone_number", unique=True)
        app.state.db.sessions.create_index("token_hash", unique=True)
        app.state.db.sessions.create_index("expires_at", expireAfterSeconds=0)
        app.state.db.saved_responses.create_index([("phone_number", 1), ("created_at", -1)])
        yield
    finally:
        client.close()


app = FastAPI(lifespan=lifespan)


@app.get("/", include_in_schema=False)
async def landing_page():
    return {"message": "Poshu Sheba AI API is running"}


@app.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: UserRegisterRequest):
    """Create a user account without phone verification."""
    users = app.state.db.users

    if users.find_one({"phone_number": user.phone_number}, {"_id": 1}):
        raise HTTPException(status_code=409, detail="This phone number is already registered")

    now = datetime.now(timezone.utc)
    try:
        result = app.state.db.users.insert_one(
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


def require_active_session(
    authorization: Annotated[str | None, Header()] = None,
) -> dict[str, Any]:
    """Return the active session represented by a Bearer access token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Log in before saving responses")

    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise HTTPException(status_code=401, detail="Log in before saving responses")

    session = app.state.db.sessions.find_one({"token_hash": hash_session_token(token)})
    if not session or session["expires_at"] <= datetime.now(timezone.utc):
        if session:
            app.state.db.sessions.delete_one({"_id": session["_id"]})
        raise HTTPException(status_code=401, detail="Your login session has expired")
    return session


@app.post("/login")
async def login(payload: LoginRequest):
    """Verify a phone number and password, then create a save session."""
    user = app.state.db.users.find_one({"phone_number": payload.phone_number})
    if not user or not verify_password(payload.password, user.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid phone number or password")

    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(days=30)
    app.state.db.sessions.insert_one(
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


@app.post("/save-response", status_code=status.HTTP_201_CREATED)
async def save_response(
    payload: SaveResponseRequest,
    session: Annotated[dict[str, Any], Depends(require_active_session)],
):
    """Save a generated response for the phone number associated with the login."""
    response_id = save_user_response(
        app.state.db, session["phone_number"], payload.response
    )
    return {"message": "Response saved successfully", "response_id": response_id}


@app.get("/saved-responses")
async def get_saved_responses(
    session: Annotated[dict[str, Any], Depends(require_active_session)],
):
    """Return all responses saved by the logged-in user."""
    phone_number = session["phone_number"]
    return {
        "phone_number": phone_number,
        "responses": get_user_saved_responses(app.state.db, phone_number),
    }


@app.post("/generate")
async def generate(
        text: Optional[str] = Form(None),
        images: list[UploadFile] = File(default=[]),
        audio: UploadFile | None = File(default=None),
):
    if not text and not images and not audio:
        raise HTTPException(
            status_code=400,
            detail="লিখিত তথ্য, ছবি অথবা অডিও এর থেকে কমপক্ষে একটি দিন।",
        )

    images_b64: list[str] = []
    audio_transcript: Optional[str] = None

    if images:
        for img in images:
            raw = await img.read()
            images_b64.append(base64.b64encode(raw).decode("utf-8"))

    if audio is not None:
        raw = await audio.read()
        try:
            audio_transcript = transcribe_audio(raw, audio.filename, language="bn")
        except AudioConversionError as e:
            raise HTTPException(status_code=500, detail=f"অডিও প্রসেস করায় সমস্যা হয়েছে। দয়া করে কথায় লিখুন। \ন {str(e)}")

    content_parts = []
    if text:
        content_parts.append(text)
    if audio_transcript:
        content_parts.append(
            "[Audio transcript — note: this was transcribed from Bengali "
            "(Bangla) speech using automatic speech recognition, which "
            "sometimes mistakenly renders Bangla in Hindi wording/script "
            "due to phonetic similarity. Interpret the following as "
            f"Bengali speech and reply entirely in Bengali]: {audio_transcript}")
    content = "\n\n".join(content_parts)
    print(content)

    message = {"role": "user", "content": content}
    if images_b64:
        message["images"] = images_b64

    try:
        response = ollama.chat(model="gemma4:e4b-it-q4_K_M", messages=[
            message])
    except ollama.ResponseError as e:
        raise HTTPException( status_code=e.status_code or 502, detail=f"এই মুহূর্তে AI সাহায্য করতে পারছে না। বিকল্প উপায় দেখুন বা আবার চেষ্টা করুন।\n{str(e)}", )
    except ollama.RequestError as e:
        raise HTTPException( status_code=503, detail=f"AI পর্যন্ত কল যায়নি। বিকল্প উপায় দেখুন।\n{str(e)}", )
    return {"response": response["message"]["content"]}
