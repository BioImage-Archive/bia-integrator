import logging
from typing import List

from .config import settings
from openapi_client import models as api_models

logger = logging.getLogger(__name__)

def get_filerefs(study_accession_id: str) -> List[api_models.FileReference]:
    study_obj_info = settings.api_client.get_object_info_by_accession_api_object_info_by_accessions_get([study_accession_id]).pop()
    filerefs = settings.api_client.get_study_file_references_api_study_uuid_file_references_get(study_obj_info.uuid)

    return filerefs