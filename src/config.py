import os
import pathlib
from typing import Final

from dotenv import load_dotenv

PATH_ENV_DB = pathlib.Path(__file__).parent.parent / "env" / ".env.db_prod"
load_dotenv(dotenv_path=PATH_ENV_DB, override=False)

user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
host = os.getenv("POSTGRES_HOST")
port = os.getenv("POSTGRES_PORT")
db = os.getenv("POSTGRES_DB")
DATABASE_URL = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"

PATH_ENV_AUTH = pathlib.Path(__file__).parent.parent / "env" / ".env.auth"
load_dotenv(dotenv_path=PATH_ENV_AUTH, override=False)

SECRET_KEY: Final[str] = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRES_MINUTES = 5
REFRESH_TOKEN_EXPIRE_DAYS = 7

COOKIE_ACCESS_TOKEN_MAX_AGE = ACCESS_TOKEN_EXPIRES_MINUTES * 60
COOKIE_REFRESH_TOKEN_MAX_AGE = REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
COOKIE_SECURE = False
COOKIE_SAMESITE = "lax"
COOKIE_HTTPONLY = True
COOKIE_DOMAIN = None
COOKIE_PATH = "/"
