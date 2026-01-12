import logging
from functools import cache
from pathlib import Path
from typing import Self

from pydantic import (
    AliasChoices,
    Field,
    ValidationInfo,
    field_validator,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger("__main__." + __name__)


class Settings(BaseSettings):
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

    dev_api_basepath: str = Field("")
    dev_api_username: str = Field("")
    dev_api_password: str = Field("")

    # Defaults to local api
    bia_api_basepath: str | None = Field(None)
    bia_api_username: str | None = Field(None)
    bia_api_password: str | None = Field(None)

    # s3 settings
    aws_access_key_id: str = Field(default="", description="AWS access key (required for S3 uploads)")
    aws_secret_access_key: str = Field(default="", description="AWS secret key (required for S3 uploads)")
    aws_request_checksum_calculation: str = Field(default="WHEN_REQUIRED")
    aws_response_checksum_validation: str = Field(default="WHEN_REQUIRED")
    endpoint_url: str = Field(default="https://uk1s3.embassy.ebi.ac.uk", description="S3 endpoint URL")
    bucket_name: str = Field(default="", description="S3 bucket name (required for S3 uploads)")

    @model_validator(mode="after")
    def copy_other_field(self) -> Self:
        self.set_to_local_api()
        return self

    @field_validator(
        "bia_api_basepath", "bia_api_username", "bia_api_password", mode="before"
    )
    def warn_about_overwrite(cls, value: str, info: ValidationInfo):
        if value:
            logger.warning(
                f"{info.field_name} was set but this value may get overwritten by code. Use local_{info.field_name} or dev_{info.field_name} instead."
            )
        return value

    def set_to_dev_api(self):
        self.bia_api_basepath = self.dev_api_basepath
        self.bia_api_username = self.dev_api_username
        self.bia_api_password = self.dev_api_password

    def set_to_local_api(self):
        self.bia_api_basepath = self.local_bia_api_basepath
        self.bia_api_username = self.local_bia_api_username
        self.bia_api_password = self.local_bia_api_password


@cache
def get_settings() -> Settings:
    return (
        Settings()
    )  # pyright: ignore[reportCallIssue] - pyright doesn't understand how this loads the field values.
