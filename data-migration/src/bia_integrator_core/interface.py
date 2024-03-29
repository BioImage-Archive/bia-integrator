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
from .models import BIAImage, BIAStudy, StudyAnnotation
from .config import settings
from .integrator import load_study_with_linked_objects_not_annotated
from .study import get_study, persist_study
from .image import persist_image
from .collection import get_collection, persist_collection
from .representation import persist_image_representation, get_representations

logger = logging.getLogger(__name__)


def get_all_study_identifiers() -> List[str]:
    """Return a list of all accession identifiers of studies."""

    return [fp.stem for fp in settings.studies_dirpath.iterdir()]


def get_image(accession_id: str, image_id: str) -> BIAImage:
    """Get the given image from the study with the given accession identifier."""

    study = load_study_with_linked_objects_not_annotated(accession_id)

    return study.images[image_id]


def get_images_for_study(accession_id) -> List[BIAImage]:
    """Get all images from the study with the given accession identifier."""

    study = load_study_with_linked_objects_not_annotated(accession_id)

    return list(study.images.values())


