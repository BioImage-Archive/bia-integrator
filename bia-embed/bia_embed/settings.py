from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path


class Settings(BaseSettings):
    api_base_url: str = Field(default="http://localhost:8080")
    api_username: str = Field(default="test@example.com")
    api_password: str = Field(default="test")

    # Note that Pydantic will prefer current ENV values over those in the file.
    # This is useful & used to override values for testing.
    model_config = SettingsConfigDict(
        env_file=f"{Path(__file__).parent / '.env_embed'}",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
