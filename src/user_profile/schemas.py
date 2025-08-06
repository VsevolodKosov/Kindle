from typing import Annotated
from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from pydantic import constr
from pydantic import EmailStr
from pydantic import field_validator

UsernameStr = Annotated[str, constr(min_length=3, max_length=50)]
GenderStr = Annotated[str, constr(min_length=1, max_length=1)]
CountryCityStr = Annotated[str, constr(min_length=1, max_length=100)]
TitleStr = Annotated[str, constr(min_length=1, max_length=100)]
LinkStr = Annotated[str, constr(min_length=1, max_length=255)]
UrlStr = Annotated[str, constr(min_length=1, max_length=255)]
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
    bio: Optional[Optional[str]] = None  # Allow explicit null
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


class UserPhotoCreate(BaseModel):
    user_id: UUID
    url: UrlStr
    description: Optional[str] = None


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
