"""Module for application settings management. Based on bia-ingest/settings.py."""
import logging
import os
from enum import Enum
from pathlib import Path
from typing import ClassVar, Optional

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


class Settings(BaseSettings):
    # Make API target a class var set at runtime, not from env files or env vars
    _instance: ClassVar[Optional["Settings"]] = None

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

    cache_root_dirpath: str = Field(str(Path.home() / ".cache" / "bia-converter"))
    endpoint_url: str = Field("https://uk1s3.embassy.ebi.ac.uk")
    bucket_name: str = Field("")
    bioformats2raw_java_home: str = Field("")
    bioformats2raw_bin: str = Field("")
    bioformats2raw_docker_tag: str = Field("")

    @classmethod
    def get_instance(cls) -> "Settings":
        if cls._instance is None:
            instance = cls()
            if instance.cache_root_dirpath == "":
                instance.cache_root_dirpath = str(Path.home() / ".cache" / "bia-converter")
            cls._instance = instance
        return cls._instance

def get_settings() -> Settings:
    """Return singleton settings instance."""
    return Settings.get_instance()