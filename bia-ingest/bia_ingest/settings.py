from pathlib import Path
import os
import logging

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger("__main__." + __name__)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=[
            f"{Path(__file__).parents[1] / '.env_template'}"      
            f"{Path(__file__).parents[1] / '.env'}"      
            ],
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    bia_data_dir: str = Field(
        str(Path(os.environ.get("HOME", "")) / ".cache" / "bia-integrator-data-sm")
    )
    local_bia_api_basepath: str = Field("http://localhost:8080")
    local_bia_api_username: str = Field("test@example.com")
    local_bia_api_password: str = Field("test")
    bia_api_basepath: str = Field("")
    bia_api_username: str = Field("")
    bia_api_password: str = Field("")



settings = Settings()
