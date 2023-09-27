import logging
from typing import List, Optional
from uuid import UUID

from .alias import persist_image_alias
from .annotation import (
    get_study_annotations,
    persist_study_annotation,
    persist_image_annotation,
    add_study_tag,
    get_study_tags,
    get_image_annotations,
)
from openapi_client import models as api_models
from .config import settings
from .integrator import load_and_annotate_study
from .study import get_study, persist_study
from .image import persist_image, get_images
from .collection import get_collection, persist_collection, update_collection, get_collections
from .representation import persist_image_representation, get_representations

logger = logging.getLogger(__name__)


def get_all_study_identifiers() -> List[api_models.BIAStudy]:
    """Return a list of all accession identifiers of studies."""

    raise Exception("TODO: Doesn't exist in api at the moment")

    return [fp.stem for fp in settings.studies_dirpath.iterdir()]

def get_all_studies() -> List[api_models.BIAStudy]:
    studies = settings.api_client.search_studies(limit=10**6)
    return studies

def to_uuid(uuid_or_alternative: str | UUID, fn_fetch_object):
    if type(uuid_or_alternative) is UUID:
        return uuid_or_alternative
    elif type(uuid_or_alternative) is str:
        try:
            uuid = UUID(uuid_or_alternative)
        except ValueError:
            obj_info = fn_fetch_object()
            uuid = obj_info.uuid
        return uuid
    else:
        raise Exception("Should never reach this")

def get_image_by_uuid(image_uuid: str) -> api_models.BIAImage:
    """Get the given image from the study with the given accession identifier."""

    img = settings.api_client.get_image(image_uuid)

    return img

def get_image_by_alias(study_accno: str, img_alias: str) -> api_models.BIAImage:
    images = settings.api_client.get_study_images_by_alias(study_accession=study_accno, aliases=[img_alias])
    assert len(images) == 1

    return images.pop()

def get_bia_user() -> Optional[str]:
    return settings.bia_username

# DELETEME: workaround to deprecate get_images_for_study
get_images_for_study = get_images
