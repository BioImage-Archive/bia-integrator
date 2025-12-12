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
from persistence.bia_api_client import BIAAPIClient
from persistence.utils import create_test_user


logger = logging.getLogger("__main__." + __name__)


class ApiTarget(str, Enum):
    """API to point client to"""

    prod = "prod"
    local = "local"


def get_api_client(target: ApiTarget) -> PrivateApi:
    """Return client pointing to prod or local API using Singleton pattern."""

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


def get_bia_api_client() -> BIAAPIClient:
    settings = get_settings()
    settings.set_to_dev_api()
    private_api_client = BIAAPIClient(settings)
    return private_api_client


def get_local_bia_api_client() -> BIAAPIClient:
    settings = get_settings()
    settings.set_to_local_api()
    create_test_user(settings)
    private_api_client = BIAAPIClient(settings)
    return private_api_client


def store_object_in_api_idempotent(api_client: BIAAPIClient, model_object: BaseModel):
    api_client.put_object(model_object)


def update_object_in_api_idempotent(api_client: BIAAPIClient, model_object: BaseModel):
    api_client.update_existing_object(model_object)
