from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    fastapi_root_path: str = ""

    elastic_connstring: str = "http://elastic:test@localhost:9200"
    elastic_index_study: str = "test_index"
    elastic_index_image: str = "test_index_images"

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent / ".env", extra="ignore"
    )
