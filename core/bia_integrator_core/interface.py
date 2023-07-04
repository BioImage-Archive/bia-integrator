import logging
from typing import List
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
from .collection import get_collection, persist_collection, update_collection
from .representation import persist_image_representation, get_representations

logger = logging.getLogger(__name__)


def get_all_study_identifiers() -> List[str]:
    """Return a list of all accession identifiers of studies."""

    raise Exception("TODO: Doesn't exist in api at the moment")

    return [fp.stem for fp in settings.studies_dirpath.iterdir()]

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

def get_image(accession_id: str, image_uuid: str) -> api_models.BIAImage:
    """Get the given image from the study with the given accession identifier."""

    study = load_and_annotate_study(accession_id)

    images_with_accession = [image for image in study.images if image.uuid == image_uuid]
    assert len(images_with_accession) == 1

    return images_with_accession[0]

# DELETEME: workaround to deprecate get_images_for_study
get_images_for_study = get_images
