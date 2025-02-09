from pathlib import Path
import logging

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic.alias_generators import to_snake

from bia_integrator_api import exceptions as api_exceptions
from bia_integrator_api.util import get_client_private

logger = logging.getLogger("objects")


env_file_path = f"{Path(__file__).parent.parent / '.env'}"


class APIClientSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_file_path, extra="allow")

    # TODO: Discuss standardising env variables across all bia-integrator subpackages
    api_base_url: str = "https://wwwdev.ebi.ac.uk/bioimage-archive/api"
    bia_api_username: str = "test@example.com"
    bia_api_password: str = "test"


client_settings = APIClientSettings()

api_client = get_client_private(
    username=client_settings.bia_api_username,
    password=client_settings.bia_api_password,
    api_base_url=client_settings.api_base_url,
)


def store_object_in_api_idempotent(model_object):
    model_name = model_object.__class__.__name__
    # converts, e.g. "BioSample" into "bio_sample"
    model_name_snake = to_snake(model_name)

    get_func_name = "get_" + model_name_snake
    get_func = getattr(api_client, get_func_name)

    post_func_name = "post_" + model_name_snake
    post_func = getattr(api_client, post_func_name)

    try:
        get_func(model_object.uuid)
    except api_exceptions.NotFoundException:
        logger.info(f"Storing {model_name} with UUID {model_object.uuid} in API")
        post_func(model_object)
