from pathlib import Path
from pydantic_settings import SettingsConfigDict
from persistence.settings import Settings as ApiSettings


class Settings(ApiSettings):
    model_config = SettingsConfigDict(
        env_file=[
            *ApiSettings.model_config["env_file"],
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


def get_settings() -> Settings:
    return (
        Settings()
    )  # pyright: ignore[reportCallIssue] - pyright doesn't understand this loads the field values.
