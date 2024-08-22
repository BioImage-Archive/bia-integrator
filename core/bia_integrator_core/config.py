from pathlib import Path
from pydantic import BaseSettings
from typing import Optional
from bia_integrator_api.util import simple_client
from bia_integrator_api.api import PrivateApi


class Settings(BaseSettings):
    bia_api_basepath: str = "http://localhost:8080"
    bia_username: Optional[str] = None
    bia_password: Optional[str] = None
    bia_disable_ssl_host_check: bool = False
    cache_root_dirpath: Path = Path.home() / ".cache" / "bia-converter"

    bia_api_client: Optional[PrivateApi] = None

    @property
    def api_client(self) -> PrivateApi:
        if not self.bia_api_client:
            self.bia_api_client = simple_client(
                self.bia_api_basepath,
                self.bia_username,
                self.bia_password,
                self.bia_disable_ssl_host_check,
            )

        return self.bia_api_client

    class Config:
        case_sensitive: True


settings = Settings()
