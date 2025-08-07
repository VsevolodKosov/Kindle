import os
import pathlib

from dotenv import load_dotenv

env_path = pathlib.Path(__file__).parent.parent / "env" / ".env.db_prod"
load_dotenv(dotenv_path=env_path, override=False)

DATABASE_URL = (
    f"postgresql+asyncpg://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@"
    f"{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/"
    f"{os.getenv('POSTGRES_DB')}"
)
