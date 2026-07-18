"""Pydantic request models for saving generated responses."""

from pydantic import BaseModel, Field, field_validator


class SaveResponseRequest(BaseModel):
    response: str = Field(min_length=1, max_length=50_000)

    @field_validator("response")
    @classmethod
    def clean_response(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Response cannot be empty")
        return value
