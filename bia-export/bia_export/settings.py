from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    api_base_url: str = Field(default="https://wwwdev.ebi.ac.uk/bioimage-archive/api")

    # Note that Pydantic will prefer current ENV values over those in the file.
    # This is useful & used to override values for testing.
    class Config:
        env_file = ".env_export"
        env_file_encoding = "utf-8"


settings = Settings()
