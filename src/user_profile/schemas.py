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


class LanguageCreate(BaseModel):
    name: LanguageNameStr


class LanguageRead(BaseModel):
    id: int
    name: str


class UserLanguageCreate(BaseModel):
    user_id: UUID
    language_id: int


class UserLanguageRead(BaseModel):
    user_id: UUID
    language_id: int


class UserSocialMediaLinkCreate(BaseModel):
    user_id: UUID
    title: TitleStr
    link: LinkStr


class UserSocialMediaLinkRead(BaseModel):
    id: int
    user_id: UUID
    title: str
    link: str


class UserPhotoCreate(BaseModel):
    user_id: UUID
    url: UrlStr
    description: Optional[str] = None


class UserPhotoRead(BaseModel):
    id: int
    user_id: UUID
    url: str
    description: Optional[str]
