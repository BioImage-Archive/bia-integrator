from bia_integrator_api import Configuration, ApiClient
from bia_integrator_api.api import PrivateApi, PublicApi
from typing import Optional

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
    api_base_url: str = PUBLIC_API_URI,
    username: Optional[str] = None,
    password: Optional[str] = None,
    auto_refresh_jwt = True
) -> PrivateApi:
    raise Exception("TODO - auth")