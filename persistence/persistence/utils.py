import os
from pathlib import Path

import bia_integrator_api.models as api_models
from bia_integrator_api import ApiClient, Configuration, exceptions
from bia_integrator_api.api import PrivateApi
from dotenv import dotenv_values

from persistence.settings import Settings


def set_dev_settings_to_local():
    # Safety function when running tests to make sure you can't accidentally push to dev.
    # Doesn't use the settings class as this should be run prior the first call of get_settings()
    # E.g. using pytest_configure
    env_settings = dotenv_values(str(Path(__file__).parents[1] / ".env_template"))
    os.environ["dev_api_basepath"] = env_settings["local_bia_api_basepath"]
    os.environ["dev_api_username"] = env_settings["local_bia_api_username"]
    os.environ["dev_api_password"] = env_settings["local_bia_api_password"]


def create_test_user(settings: Settings) -> None:
    api_config = Configuration(host=settings.local_bia_api_basepath)
    private_api = PrivateApi(ApiClient(configuration=api_config))
    user_creation_token = settings.local_user_create_secret_token
    user_creation_details = {
        "email": settings.local_bia_api_username,
        "password_plain": settings.local_bia_api_password,
        "secret_token": user_creation_token,
    }
    try:
        # First check if user is already created by trying to log
        access_token = private_api.login_for_access_token(
            username=user_creation_details["email"],
            password=user_creation_details["password_plain"],
        )
    except exceptions.UnauthorizedException:
        private_api.register_user(api_models.BodyRegisterUser(**user_creation_details))
        access_token = private_api.login_for_access_token(
            username=user_creation_details["email"],
            password=user_creation_details["password_plain"],
        )
    assert access_token
