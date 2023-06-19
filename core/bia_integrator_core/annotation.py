import logging
from typing import List, Set

from openapi_client import models as api_models
from .config import settings
from .study import get_study, update_study
from .image import get_image

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
    return study.tags


def get_image_annotations(image_uuid: str) -> List[api_models.ImageAnnotation]:
    """Load image annotations from disk and return."""
    image = get_image(image_uuid)
    return image.annotations
  

def persist_study_annotation(annotation: api_models.StudyAnnotation):
    """Save the given annotation to disk."""

    annotation_dirpath = settings.annotations_dirpath/annotation.accession_id
    annotation_dirpath.mkdir(exist_ok=True, parents=True)

    annotation_fpath = annotation_dirpath/f"{annotation.key}.json"

    logger.info(f"Writing study annotation to {annotation_fpath}")
    with open(annotation_fpath, "w") as fh:
        fh.write(annotation.json(indent=2))


def persist_image_annotation(annotation: api_models.ImageAnnotation):
    """Save the given image annotation to disk."""

    annotation_dirpath = settings.annotations_dirpath/annotation.accession_id/annotation.image_id
    annotation_dirpath.mkdir(exist_ok=True, parents=True)

    annotation_fpath = annotation_dirpath/f"{annotation.key}.json"

    logger.info(f"Writing image annotation to {annotation_fpath}")
    with open(annotation_fpath, "w") as fh:
        fh.write(annotation.json(indent=2))


def add_study_tag(study_accession: str, tag_name: str, tag_value: str):
    """Save the given study tag to disk."""

    study = get_study(study_accession)
    study.tags[tag_name] = tag_value
    update_study(study)