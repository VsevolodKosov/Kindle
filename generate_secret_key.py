import pathlib
import secrets


def generate_secret_key():
    return secrets.token_urlsafe(32)


def create_env_file():
    secret_key = generate_secret_key()

    env_path = pathlib.Path(__file__).parent / "env" / ".env.auth"

    env_path.parent.mkdir(exist_ok=True)

    with open(env_path, "w") as f:
        f.write(f"SECRET_KEY={secret_key}\n")


if __name__ == "__main__":
    create_env_file()
