import logging

from .config import settings
from .models import BIAStudy


logger = logging.getLogger(__name__)

def get_study(accession_id: str) -> BIAStudy:
    """Return the study object for the given accession identifier."""

    bia_study = settings.api_client.get_study_api_study_uuid_get(accession_id)

    return bia_study


def persist_study(study: BIAStudy):
    """Persist the given study to disk."""

    settings.api_client.create_study_api_private_study_post(study)
