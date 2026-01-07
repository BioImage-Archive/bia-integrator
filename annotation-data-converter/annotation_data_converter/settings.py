import os
import logging

from pathlib import Path
from pydantic import Field, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger("__main__." + __name__)


class Settings(BaseSettings):
    # Note env files overwrite one another in order of the list (last element overwrites previous ones)
    # Uses api settings to get user create token when testing locally.
    model_config = SettingsConfigDict(
        env_file=[
            str(Path(__file__).parents[2] / "api" / ".env_compose"),
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

    default_output_directory: Path = Field(Path(__file__).parents[1] / "output_data")
    local_annotations_server: str | None = Field(None)

    endpoint_url: str = Field("https://uk1s3.embassy.ebi.ac.uk")
    bucket_name: str | None = Field(None)
    aws_request_checksum_calculation: str = Field("WHEN_REQUIRED")
    aws_response_checksum_validation: str = Field("WHEN_REQUIRED")


def get_settings():
    return Settings()  # pyright: ignore[reportCallIssue]
