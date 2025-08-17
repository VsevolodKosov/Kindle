from datetime import date
from typing import Annotated, Optional

from pydantic import BaseModel, EmailStr, StringConstraints, field_validator

NameStr = Annotated[
    str, StringConstraints(min_length=1, max_length=50, strip_whitespace=True)
]
GenderStr = Annotated[
    str, StringConstraints(min_length=1, max_length=1, strip_whitespace=True)
]
CountryCityStr = Annotated[
    str, StringConstraints(min_length=1, max_length=50, strip_whitespace=True)
]
PasswordStr = Annotated[str, StringConstraints(min_length=8)]
AccessTokenStr = Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)]
RefreshTokenStr = Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)]


def validate_password_not_empty(v: str) -> str:
    if not v.strip():
        raise ValueError("Password cannot be empty")
    return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: PasswordStr

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        return validate_password_not_empty(v)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: PasswordStr
    name: NameStr
    surname: NameStr
    date_of_birth: date
    bio: Optional[str] = None
    gender: GenderStr
    country: CountryCityStr
    city: CountryCityStr

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        return validate_password_not_empty(v)

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v):
        if v not in ("m", "f"):
            raise ValueError("Gender must be m or f")
        return v

    @field_validator("bio")
    @classmethod
    def validate_bio(cls, v):
        if v and len(v) > 5000:
            raise ValueError("Bio must not exceed 5000 characters")
        return v

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, v: date) -> date:
        today = date.today()
        min_age = 18
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if v > today:
            raise ValueError("Date of birth cannot be in the future")
        if age < min_age:
            raise ValueError(f"User must be at least {min_age} years old")
        return v


class TokenRevokeRequest(BaseModel):
    refresh_token: RefreshTokenStr


class TokenResponse(BaseModel):
    access_token: AccessTokenStr
    refresh_token: RefreshTokenStr


class RefreshTokenResponse(BaseModel):
    refresh_token: RefreshTokenStr
    active: bool
