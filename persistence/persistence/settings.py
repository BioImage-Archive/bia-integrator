from pathlib import Path
from typing import Self

from pydantic import AliasChoices, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
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
    bia_api_basepath: str = Field("")
    bia_api_username: str = Field("")
    bia_api_password: str = Field("")

    @model_validator(mode="after")
    def copy_other_field(self) -> Self:
        self.set_to_local_api()
        return self

    def set_to_dev_api(self):
        self.bia_api_basepath = self.dev_api_basepath
        self.bia_api_username = self.dev_api_username
        self.bia_api_password = self.dev_api_password

    def set_to_local_api(self):
        self.bia_api_basepath = self.local_bia_api_basepath
        self.bia_api_username = self.local_bia_api_username
        self.bia_api_password = self.local_bia_api_password


def get_settings() -> Settings:
    return (
        Settings()
    )  # pyright: ignore[reportCallIssue] - pyright doesn't understand how this loads the field values.
