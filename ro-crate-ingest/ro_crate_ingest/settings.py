import logging
import os
from functools import cache
from pathlib import Path

from persistence.settings import Settings as ApiSettings
from pydantic import Field
from pydantic_settings import SettingsConfigDict

logger = logging.getLogger("__main__." + __name__)


class Settings(ApiSettings):
    # Note env files overwrite one another in order of the list (last element overwrites previous ones)
    # Uses api settings to get user create token when testing locally.
    model_config = SettingsConfigDict(
        env_file=[
            *ApiSettings.model_config["env_file"],
            # str(Path(__file__).parents[1] / ".env_template"),
            str(Path(__file__).parents[1] / ".env"),
        ],
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    bia_data_dir: str = Field(
        str(Path(os.environ.get("HOME", "")) / ".cache" / "ro-crate-ingest"),
    )

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

    parallelisation_max_workers: int = Field(4)

@cache
def get_settings() -> Settings:
    return Settings()
