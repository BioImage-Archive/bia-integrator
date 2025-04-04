from pathlib import Path
import logging

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic.alias_generators import to_snake

import bia_integrator_api.models as api_models
from bia_integrator_api import exceptions as api_exceptions
from bia_integrator_api.util import get_client_private

logger = logging.getLogger("objects")


env_file_path = f"{Path(__file__).parent.parent / '.env'}"


class APIClientSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_file_path, extra="allow")

    # TODO: Discuss standardising env variables across all bia-integrator subpackages
    # api_base_url: str = "https://wwwdev.ebi.ac.uk/bioimage-archive/api"
    api_base_url: str = "http://localhost:8080"
    bia_api_username: str = "test@example.com"
    bia_api_password: str = "test"


client_settings = APIClientSettings()

api_client = get_client_private(
    username=client_settings.bia_api_username,
    password=client_settings.bia_api_password,
    api_base_url=client_settings.api_base_url,
)


# def store_object_in_api_idempotent(model_object):
#    model_name = model_object.__class__.__name__
#    # converts, e.g. "BioSample" into "bio_sample"
#    model_name_snake = to_snake(model_name)
#
#    get_func_name = "get_" + model_name_snake
#    get_func = getattr(api_client, get_func_name)
#
#    post_func_name = "post_" + model_name_snake
#    post_func = getattr(api_client, post_func_name)
#
#    try:
#        get_func(model_object.uuid)
#    except api_exceptions.NotFoundException:
#        logger.info(f"Storing {model_name} with UUID {model_object.uuid} in API")
#        post_func(model_object)


def store_object_in_api_idempotent(model_object):
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


def update_object_in_api_idempotent(model_object):
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
