import datetime

import pytest


@pytest.mark.parametrize(
    "field,value",
    [
        ("name", ""),
        ("surname", ""),
        ("country", ""),
        ("city", ""),
    ],
)
def test_user_create_required_strings_not_empty(field, value):
    from src.user_profile.schemas import UserCreate

    payload = {
        "email": "test@example.com",
        "name": "A",
        "surname": "B",
        "date_of_birth": "1990-01-01",
        "bio": "ok",
        "gender": "m",
        "country": "C",
        "city": "D",
    }
    payload[field] = value
    with pytest.raises(Exception):
        UserCreate(**payload)


def test_user_create_gender_invalid():
    from src.user_profile.schemas import UserCreate

    with pytest.raises(Exception):
        UserCreate(
            email="a@b.c",
            name="A",
            surname="B",
            date_of_birth="1990-01-01",
            bio="ok",
            gender="x",
            country="C",
            city="D",
        )


def test_user_create_dob_future_and_age():
    from src.user_profile.schemas import UserCreate

    future = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
    with pytest.raises(Exception):
        UserCreate(
            email="a@b.c",
            name="A",
            surname="B",
            date_of_birth=future,
            bio="ok",
            gender="m",
            country="C",
            city="D",
        )


@pytest.mark.parametrize(
    "payload",
    [
        {"name": " ", "surname": "A"},
        {"gender": "x"},
        {"bio": "x" * 6000},
    ],
)
def test_user_update_invalid(payload):
    from src.user_profile.schemas import UserUpdate

    with pytest.raises(Exception):
        UserUpdate(**payload)


@pytest.mark.parametrize(
    "payload",
    [
        {"name": ""},
        {"link": "not-a-url"},
    ],
)
def test_user_social_link_create_invalid(payload):
    from src.user_profile.schemas import UserSocialMediaLinkCreate

    with pytest.raises(Exception):
        UserSocialMediaLinkCreate(**payload)


@pytest.mark.parametrize(
    "payload",
    [
        {"id": 1, "name": ""},
        {"id": 1, "link": "not-a-url"},
    ],
)
def test_user_social_link_update_invalid(payload):
    from src.user_profile.schemas import UserSocialMediaLinkUpdate

    with pytest.raises(Exception):
        UserSocialMediaLinkUpdate(**payload)


@pytest.mark.parametrize(
    "payload",
    [
        {"url": "not-a-url"},
    ],
)
def test_user_photo_create_invalid(payload):
    from src.user_profile.schemas import UserPhotoCreate

    with pytest.raises(Exception):
        UserPhotoCreate(**payload)
