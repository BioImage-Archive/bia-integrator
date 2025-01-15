import logging

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic.alias_generators import to_snake

from bia_integrator_api import exceptions as api_exceptions
from bia_integrator_api.util import get_client_private
from bia_integrator_api.models import Attribute

logger = logging.getLogger("objects")


# api_base_url = "http://bia-processor-1:8080"
api_base_url = "https://wwwdev.ebi.ac.uk/bioimage-archive/api"


class APIClientSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env')

    username: str = "test@example.com"
    password: str = "test"


client_settings = APIClientSettings()

api_client = get_client_private(
    username=client_settings.username,
    password=client_settings.password,
    api_base_url=api_base_url
)


def store_object_in_api_idempotent(model_object):
    model_name = model_object.__class__.__name__
    # converts, e.g. "BioSample" into "bio_sample"
    model_name_snake = to_snake(model_name)

    get_func_name = 'get_' + model_name_snake
    get_func = getattr(api_client, get_func_name)

    post_func_name = 'post_' + model_name_snake
    post_func = getattr(api_client, post_func_name)

    try:
        get_func(model_object.uuid)
    except api_exceptions.NotFoundException:
        logger.info(f"Storing {model_name} in API")
        post_func(model_object)

def update_object_in_api_version_checked(model_object):
    model_name = model_object.__class__.__name__
    # converts, e.g. "BioSample" into "bio_sample"
    model_name_snake = to_snake(model_name)

    post_func_name = 'post_' + model_name_snake
    post_func = getattr(api_client, post_func_name)    

    logger.info(f"Updating {model_name} in API")
    post_func(model_object)

def update_attributes(existing_attributes: list[Attribute], new_attributes: list[Attribute]) -> list[Attribute]:
   """
   Updates list of attributes, replacing any with matching names.
   
   Args:
       existing_attributes (list[Attribute]): Existing attribute objects
       new_attributes (list[Attribute]): New attribute objects to add/update
       
   Returns:
       list[Attribute]: Updated attribute list with duplicates removed
   """
   existing_dict = {attr.name: attr for attr in existing_attributes}
   new_dict = {attr.name: attr for attr in new_attributes}
   existing_dict.update(new_dict)

   return list(existing_dict.values())
