from pathlib import Path
import os
import logging

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from bia_integrator_api.util import get_client_private

logger = logging.getLogger("__main__." + __name__)

default_output_base = (
    f"{Path(os.environ.get('HOME', '')) / '.cache' / 'bia-integrator-data-sm'}"
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=f"{Path(__file__).parent.parent / '.env'}",
        env_file_encoding="utf-8",
        case_sensitive=False,
        # extra="forbid",
    )

    bia_data_dir: str = Field(default_output_base)
    endpoint_url: str = Field("https://uk1s3.embassy.ebi.ac.uk")
    bucket_name: str = Field("bia-integrator-data")
    cache_root_dirpath: Path = Field(Path.home() / ".cache" / "bia-converter")
    bioformats2raw_java_home: str = Field("")
    bioformats2raw_bin: str = Field("")
    bia_api_basepath: str = Field("http://localhost:8080")
    bia_api_username: str = Field("test@example.com")
    bia_api_password: str = Field("test")


# class Settings:
#    def __init__(self):
#        self.bia_data_dir = default_output_base


settings = Settings()

# TODO: Put client details in .env (and maybe environment variables?)
try:
    api_client = get_client_private(
        username=settings.bia_api_username,
        password=settings.bia_api_password,
        api_base_url=settings.bia_api_basepath,
    )
except Exception as e:
    message = f"Could not initialise api_client: {e}"
    logger.warning(message)
    api_client = None
