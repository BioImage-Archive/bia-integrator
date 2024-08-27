from bia_integrator_api import Configuration, ApiClient
from bia_integrator_api.api import PrivateApi, PublicApi

PUBLIC_API_URI = "http://localhost:8080"

def get_client(
    api_base_url: str = PUBLIC_API_URI
) -> PublicApi:
    api_config = Configuration(
        host = api_base_url
    )
    
    api_client = ApiClient(configuration=api_config)
    return PublicApi(api_client=api_client)

def get_client_private(
    username: str,
    password: str,
    api_base_url: str = PUBLIC_API_URI,
    auto_refresh_jwt = False
) -> PrivateApi:
    if auto_refresh_jwt:
        """
        @TODO
        re-add auth autorefresh hook / @property workaround from the deprecated client?
        caveat of the api client having to be a singleton, and it also seems like there must be less hacky way to do this
        """
        raise Exception("TODO")

    api_config = Configuration(
        host = api_base_url
    )
    private_api = PrivateApi(ApiClient(configuration=api_config))
    access_token = private_api.login_for_access_token(username=username, password=password)
    api_config.access_token = access_token.access_token

    return private_api