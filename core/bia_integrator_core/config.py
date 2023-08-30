from pydantic import BaseSettings
from typing import Optional
from openapi_client.util import simple_client
from openapi_client.api import DefaultApi
from dotenv import dotenv_values

# @TODO: If credentials are missing from config, build public-only unauthenticated client
#config = dotenv_values(".env_biaint")
config = {
    "biaint_api_url": "http://localhost:8080",
    "biaint_username": "test@example.com",
    "biaint_password": "test"
}

class Settings(BaseSettings):
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
            self.bia_api = simple_client(
                config["biaint_api_url"],
                config['biaint_username'],
                config['biaint_password']
            )
        
        return self.bia_api

settings = Settings()