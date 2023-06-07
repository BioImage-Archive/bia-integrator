import os
from pathlib import Path

from pydantic import BaseSettings
from typing import Optional
from openapi_client import Configuration


class Settings(BaseSettings):
    data_dirpath: Path = Path.home()/".bia-integrator-data"
    api_host = "http://45.88.80.182:8080"
    _api_client: Optional[Configuration] = None

    @property
    def studies_dirpath(self):
        return self.data_dirpath/"studies"

    @property
    def aliases_dirpath(self):
        return self.data_dirpath/"aliases"

    @property
    def annotations_dirpath(self):
        return self.data_dirpath/"annotations"

    @property
    def images_dirpath(self):
        return self.data_dirpath/"images"

    @property
    def representations_dirpath(self):
        return self.data_dirpath/"representations"

    @property
    def collections_dirpath(self):
        return self.data_dirpath/"collections"

    @property
    def api_client(self) -> Configuration:
        if not self._api_client:
            self._api_client = Configuration(
                host = self.api_host
            )
        
        return self._api_client

settings = Settings()