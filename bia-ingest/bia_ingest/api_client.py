from bia_ingest.settings import Settings
from bia_integrator_api.util import get_client_private
import logging

settings = Settings()

logger = logging.getLogger("__main__." + __name__)


def get_bia_api_client():
    private_api_client = get_client_private(
        username=settings.bia_api_username,
        password=settings.bia_api_password,
        api_base_url=settings.bia_api_basepath,
    )
    return private_api_client


def get_local_bia_api_client():
    private_api_client = get_client_private(
        username=settings.local_bia_api_username,
        password=settings.local_bia_api_password,
        api_base_url=settings.local_bia_api_basepath,
    )
    return private_api_client
