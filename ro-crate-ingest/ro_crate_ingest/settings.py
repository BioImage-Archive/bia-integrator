from pathlib import Path
import os
import logging

from pydantic import Field, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger("__main__." + __name__)


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
        str(Path(os.environ.get("HOME", "")) / ".cache" / "ro-crate-ingest"),
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

    biostudies_override_dir: str = Field(
        str(Path(__file__).parents[1] / "override_data" / "biostudies")
    )
    empiar_override_dir: str = Field(
        str(Path(__file__).parents[1] / "override_data" / "empiar")
    )

    accepted_bioformats_file: str = Field(
        str(
            Path(__file__).parents[1]
            / "resources"
            / "bioformats_curated_single_file_formats.txt"
        )
    )


def get_settings():
    return Settings()
