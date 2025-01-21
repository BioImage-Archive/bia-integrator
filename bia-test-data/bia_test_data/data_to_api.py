from pathlib import Path
from dotenv import dotenv_values
from bia_integrator_api.api import PrivateApi
from bia_integrator_api import Configuration, ApiClient, exceptions
from pydantic.alias_generators import to_snake
import bia_integrator_api.models as api_models


def test_user_creation_details() -> dict:
    env_path = Path(__file__).parents[2] / "api" / ".env_compose"
    container_env = dotenv_values(env_path)
    user_creation_token = container_env.get("USER_CREATE_SECRET_TOKEN")
    user_creation_details = {
        "email": "test@example.com",
        "password_plain": "test",
        "secret_token": user_creation_token,
    }
    return user_creation_details


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
        private_api.register_user(user_dict)
        access_token = private_api.login_for_access_token(
            username=user_dict["email"], password=user_dict["password_plain"]
        )

    assert access_token

    api_config.access_token = access_token.access_token

    return private_api


def add_objects_to_api(api_base_url, object_list=list[dict]):
    private_client = get_object_creation_client(api_base_url)

    # TODO: write clever function for ordering objects correctly by type & dependencies: 

    for bia_object_dict in object_list:
        bia_object_type = bia_object_dict["model"]["type_name"]
        post_method_name = "post_" + to_snake(bia_object_type)
        post_function = private_client.__getattribute__(post_method_name)
        get_method_name = "get_" + to_snake(bia_object_type)
        get_function = private_client.__getattribute__(get_method_name)
        api_obj = getattr(api_models, bia_object_type).model_validate(bia_object_dict)

        try:
            object_from_api = get_function(bia_object_dict["uuid"])
        except exceptions.NotFoundException:
            object_from_api = None

        if object_from_api:
            assert object_from_api == api_obj
        else:
            post_function(api_obj)
