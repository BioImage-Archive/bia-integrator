import logging
from enum import Enum

from bia_integrator_api.api import PrivateApi
from persistence.bia_api_client import BIAAPIClient
from persistence.utils import create_test_user

from annotation_data_converter.settings import get_settings

logger = logging.getLogger(__name__)


_api_clients = {}


class ApiTarget(str, Enum):
    """API to point client to"""

    prod = "prod"
    local = "local"


def get_api_client(target: ApiTarget) -> PrivateApi:
    """Return client pointing to prod or local API."""
    if target not in _api_clients:
        if target == ApiTarget.prod:
            _api_clients[target] = get_bia_api_client()
        elif target == ApiTarget.local:
            _api_clients[target] = get_local_bia_api_client()
        else:
            raise ValueError(f"Unknown API target: {target}")
    
    return _api_clients[target]


def get_bia_api_client() -> BIAAPIClient:
    settings = get_settings()
    settings.set_to_dev_api()
    return BIAAPIClient(settings)


def get_local_bia_api_client() -> BIAAPIClient:
    settings = get_settings()
    settings.set_to_local_api()
    create_test_user(settings)
    return BIAAPIClient(settings)
