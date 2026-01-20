import logging
from pathlib import Path
from typing import ClassVar, Optional
from enum import Enum

from pydantic import Field
from pydantic_settings import SettingsConfigDict
from persistence.settings import Settings as ApiSettings

logger = logging.getLogger(__name__)


class OutputMode(str, Enum):
    BOTH = "both"
    LOCAL = "local"
    S3 = "s3"
    DRY_RUN = "dry_run"


class Settings(ApiSettings):
    # API target a class var at runtime, not from env files or env vars
    _instance: ClassVar[Optional["Settings"]] = None

    model_config = SettingsConfigDict(
        env_file=[
            *ApiSettings.model_config["env_file"], 
            str(Path(__file__).parents[1] / ".env"), 
        ],
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    default_output_directory: Path = Field(Path(__file__).parents[1] / "output_data")
    local_annotations_server: str | None = Field(None)

    s3_endpoint_url: str = Field("https://uk1s3.embassy.ebi.ac.uk")
    s3_bucket_name: str | None = Field(None)

    output_mode: OutputMode = Field(OutputMode.LOCAL)

    @classmethod
    def get_instance(cls) -> "Settings":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


def get_settings() -> Settings:
    """Return singleton settings instance."""
    return Settings.get_instance()
