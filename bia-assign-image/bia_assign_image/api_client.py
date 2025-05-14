# Originally from bia-ingest
from enum import Enum
from pydantic.alias_generators import to_snake
from bia_integrator_api.util import get_client_private
from bia_integrator_api import Configuration, ApiClient
from bia_integrator_api import exceptions as api_exceptions
from bia_integrator_api.api import PrivateApi
import bia_integrator_api.models as api_models
import logging
from bia_assign_image.settings import settings

logger = logging.getLogger("__main__." + __name__)


class ApiTarget(str, Enum):
    """API to point client to"""

    prod = "prod"
    local = "local"


def get_api_client(target: ApiTarget) -> PrivateApi:
    """Return client pointing to prod or local API"""

    if target == ApiTarget.prod:
        return get_bia_api_client()
    elif target == ApiTarget.local:
        return get_local_bia_api_client()
    else:
        raise Exception(f"No API target corresponds to profile {target} ")


def get_bia_api_client() -> PrivateApi:
    private_api_client = get_client_private(
        username=settings.bia_api_username,
        password=settings.bia_api_password,
        api_base_url=settings.bia_api_basepath,
    )
    return private_api_client


def get_local_bia_api_client() -> PrivateApi:
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


# This function is based on similar ones in from bia-converter.bia_api_client
# However, there, storing and updating are separate.
# TODO: Do we want separate functions for storing and updating?
# TODO: Should this function be in a separate utils.py?


def store_object_in_api_idempotent(api_client, model_object):
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
    equivalent_api_class = getattr(api_models, model_object.model.type_name)
    equivalent_api_object = equivalent_api_class.model_validate_json(
        model_object.model_dump_json()
    )

    try:
        api_copy_of_object = get_func(model_object_uuid)
    except api_exceptions.NotFoundException:
        logger.info(f"Storing {model_name} with UUID {model_object_uuid} in API")
        post_func(equivalent_api_object)
        return

    # Negate the difference in value of the version field.
    # We want to compare differences in actual values (we can have
    # different versions of exactly the same object)
    equivalent_api_object.version = api_copy_of_object.version
    if equivalent_api_object == api_copy_of_object:
        return
    else:
        equivalent_api_object.version = api_copy_of_object.version + 1

        logger.info(f"Updating {model_name} with UUID {model_object_uuid} in API")
        post_func(equivalent_api_object)
