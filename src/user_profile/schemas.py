from datetime import date
from typing import Annotated
from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import field_validator
from pydantic import StringConstraints

NameStr = Annotated[
    str, StringConstraints(min_length=1, max_length=50, strip_whitespace=True)
]

GenderStr = Annotated[
    str, StringConstraints(min_length=1, max_length=1, strip_whitespace=True)
]
CountryCityStr = Annotated[
    str, StringConstraints(min_length=1, max_length=50, strip_whitespace=True)
]
TitleStr = Annotated[
    str, StringConstraints(min_length=1, max_length=100, strip_whitespace=True)
]
LinkStr = Annotated[
    str, StringConstraints(min_length=1, max_length=255, strip_whitespace=True)
]
UrlStr = Annotated[
    str, StringConstraints(min_length=1, max_length=255, strip_whitespace=True)
]


class UserCreate(BaseModel):
    email: EmailStr
    name: NameStr
    surname: NameStr
    date_of_birth: date
    bio: Optional[str] = None
    gender: GenderStr
    country: CountryCityStr
    city: CountryCityStr

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v):
        if v not in ("m", "f"):
            raise ValueError("Gender must be m or f")
        return v

    @field_validator("bio")
    @classmethod
    def validate_bio(cls, v):
        if v is not None and len(v) > 5000:
            raise ValueError("Bio must not exceed 5000 characters")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Name cannot be empty")
        return v

    @field_validator("surname")
    @classmethod
    def validate_surname(cls, v):
        if not v or not v.strip():
            raise ValueError("Surname cannot be empty")
        return v

    @field_validator("country")
    @classmethod
    def validate_country(cls, v):
        if not v or not v.strip():
            raise ValueError("Country cannot be empty")
        return v

    @field_validator("city")
    @classmethod
    def validate_city(cls, v):
        if not v or not v.strip():
            raise ValueError("City cannot be empty")
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


class UserRead(BaseModel):
    user_id: UUID
    email: EmailStr
    name: NameStr
    surname: NameStr
    date_of_birth: date
    bio: Optional[str] = None
    gender: GenderStr
    country: CountryCityStr
    city: CountryCityStr

    @property
    def age(self) -> int:
        today = date.today()
        return (
            today.year
            - self.date_of_birth.year
            - (
                (today.month, today.day)
                < (self.date_of_birth.month, self.date_of_birth.day)
            )
        )

    @classmethod
    def from_orm_obj(cls, user) -> "UserRead":
        return cls(
            user_id=user.id,
            email=user.email,
            name=user.name,
            surname=user.surname,
            date_of_birth=user.date_of_birth,
            bio=user.bio,
            gender=user.gender,
            country=user.country,
            city=user.city,
        )


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[NameStr] = None
    surname: Optional[NameStr] = None
    date_of_birth: Optional[date] = None
    bio: Optional[str] = None
    gender: Optional[GenderStr] = None
    country: Optional[CountryCityStr] = None
    city: Optional[CountryCityStr] = None

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v):
        if v is not None and v not in ("m", "f"):
            raise ValueError("Gender must be 'm' or 'f'")
        return v


class UserSocialMediaLinkCreate(BaseModel):
    name: NameStr
    link: LinkStr

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Name cannot be empty")
        return v

    @field_validator("link")
    @classmethod
    def validate_link(cls, v):
        if not v or not v.strip():
            raise ValueError("Link cannot be empty")
        return v


class UserSocialMediaLinkRead(BaseModel):
    id: int
    user_id: UUID
    name: str
    link: str

    @classmethod
    def from_orm_obj(cls, link):
        return cls(
            id=link.id,
            user_id=link.user_id,
            name=link.name,
            link=link.link,
        )


class UserSocialMediaLinkUpdate(BaseModel):
    id: int
    name: Optional[NameStr] = None
    link: Optional[LinkStr] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Name cannot be empty")
        return v

    @field_validator("link")
    @classmethod
    def validate_link(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Link cannot be empty")
        return v

    @classmethod
    def from_orm_obj(cls, link):
        return cls(
            id=link.id,
            name=link.name,
            link=link.link,
        )


class UserPhotoCreate(BaseModel):
    url: UrlStr

    @field_validator("url")
    @classmethod
    def validate_url(cls, v):
        if not v or not v.strip():
            raise ValueError("URL cannot be empty")
        return v


class UserPhotoRead(BaseModel):
    id: int
    user_id: UUID
    url: str

    @classmethod
    def from_orm_obj(cls, photo):
        return cls(
            id=photo.id,
            user_id=photo.user_id,
            url=photo.url,
        )


class UserPhotoUpdate(BaseModel):
    id: int
    url: Optional[UrlStr] = None

    @field_validator("url")
    @classmethod
    def validate_url(cls, v):
        if v is not None and not v.strip():
            raise ValueError("URL cannot be empty")
        return v
