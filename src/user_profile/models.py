import uuid
from datetime import date
from typing import List

from sqlalchemy import CHAR
from sqlalchemy import Date
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import UUID
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from src.models import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    surname: Mapped[str] = mapped_column(String(50), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    bio: Mapped[str] = mapped_column(Text)
    gender: Mapped[str] = mapped_column(CHAR(1), nullable=False)
    country: Mapped[str] = mapped_column(String(50), nullable=False)
    city: Mapped[str] = mapped_column(String(50), nullable=False)

    photos: Mapped[List["UserPhoto"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    social_media_links: Mapped[List["UserSocialMediaLinks"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class UserPhoto(Base):
    __tablename__ = "user_photo"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    url: Mapped[str] = mapped_column(String(255), nullable=False)

    user: Mapped["User"] = relationship(back_populates="photos")


class UserSocialMediaLinks(Base):
    __tablename__ = "user_social_media_links"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    link: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)

    user: Mapped["User"] = relationship(back_populates="social_media_links")
