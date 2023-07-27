import os
from pathlib import Path

from pydantic import BaseSettings
from typing import Optional
from openapi_client import Configuration, ApiClient
from openapi_client.api import DefaultApi
from dotenv import dotenv_values

config = dotenv_values(".env")


class Settings(BaseSettings):
    api_host = "http://localhost:8080"
    bia_api: Optional[DefaultApi] = None

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
    def api_client(self) -> DefaultApi:
        if not self.bia_api:
            config = Configuration(
                host = config["biaint_api_url"]
            )

            config.access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwiZXhwIjoxNjkwNDAzMDI4fQ.zbCqx9U_h8fioSGdEmY0kgXW0RKI0BqVWWkvTK_q1N0"
            api_client = ApiClient(configuration=config)
            self.bia_api = DefaultApi(api_client=api_client)
        
        return self.bia_api

settings = Settings()