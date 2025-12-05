"""Module for application settings management. Based on bia-ingest/settings.py."""

import logging
from pathlib import Path
from typing import ClassVar, Optional

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger("__main__." + __name__)


class Settings(BaseSettings):
    # Make API target a class var set at runtime, not from env files or env vars
    _instance: ClassVar[Optional["Settings"]] = None

    # Note env files overwrite one another in order of the list (last element overwrites previous ones)
    # Uses api settings to get user create token when testing locally.
    model_config = SettingsConfigDict(
        env_file=[
            str(
                Path(__file__).parents[2] / "api" / ".env_compose"
            ),  # Needed for local_user_create_secret_token
            str(Path(__file__).parents[1] / ".env"),
        ],
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
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

    cache_root_dirpath: Path = Field(
        Path.home().absolute() / ".cache" / "bia-converter"
    )
    endpoint_url: str = Field("https://uk1s3.embassy.ebi.ac.uk")
    bucket_name: str = Field("")

    aws_access_key_id: str = Field("")
    aws_secret_access_key: str = Field("")
    aws_request_checksum_calculation: str = Field("WHEN_REQUIRED")
    aws_response_checksum_validation: str = Field("WHEN_REQUIRED")

    bioformats2raw_java_home: str = Field("")
    bioformats2raw_bin: str = Field("")
    bioformats2raw_docker_tag: str = Field("")

    @classmethod
    def get_instance(cls) -> "Settings":
        if cls._instance is None:
            instance = cls()
            cls._instance = instance
        return cls._instance


def get_settings() -> Settings:
    """Return singleton settings instance."""
    return Settings.get_instance()
