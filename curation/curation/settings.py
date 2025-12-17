from functools import cache
from pathlib import Path

from persistence.settings import Settings as ApiSettings
from pydantic_settings import SettingsConfigDict


class Settings(ApiSettings):
    model_config = SettingsConfigDict(
        env_file=[
            *ApiSettings.model_config["env_file"],
            str(Path(__file__).parents[1] / ".env"),
        ],
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    endpoint_url: str = "https://uk1s3.embassy.ebi.ac.uk"
    bucket_name: str = "bia-integrator-data"
    cache_root_dirpath: Path = Path.home() / ".cache" / "bia-converter"

@cache
def get_settings() -> Settings:
    return (
        Settings()
    )  # pyright: ignore[reportCallIssue] - pyright doesn't understand this loads the field values.
