import logging

from .config import settings
from bia_integrator_api import models as api_models
from typing import Optional


logger = logging.getLogger(__name__)

def get_study(accession_id: Optional[str] = None, study_uuid: Optional[str] = None, apply_annotations: bool = False) -> api_models.BIAStudy:
    """Providing an uuid overrides accession_id, as an alternative to get_study_by_* functions"""

    if not study_uuid:
        assert accession_id

        study_obj_info = settings.api_client.get_object_info_by_accession([accession_id])[0]
        study_uuid = study_obj_info.uuid
    bia_study = settings.api_client.get_study(study_uuid, apply_annotations=apply_annotations)

    return bia_study

def persist_study(study: api_models.BIAStudy):
    """Persist the given study to disk."""

    settings.api_client.create_study(study)

def update_study(study: api_models.BIAStudy):
    study.version += 1
    settings.api_client.update_study(study)