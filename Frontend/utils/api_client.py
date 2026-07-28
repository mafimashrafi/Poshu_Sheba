"""Thin wrapper around the Poshu Sheba AI FastAPI backend.

Every function raises ApiError with a ready-to-display Bangla message on
failure, so UI code never has to parse response bodies itself.
"""

import json
import os
from typing import Any, Optional

import requests

# In production, set BACKEND_URL env var to the deployed backend URL (e.g. Railway).
# Falls back to localhost for local development.
API_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000")
TIMEOUT = 60
# /generate transcribes audio (faster-whisper) and calls the Gemini API, which can
# take a while on the first request. A short timeout here would surface as a
# generic "can't connect" error even though the backend is working fine.
GENERATE_TIMEOUT = 300

CONNECTION_ERROR = "সার্ভারের সাথে সংযোগ করা যায়নি। ব্যাকএন্ড চালু আছে কিনা দেখুন এবং আবার চেষ্টা করুন।"
TIMEOUT_ERROR = "AI উত্তর তৈরি করতে স্বাভাবিকের চেয়ে বেশি সময় নিচ্ছে। কিছুক্ষণ পর আবার চেষ্টা করুন।"


class ApiError(Exception):
    """Carries a Bangla message safe to show directly to the user."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class SessionExpiredError(ApiError):
    """Raised when a bearer token is missing, invalid, or expired."""


def _detail(response: requests.Response, fallback: str) -> str:
    try:
        detail = response.json().get("detail")
    except ValueError:
        detail = None
    return detail or fallback


def register(name: Optional[str], phone_number: str, address: str, password: str) -> dict[str, Any]:
    try:
        response = requests.post(
            f"{API_URL}/register",
            json={"name": name, "phone_number": phone_number, "address": address, "password": password},
            timeout=TIMEOUT,
        )
    except requests.exceptions.RequestException:
        raise ApiError(CONNECTION_ERROR)

    if response.status_code != 201:
        raise ApiError(_detail(response, "অ্যাকাউন্ট তৈরি করা যায়নি। তথ্যগুলো আবার যাচাই করুন।"))
    return response.json()


def login(phone_number: str, password: str) -> dict[str, Any]:
    try:
        response = requests.post(
            f"{API_URL}/login",
            json={"phone_number": phone_number, "password": password},
            timeout=TIMEOUT,
        )
    except requests.exceptions.RequestException:
        raise ApiError(CONNECTION_ERROR)

    if response.status_code != 200:
        raise ApiError(_detail(response, "লগ ইন ব্যর্থ হয়েছে। ফোন নম্বর ও পাসওয়ার্ড আবার দেখুন।"))
    return response.json()


def generate(
    info: Optional[dict],
    text: str,
    images: list,
    audio,
    animal_type: Optional[str] = None,
) -> str:
    if not info and not text and not images and audio is None:
        raise ApiError("লিখিত তথ্য, ছবি অথবা অডিও এর যেকোনো একটি দিন।")

    # The request is multipart/form-data, so the structured intake data
    # (age, fever, stool_urine) travels as a JSON string in the `info` field.
    data: dict[str, str] = {}
    if info:
        data["info"] = json.dumps(info, ensure_ascii=False)
    if text:
        data["text"] = text
    if animal_type:
        data["animal_type"] = animal_type

    files: list[tuple[str, tuple[str, bytes, str]]] = []
    for image in images:
        files.append(("images", (image.name, image.getvalue(), image.type or "application/octet-stream")))
    if audio is not None:
        files.append(("audio", (audio.name or "audio.wav", audio.getvalue(), audio.type or "audio/wav")))

    try:
        response = requests.post(
            f"{API_URL}/generate",
            data=data or None,
            files=files or None,
            timeout=GENERATE_TIMEOUT,
        )
    except requests.exceptions.Timeout:
        raise ApiError(TIMEOUT_ERROR)
    except requests.exceptions.RequestException:
        raise ApiError(CONNECTION_ERROR)

    if response.status_code != 200:
        raise ApiError(_detail(response, "এই মুহূর্তে উত্তর তৈরি করা যায়নি। আবার চেষ্টা করুন।"))
    return response.json()["response"]


def save_response(
    token: str,
    response_text: str,
    prompt: Optional[str] = None,
    had_image: bool = False,
    had_audio: bool = False,
) -> dict[str, Any]:
    try:
        response = requests.post(
            f"{API_URL}/save-response",
            json={
                "response": response_text,
                "prompt": prompt,
                "had_image": had_image,
                "had_audio": had_audio,
            },
            headers={"Authorization": f"Bearer {token}"},
            timeout=TIMEOUT,
        )
    except requests.exceptions.RequestException:
        raise ApiError(CONNECTION_ERROR)

    if response.status_code == 401:
        raise SessionExpiredError("আপনার সেশনের মেয়াদ শেষ হয়ে গেছে। আবার লগ ইন করুন।")
    if response.status_code != 201:
        raise ApiError(_detail(response, "উত্তর সংরক্ষণ করা যায়নি।"))
    return response.json()


def get_saved_responses(token: str) -> list[dict[str, Any]]:
    try:
        response = requests.get(
            f"{API_URL}/saved-responses",
            headers={"Authorization": f"Bearer {token}"},
            timeout=TIMEOUT,
        )
    except requests.exceptions.RequestException:
        raise ApiError(CONNECTION_ERROR)

    if response.status_code == 401:
        raise SessionExpiredError("আপনার সেশনের মেয়াদ শেষ হয়ে গেছে। আবার লগ ইন করুন।")
    if response.status_code != 200:
        raise ApiError(_detail(response, "সংরক্ষিত উত্তর লোড করা যায়নি।"))
    return response.json()["responses"]


def get_profile(token: str) -> dict[str, Any]:
    try:
        response = requests.get(
            f"{API_URL}/profile",
            headers={"Authorization": f"Bearer {token}"},
            timeout=TIMEOUT,
        )
    except requests.exceptions.RequestException:
        raise ApiError(CONNECTION_ERROR)

    if response.status_code == 401:
        raise SessionExpiredError("আপনার সেশনের মেয়াদ শেষ হয়ে গেছে। আবার লগ ইন করুন।")
    if response.status_code != 200:
        raise ApiError(_detail(response, "প্রোফাইল তথ্য লোড করা যায়নি।"))
    return response.json()


def update_profile(token: str, profile_data: dict) -> dict[str, Any]:
    try:
        response = requests.put(
            f"{API_URL}/profile",
            json=profile_data,
            headers={"Authorization": f"Bearer {token}"},
            timeout=TIMEOUT,
        )
    except requests.exceptions.RequestException:
        raise ApiError(CONNECTION_ERROR)

    if response.status_code == 401:
        raise SessionExpiredError("আপনার সেশনের মেয়াদ শেষ হয়ে গেছে। আবার লগ ইন করুন।")
    if response.status_code != 200:
        raise ApiError(_detail(response, "প্রোফাইল আপডেট করা যায়নি।"))
    return response.json()


def delete_account(token: str) -> dict[str, Any]:
    try:
        response = requests.delete(
            f"{API_URL}/profile",
            headers={"Authorization": f"Bearer {token}"},
            timeout=TIMEOUT,
        )
    except requests.exceptions.RequestException:
        raise ApiError(CONNECTION_ERROR)

    if response.status_code == 401:
        raise SessionExpiredError("আপনার সেশনের মেয়াদ শেষ হয়ে গেছে। আবার লগ ইন করুন।")
    if response.status_code != 200:
        raise ApiError(_detail(response, "অ্যাকাউন্ট মুছে ফেলা সম্ভব হয়নি।"))
    return response.json()


def upload_profile_picture(token: str, file_bytes: bytes, filename: str, mime_type: str) -> dict[str, Any]:
    try:
        files = {"file": (filename, file_bytes, mime_type or "application/octet-stream")}
        response = requests.post(
            f"{API_URL}/profile/picture",
            files=files,
            headers={"Authorization": f"Bearer {token}"},
            timeout=TIMEOUT,
        )
    except requests.exceptions.RequestException:
        raise ApiError(CONNECTION_ERROR)

    if response.status_code == 401:
        raise SessionExpiredError("আপনার সেশনের মেয়াদ শেষ হয়ে গেছে। আবার লগ ইন করুন।")
    if response.status_code != 200:
        raise ApiError(_detail(response, "প্রোফাইল ছবি আপলোড করা যায়নি।"))
    return response.json()


