import logging
from typing import List

from .alias import persist_image_alias, get_aliases
from .annotation import (
    get_study_annotations,
    persist_study_annotation,
    persist_image_annotation,
    persist_study_tag,
    get_study_tags,
    get_image_annotations,
)
from openapi_client import models as api_models
from .config import settings
from .integrator import load_and_annotate_study
from .study import get_study, persist_study
from .image import persist_image
from .collection import get_collection, persist_collection
from .representation import persist_image_representation, get_representations

logger = logging.getLogger(__name__)


def get_all_study_identifiers() -> List[str]:
    """Return a list of all accession identifiers of studies."""

    raise Exception("TODO: Doesn't exist in api at the moment")

    return [fp.stem for fp in settings.studies_dirpath.iterdir()]


def get_image(accession_id: str, image_uuid: str) -> api_models.BIAImage:
    """Get the given image from the study with the given accession identifier."""

    study = load_and_annotate_study(accession_id)

    images_with_accession = [image for image in study.images if image.uuid == image_uuid]
    assert len(images_with_accession) == 1

    return images_with_accession[0]


def get_images_for_study(accession_id: str) -> List[api_models.BIAImage]:
    """Get all images from the study with the given accession identifier."""

    study = load_and_annotate_study(accession_id)

    return study.images


