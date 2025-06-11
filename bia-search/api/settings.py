from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    fastapi_root_path: str = ""

    elastic_connstring: str = "http://elastic:test@localhost:9200"
    elastic_index: str = "test_index"

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent / ".env", extra="ignore"
    )
