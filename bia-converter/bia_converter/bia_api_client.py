import logging
from enum import Enum

from pydantic.alias_generators import to_snake
from pydantic import BaseModel

import bia_integrator_api.models as api_models
from bia_integrator_api import exceptions as api_exceptions
from bia_integrator_api.util import get_client_private
from bia_integrator_api import Configuration, ApiClient
from bia_integrator_api.api import PrivateApi
from bia_converter.settings import get_settings

logger = logging.getLogger("__main__." + __name__)


class ApiTarget(str, Enum):
    """API to point client to"""

    prod = "prod"
    local = "local"


def get_api_client(target: ApiTarget) -> PrivateApi:
    """Return client pointing to prod or local API using Singleton pattern."""
    print(get_api_client._instances)

    def get_instance(target: ApiTarget):
        if target not in get_api_client._instances:
            if target == ApiTarget.prod:
                get_api_client._instances[target] = get_bia_api_client()
            elif target == ApiTarget.local:
                get_api_client._instances[target] = get_local_bia_api_client()
            else:
                raise Exception(f"No API target corresponds to profile {target} ")
        return get_api_client._instances[target]
    return get_instance(target) 
# Initialise the instances dictionary for the singleton pattern
get_api_client._instances = {}

    

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
    except api_exceptions.UnauthorizedException:
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


def store_object_in_api_idempotent(api_client: PrivateApi, model_object: BaseModel):
    model_name = model_object.__class__.__name__
    # converts, e.g. "BioSample" into "bio_sample"
    model_name_snake = to_snake(model_name)

    get_func_name = "get_" + model_name_snake
    get_func = getattr(api_client, get_func_name)

    post_func_name = "post_" + model_name_snake
    post_func = getattr(api_client, post_func_name)

    # Convert uuid to string to prevent validation issues with API get methods
    model_object_uuid = f"{model_object.uuid}"

    # Convert the bia_data_model object to its API equivalent as there are slight differences
    # in same models defined in bia_shared_models and api subpackages (e.g. Specimen)
    equivalent_api_class = getattr(api_models, model_name)
    equivalent_api_object = equivalent_api_class.model_validate_json(
        model_object.model_dump_json()
    )

    try:
        api_copy_of_object = get_func(model_object_uuid)
    except api_exceptions.NotFoundException:
        logger.info(f"Storing {model_name} with UUID {model_object_uuid} in API")
        post_func(equivalent_api_object)
        return

    if equivalent_api_object == api_copy_of_object:
        return
    else:
        model_object.version = api_copy_of_object.version + 1

        logger.info(f"Updating {model_name} with UUID {model_object_uuid} in API")
        post_func(model_object)


def update_object_in_api_idempotent(api_client: PrivateApi, model_object: BaseModel):
    model_name = model_object.__class__.__name__
    # converts, e.g. "BioSample" into "bio_sample"
    model_name_snake = to_snake(model_name)

    get_func_name = "get_" + model_name_snake
    get_func = getattr(api_client, get_func_name)

    try:
        api_copy_of_object = get_func(model_object.uuid)
    except api_exceptions.NotFoundException as e:
        logger.error(
            f"Cannot retrieve {model_name} with UUID {model_object.uuid} from API for update"
        )
        raise (e)

    # Convert the bia_data_model object to its API equivalent
    equivalent_api_class = getattr(api_models, model_object.model.type_name)
    equivalent_api_object = equivalent_api_class.model_validate_json(
        model_object.model_dump_json()
    )

    if equivalent_api_object == api_copy_of_object:
        return
    else:
        model_object.version += 1
        post_func_name = "post_" + model_name_snake
        post_func = getattr(api_client, post_func_name)

        logger.info(f"Updating {model_name} with UUID {model_object.uuid} in API")
        post_func(model_object)
