"""Pydantic request models for user registration and login."""

import re
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class UserRegisterRequest(BaseModel):
    name: Optional[str] = Field(default=None, max_length=100)
    phone_number: str = Field(description="Bangladesh mobile number")
    password: str = Field(min_length=8, max_length=128)

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        value = value.strip()
        return value or None

    @field_validator("phone_number")
    @classmethod
    def normalize_bangladesh_phone(cls, value: str) -> str:
        number = re.sub(r"[\s-]", "", value)
        if number.startswith("+880"):
            number = "0" + number[4:]
        elif number.startswith("880"):
            number = "0" + number[3:]

        if not re.fullmatch(r"01[3-9]\d{8}", number):
            raise ValueError("Enter a valid Bangladesh mobile number")
        return "+880" + number[1:]


class LoginRequest(BaseModel):
    phone_number: str = Field(description="Bangladesh mobile number")
    password: str = Field(min_length=8, max_length=128)

    @field_validator("phone_number")
    @classmethod
    def normalize_bangladesh_phone(cls, value: str) -> str:
        return UserRegisterRequest.normalize_bangladesh_phone(value)
