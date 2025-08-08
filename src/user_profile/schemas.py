from typing import Annotated
from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from pydantic import constr
from pydantic import EmailStr
from pydantic import field_validator

UsernameStr = Annotated[
    str, constr(min_length=3, max_length=50, strip_whitespace=True)
]
GenderStr = Annotated[
    str, constr(min_length=1, max_length=1, strip_whitespace=True)
]
CountryCityStr = Annotated[
    str, constr(min_length=1, max_length=100, strip_whitespace=True)
]
TitleStr = Annotated[str, constr(min_length=1, max_length=100, strip_whitespace=True)]
LinkStr = Annotated[str, constr(min_length=1, max_length=255, strip_whitespace=True)]
UrlStr = Annotated[str, constr(min_length=1, max_length=255, strip_whitespace=True)]
LanguageNameStr = Annotated[str, constr(min_length=1, max_length=50)]


class UserCreate(BaseModel):
    username: UsernameStr
    email: EmailStr
    bio: Optional[str] = None
    gender: GenderStr
    country: CountryCityStr
    city: CountryCityStr

    @field_validator("gender")
    @classmethod
    def gender_must_be_m_or_f(cls, v):
        if v not in ("m", "f"):
            raise ValueError("Gender must be 'm' or 'f'")
        return v

    @field_validator("bio")
    @classmethod
    def bio_length(cls, v):
        if v is not None and len(v) > 5000:
            raise ValueError("Bio must not exceed 5000 characters")
        return v

    @field_validator("username")
    @classmethod
    def username_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Username cannot be empty")
        return v

    @field_validator("country")
    @classmethod
    def country_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Country cannot be empty")
        return v

    @field_validator("city")
    @classmethod
    def city_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("City cannot be empty")
        return v


class UserRead(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    bio: Optional[str]
    gender: str
    country: str
    city: str

    @classmethod
    def from_orm_obj(cls, user):
        return cls(
            id=user.id,
            username=user.username,
            email=user.email,
            bio=user.bio,
            gender=user.gender,
            country=user.country,
            city=user.city,
        )


class UserUpdate(BaseModel):
    username: Optional[UsernameStr] = None
    email: Optional[EmailStr] = None
    bio: Optional[Optional[str]] = None
    gender: Optional[GenderStr] = None
    country: Optional[CountryCityStr] = None
    city: Optional[CountryCityStr] = None

    @field_validator("gender")
    @classmethod
    def gender_must_be_m_or_f(cls, v):
        if v is not None and v not in ("m", "f"):
            raise ValueError("Gender must be 'm' or 'f'")
        return v


class LanguageCreate(BaseModel):
    name: LanguageNameStr

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Language name cannot be empty")
        return v


class LanguageRead(BaseModel):
    id: int
    name: str

    @classmethod
    def from_orm_obj(cls, language):
        return cls(
            id=language.id,
            name=language.name,
        )


class LanguageUpdate(BaseModel):
    name: Optional[LanguageNameStr] = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Language name cannot be empty")
        return v


class UserLanguageCreate(BaseModel):
    user_id: UUID
    language_id: int


class UserLanguageRead(BaseModel):
    user_id: UUID
    language_id: int

    @classmethod
    def from_orm_obj(cls, user_language):
        return cls(
            user_id=user_language.user_id,
            language_id=user_language.language_id,
        )


class UserSocialMediaLinkCreate(BaseModel):
    user_id: UUID
    title: TitleStr
    link: LinkStr

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Title cannot be empty")
        return v

    @field_validator("link")
    @classmethod
    def link_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Link cannot be empty")
        return v


class UserSocialMediaLinkRead(BaseModel):
    id: int
    user_id: UUID
    title: str
    link: str

    @classmethod
    def from_orm_obj(cls, link):
        return cls(
            id=link.id,
            user_id=link.user_id,
            title=link.title,
            link=link.link,
        )


class UserSocialMediaLinkUpdate(BaseModel):
    title: Optional[TitleStr] = None
    link: Optional[LinkStr] = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Title cannot be empty")
        return v

    @field_validator("link")
    @classmethod
    def link_not_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Link cannot be empty")
        return v


class UserPhotoCreate(BaseModel):
    user_id: UUID
    url: UrlStr
    description: Optional[str] = None

    @field_validator("url")
    @classmethod
    def url_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("URL cannot be empty")
        return v

    @field_validator("description")
    @classmethod
    def description_length(cls, v):
        if v is not None and len(v) > 5000:
            raise ValueError("Description must not exceed 5000 characters")
        return v


class UserPhotoRead(BaseModel):
    id: int
    user_id: UUID
    url: str
    description: Optional[str]

    @classmethod
    def from_orm_obj(cls, photo):
        return cls(
            id=photo.id,
            user_id=photo.user_id,
            url=photo.url,
            description=photo.description,
        )


class UserPhotoUpdate(BaseModel):
    url: Optional[UrlStr] = None
    description: Optional[Optional[str]] = None

    @field_validator("url")
    @classmethod
    def url_not_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError("URL cannot be empty")
        return v

    @field_validator("description")
    @classmethod
    def description_length(cls, v):
        if v is not None and len(v) > 5000:
            raise ValueError("Description must not exceed 5000 characters")
        return v
