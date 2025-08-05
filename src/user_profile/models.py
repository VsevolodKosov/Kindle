import uuid
from typing import List
from typing import Optional

from sqlalchemy import CHAR
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from src.models import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    bio: Mapped[Optional[str]] = mapped_column(Text)
    gender: Mapped[str] = mapped_column(CHAR(1), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)

    languages: Mapped[List["UserLanguage"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    social_media_links: Mapped[List["UserSocialMediaLink"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    photos: Mapped[List["UserPhoto"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Language(Base):
    __tablename__ = "languages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)

    users: Mapped[List["UserLanguage"]] = relationship(
        back_populates="language", cascade="all, delete-orphan"
    )


class UserLanguage(Base):
    __tablename__ = "user_languages"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True
    )
    language_id: Mapped[int] = mapped_column(
        ForeignKey("languages.id"), primary_key=True
    )

    user: Mapped["User"] = relationship(back_populates="languages")
    language: Mapped["Language"] = relationship(back_populates="users")


class UserSocialMediaLink(Base):
    __tablename__ = "user_social_media_links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    link: Mapped[str] = mapped_column(String(255), nullable=False)

    user: Mapped["User"] = relationship(back_populates="social_media_links")


class UserPhoto(Base):
    __tablename__ = "user_photos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    url: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship(back_populates="photos")
