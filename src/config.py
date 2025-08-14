import os
import pathlib

from dotenv import load_dotenv

PATH_ENV = pathlib.Path(__file__).parent.parent / "env" / ".env.db_prod"
load_dotenv(dotenv_path=PATH_ENV, override=False)

user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
host = os.getenv("POSTGRES_HOST")
port = os.getenv("POSTGRES_PORT")
db = os.getenv("POSTGRES_DB")
DATABASE_URL = f"postgresql+asyncpg//{user}:{password}@{host}:{port}/{db}"
