import logging
import os
from enum import Enum
from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger("__main__." + __name__)


LOGGING_LEVELS: dict = {
    0: logging.CRITICAL,
    1: logging.ERROR,
    2: logging.WARNING,
    3: logging.INFO,
    4: logging.DEBUG,
}


class OutputMode(str, Enum):
    table = "table"
    simple = "simple"


class Settings(BaseSettings):
    # Note env files overwrite one another in order of the list (last element overwrites previous ones)
    # Uses api settings to get user create token when testing locally.
    model_config = SettingsConfigDict(
        env_file=[
            str(Path(__file__).parents[2] / "api" / ".env_compose"),
            str(Path(__file__).parents[1] / ".env_template"),
            str(Path(__file__).parents[1] / ".env"),
        ],
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    bia_data_dir: str = Field(
        str(Path(os.environ.get("HOME", "")) / ".cache" / "bia-integrator-data-sm")
    )
    local_bia_api_basepath: str = Field("http://localhost:8080")
    local_bia_api_username: str = Field("test@example.com")
    local_bia_api_password: str = Field("test")
    local_user_create_secret_token: str = Field(
        validation_alias=AliasChoices(
            "local_user_create_secret_token", "USER_CREATE_SECRET_TOKEN"
        )
    )
    bia_api_basepath: str = Field("")
    bia_api_username: str = Field("")
    bia_api_password: str = Field("")


def get_settings():
    return Settings()
