import bia_integrator_api.models as api_models
import logging

from bia_integrator_api.util import get_client_private
from bia_integrator_api import Configuration, ApiClient, exceptions
from bia_integrator_api.api import PrivateApi
from enum import Enum
from .settings import get_settings

logger = logging.getLogger("__main__." + __name__)


def get_bia_api_client() -> PrivateApi:
    settings = get_settings()
    private_api_client = get_client_private(
        username=settings.bia_api_username,
        password=settings.bia_api_password,
        api_base_url=settings.bia_api_basepath,
    )
    return private_api_client


def get_local_bia_api_client() -> PrivateApi:
    settings = get_settings()
    api_config = Configuration(host=settings.local_bia_api_basepath)
    private_api = PrivateApi(ApiClient(configuration=api_config))
    try:
        access_token = private_api.login_for_access_token(
            username=settings.local_bia_api_username,
            password=settings.local_bia_api_password,
        )
    except exceptions.UnauthorizedException:
        private_api.register_user(
            api_models.BodyRegisterUser(
                email=settings.local_bia_api_username,
                password_plain=settings.local_bia_api_password,
                secret_token=settings.local_user_create_secret_token,
            )
        )
        access_token = private_api.login_for_access_token(
            username=settings.local_bia_api_username,
            password=settings.local_bia_api_password,
        )
    assert access_token
    api_config.access_token = access_token.access_token
    return private_api


class APIMode(str, Enum):
    """
    Enum for the different persistence modes.
    """

    LOCAL_API = "local_api"
    DEV_API = "dev_api"


def get_client(mode: APIMode):
    if mode == APIMode.DEV_API:
        return get_bia_api_client()
    else:
        return get_local_bia_api_client()
