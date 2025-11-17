from pathlib import Path
from typing import Self

from pydantic import Field, model_validator, AliasChoices
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

    endpoint_url: str = "https://uk1s3.embassy.ebi.ac.uk"
    bucket_name: str = "bia-integrator-data"
    cache_root_dirpath: Path = Path.home() / ".cache" / "bia-converter"

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
    def copy_other_field(
        self,
    ) -> Self:
        for field in ("bia_api_basepath", "bia_api_username", "bia_api_password"):
            self.__setattr__(field, self.__getattribute__(f"local_{field}"))
        return self

    def configure_for_dev_api(self):
        self.bia_api_basepath = self.dev_api_basepath
        self.bia_api_username = self.dev_api_username
        self.bia_api_password = self.dev_api_password


def get_settings() -> Settings:
    return (
        Settings()
    )  # pyright: ignore[reportCallIssue] - pyright doesn't understand this loads the field values.
