from os import getenv
from pathlib import Path

from dotenv import load_dotenv
from spotify_readme.modules.paths import PATHS


class ENV_VARS:
    env_file: Path = PATHS.ROOT_DIRECTORY / ".env"
    load_dotenv(env_file)

    REFRESH_TOKEN: str | None = getenv("REFRESH_TOKEN")
    CLIENT_ID: str | None = getenv("CLIENT_ID")
    CLIENT_SECRET: str | None = getenv("CLIENT_SECRET")

    if not all({REFRESH_TOKEN, CLIENT_ID, CLIENT_SECRET}):
        raise OSError(f"Error obtaining required environment variables from {env_file}")
