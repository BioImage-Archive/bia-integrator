import os
from pathlib import Path

import bia_integrator_api.models as api_models
import pytest
from bia_integrator_api import ApiClient, Configuration, exceptions
from bia_integrator_api.api import PrivateApi
from bia_shared_datamodels import bia_data_model, mock_objects
from dotenv import dotenv_values

from curation.settings import get_settings


def test_user_creation_details() -> dict[str, str]:

    user_creation_token = get_settings().local_user_create_secret_token
    user_creation_details = {
        "email": "test@example.com",
        "password_plain": "test",
        "secret_token": user_creation_token,
    }
    return user_creation_details


def pytest_configure(config: pytest.Config):
    env_settings = dotenv_values(str(Path(__file__).parents[1] / ".env_template"))
    os.environ["bia_api_basepath"] = env_settings["local_bia_api_basepath"]
    os.environ["bia_api_username"] = env_settings["local_bia_api_username"]
    os.environ["bia_api_password"] = env_settings["local_bia_api_password"]


def get_object_creation_client(
    api_base_url: str,
) -> PrivateApi:
    api_config = Configuration(host=api_base_url)
    private_api = PrivateApi(ApiClient(configuration=api_config))
    user_dict = test_user_creation_details()
    try:
        access_token = private_api.login_for_access_token(
            username=user_dict["email"], password=user_dict["password_plain"]
        )
    except exceptions.UnauthorizedException:
        private_api.register_user(api_models.BodyRegisterUser(**user_dict))
        access_token = private_api.login_for_access_token(
            username=user_dict["email"],
            password=user_dict["password_plain"],
        )

    assert access_token

    api_config.access_token = access_token.access_token

    return private_api


@pytest.fixture(scope="session")
def private_client() -> PrivateApi:
    setttings = get_settings()
    return get_object_creation_client(setttings.local_bia_api_basepath)


@pytest.fixture(scope="session")
def any_api_object(private_client: PrivateApi) -> api_models.Study:
    study_dict = mock_objects.get_study_dict()
    study_object = api_models.Study.model_validate_json(
        bia_data_model.Study(**study_dict).model_dump_json()
    )
    try:
        private_client.post_study(study_object)
    except exceptions.ApiException as e:
        if e.reason == "Conflict":
            api_copy = private_client.get_study(str(study_object.uuid))
            study_object.version = api_copy.version + 1
            private_client.post_study(study_object)
        else:
            raise e
    return study_object
