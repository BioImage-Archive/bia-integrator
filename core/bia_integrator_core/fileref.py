import logging
from typing import List

from .config import settings
from bia_integrator_api import models as api_models

logger = logging.getLogger(__name__)

def persist_fileref(fileref: api_models.FileReference):
    """Persist the fileref to disk."""

    persist_filerefs([fileref])

def persist_filerefs(filerefs: list[api_models.FileReference]):
    """Persist the filerefs to disk."""

    logger.info(f"Writing fileref(s) to {filerefs[0].study_uuid}")
    settings.api_client.create_file_references(filerefs)

def update_fileref(fileref: api_models.FileReference):
    """Persist the fileref to disk."""

    fileref.version += 1
    settings.api_client.update_file_reference(fileref)

def get_filerefs(study_accession_id: str, limit: int = 10**6, apply_annotations: bool = False) -> List[api_models.FileReference]:
    """Return all filerefs stored on disk for the given accession."""
    
    study_obj_info = settings.api_client.get_object_info_by_accession([study_accession_id]).pop()
    filerefs = settings.api_client.get_study_file_references(study_obj_info.uuid, limit=limit, apply_annotations=apply_annotations)

    return filerefs

def get_fileref(fileref_uuid: str, apply_annotations: bool = False) -> api_models.FileReference:
    """Return all filerefs stored on disk for the given accession."""
    
    fileref = settings.api_client.get_file_reference(fileref_uuid, apply_annotations=apply_annotations)

    return fileref
