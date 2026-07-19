"""Pydantic request models for user registration and login."""

import re
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


class UserRegisterRequest(BaseModel):
    name: Optional[str] = Field(default=None, max_length=100)
    phone_number: str = Field(description="Bangladesh mobile number")
    address: str = Field(description="User address")
    password: str = Field(min_length=8, max_length=128)

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        value = value.strip()
        return value or None

    @field_validator("address")
    @classmethod
    def validate_address(cls, value: str) -> str:
        if value is None or not value.strip():
            raise ValueError("Address cannot be empty")
        return value.strip()

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


class FarmEntry(BaseModel):
    animal_type: str = Field(description="Type of animal")
    count: int = Field(ge=1, description="Number of animals")

    @field_validator("animal_type")
    @classmethod
    def validate_animal_type(cls, value: str) -> str:
        if value is None or not value.strip():
            raise ValueError("Animal type cannot be empty")
        return value.strip()


class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = Field(default=None, max_length=100)
    address: Optional[str] = Field(default=None)
    email: Optional[str] = Field(default=None)
    profile_picture_url: Optional[str] = Field(default=None)
    farms: Optional[List[FarmEntry]] = Field(default=None)

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        value = value.strip()
        return value or None

    @field_validator("address")
    @classmethod
    def clean_address(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("Address cannot be empty")
        return value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        value = value.strip()
        if not value:
            return None
        if not re.fullmatch(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", value):
            raise ValueError("Enter a valid email address")
        return value
