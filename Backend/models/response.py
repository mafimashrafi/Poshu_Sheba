"""Pydantic request models for saving generated responses."""

from typing import Optional

from pydantic import BaseModel, Field, field_validator


class SaveResponseRequest(BaseModel):
    response: str = Field(min_length=1, max_length=50_000)
    prompt: Optional[str] = Field(default=None, max_length=10_000)
    had_image: bool = False
    had_audio: bool = False

    @field_validator("response")
    @classmethod
    def clean_response(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Response cannot be empty")
        return value

    @field_validator("prompt")
    @classmethod
    def clean_prompt(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        value = value.strip()
        return value or None
