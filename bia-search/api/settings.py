from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    fastapi_root_path: str = ""

    elastic_connstring: str
    elastic_index: str = "fts_index"

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent / ".env", extra="ignore"
    )
