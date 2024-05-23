import logging

from pydantic import BaseSettings

from bia_integrator_api.util import simple_client
from bia_integrator_api import models as api_models, exceptions as api_exceptions

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    bia_api_basepath: str = "https://bia-cron-1.ebi.ac.uk:8080"
    bia_username: str = None
    bia_password: str = None
    bia_disable_ssl_host_check: bool = True

    class Config:
        env_file = ".env"


settings = Settings()


rw_client = simple_client(
    api_base_url=settings.bia_api_basepath,
    username=settings.bia_username,
    password=settings.bia_password,
    disable_ssl_host_check=settings.bia_disable_ssl_host_check,
)


def get_study_uuid_by_accession_id(accession_id: str) -> str:
    study_obj = rw_client.get_object_info_by_accession([accession_id])
    study_uuid = study_obj[0].uuid

    return study_uuid
