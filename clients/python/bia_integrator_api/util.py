from bia_integrator_api import Configuration, ApiClient
from bia_integrator_api.api import PrivateApi
from base64 import b64decode
from typing import Optional
import time
import urllib3
import json

def get_access_token(api_config: Configuration, username: str, password: str) -> str:
    api_client = ApiClient(configuration=api_config)
    default_api = PrivateApi(api_client=api_client)

    auth_token = default_api.login_for_access_token(username, password)
    return auth_token.access_token

def access_token_auto_refresh_bearer(username: str, password: str):
    # Configuration.refresh_api_key_hook (get_api_key_with_prefix) not actually used
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

def simple_client(
        api_base_url: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        disable_ssl_host_check: bool = False,
        auto_refresh_jwt = True
    ) -> PrivateApi:
    api_config = Configuration(
        host = api_base_url
    )
    api_config.verify_ssl = not disable_ssl_host_check
    if disable_ssl_host_check:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    if auto_refresh_jwt:
        if username and password:
            # override access_token which is static and used in the api client for authentication
            #   with a dynamic property s.t. the token gets refreshed automatically before it expires, for any api call
            Configuration.access_token = property(access_token_auto_refresh_bearer(username, password))
    else:
        # just in case both a private and a public client are needed in the same application
        api_config.access_token = get_access_token(api_config, username, password)

    api_client = ApiClient(configuration=api_config)
    client = PrivateApi(api_client=api_client)

    return client
