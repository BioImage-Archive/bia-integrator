from openapi_client import Configuration, ApiClient
from openapi_client.api import DefaultApi
from base64 import b64decode
from typing import Optional
import time
import json

def get_access_token(api_config: Configuration, username: str, password: str) -> str:
    api_client = ApiClient(configuration=api_config)
    default_api = DefaultApi(api_client=api_client)

    auth_token = default_api.login_for_access_token(username, password)
    return auth_token.access_token

def access_token_auto_refresh_bearer(username: str, password: str):
    def _access_token_auto_refresh_bearer(api_config: Configuration) -> str:
        if hasattr(api_config, 'access_token_internal'):
            jwt_payload = b64decode(api_config.access_token_internal.split(".")[1] + "==")
            exp_timestamp = json.loads(jwt_payload)['exp']

            # @FIXME
            # assumes system time is the same as server time
            now = int(time.time())
            # take a 5s buffer
            if now > exp_timestamp - 5:
                api_config.access_token_internal = get_access_token(api_config, username, password)
            else:
                # token exists and doesn't need to be refreshed
                pass
        else:
            api_config.access_token_internal = get_access_token(api_config, username, password)

        return api_config.access_token_internal

    return _access_token_auto_refresh_bearer

def simple_client(api_base_url: str, username: Optional[str] = None, password: Optional[str] = None) -> DefaultApi:
    api_config = Configuration(
        host = api_base_url
    )

    if username and password:
        # override access_token which is static and used in the api client for authentication
        #   with a dynamic property s.t. the token gets refreshed automatically before it expires, for any api call
        Configuration.access_token = property(access_token_auto_refresh_bearer(username, password))

    api_client = ApiClient(configuration=api_config)
    client = DefaultApi(api_client=api_client)

    return client