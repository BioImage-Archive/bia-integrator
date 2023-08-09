import os
import json
import time
from pathlib import Path

from pydantic import BaseSettings
from typing import Optional
from openapi_client import Configuration, ApiClient
from openapi_client.api import DefaultApi
from dotenv import dotenv_values
from base64 import b64decode

# @TODO: If credentials are missing from config, build public-only unauthenticated client
#config = dotenv_values(".env_biaint")
config = {
    "biaint_api_url": "http://localhost:8080",
    "biaint_username": "test@example.com",
    "biaint_password": "test"
}

def get_access_token(api_config: Configuration) -> str:
    api_client = ApiClient(configuration=api_config)
    default_api = DefaultApi(api_client=api_client)

    auth_token = default_api.login_for_access_token_auth_token_post(config['biaint_username'], config['biaint_password'])
    return auth_token.access_token

def access_token_auto_refresh_bearer(api_config: Configuration):
    if hasattr(api_config, 'access_token_internal'):
        jwt_payload = b64decode(api_config.access_token_internal.split(".")[1] + "==")
        exp_timestamp = json.loads(jwt_payload)['exp']

        # @FIXME
        # assumes system time is the same as server time
        now = int(time.time())
        # take a 5s buffer
        if now > exp_timestamp - 5:
            api_config.access_token_internal = get_access_token(api_config)
        else:
            # token exists and doesn't need to be refreshed
            pass
    else:
        api_config.access_token_internal = get_access_token(api_config)

    return api_config.access_token_internal


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
            api_config = Configuration(
                host = config["biaint_api_url"]
            )

            # override access_token which is static and used in the api client for authentication
            #   with a dynamic property s.t. the token gets refreshed automatically before it expires, for any api call
            Configuration.access_token = property(access_token_auto_refresh_bearer)

            api_client = ApiClient(configuration=api_config)
            self.bia_api = DefaultApi(api_client=api_client)
        
        return self.bia_api

settings = Settings()