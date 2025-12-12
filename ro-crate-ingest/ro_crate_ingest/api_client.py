from persistence.bia_api_client import BIAAPIClient
from persistence.utils import create_test_user

import logging
from .settings import get_settings

logger = logging.getLogger("__main__." + __name__)


def get_bia_api_client() -> BIAAPIClient:
    settings = get_settings()
    settings.set_to_dev_api()
    private_api_client = BIAAPIClient(settings)
    return private_api_client


def get_local_bia_api_client():
    settings = get_settings()
    settings.set_to_local_api()
    create_test_user(settings)
    private_api_client = BIAAPIClient(settings)
    return private_api_client
