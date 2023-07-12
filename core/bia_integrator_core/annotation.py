import logging
from typing import List, Set

from openapi_client import models as api_models
from .config import settings
from .study import get_study, update_study
from .image import get_image, update_image

logger = logging.getLogger(__name__)

# TODO: consider removing these and just fetching the study? Same for other things that are now nested
def get_study_annotations(study_accession_id: str) -> List[api_models.StudyAnnotation]:
    """Load study annotations from disk and return."""
    study = get_study(study_accession_id)
    return study.annotations

# FIXME - this is all wrong!
def get_study_tags(study_accession_id: str) -> Set[str]:
    """Load study tags from disk and return."""

    study = get_study(study_accession_id)
    return set(study.tags)


def get_image_annotations(image_uuid: str) -> List[api_models.ImageAnnotation]:
    """Load image annotations from disk and return."""
    image = get_image(image_uuid)
    return image.annotations


def persist_study_annotation(study_uuid: str, annotation: api_models.StudyAnnotation):
    """Save the given annotation to disk."""
    study = get_study(study_uuid)
    study.annotations.append(annotation)
    update_study(study)


def persist_image_annotation(image_uuid: str, annotation: api_models.ImageAnnotation):
    """Save the given image annotation to disk."""

    img = get_image(image_uuid)
    img.annotations.append(annotation)
    update_image(img)

def add_study_tag(study_accession: str, tag_name: str):
    """Save the given study tag to disk."""

    study = get_study(study_accession)
    study.tags.append(tag_name)
    update_study(study)