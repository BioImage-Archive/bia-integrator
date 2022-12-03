import logging
from typing import List

from .models import StudyAnnotation, ImageAnnotation
from .config import Settings


logger = logging.getLogger(__name__)


def get_study_annotations(accession_id: str) -> List[StudyAnnotation]:
    """Load study annotations from disk and return."""
    settings = Settings()

    study_annotations_dirpath = settings.annotations_dirpath/accession_id

    if study_annotations_dirpath.exists():
        study_annotations = [
                StudyAnnotation.parse_file(fp)
                for fp in study_annotations_dirpath.iterdir()
                if fp.is_file()
        ]
    else:
        study_annotations = []

    return study_annotations


def get_image_annotations(accession_id: str, image_id: str) -> List[ImageAnnotation]:
    """Load image annotations from disk and return."""

    settings = Settings()
    image_annotations_dirpath = settings.annotations_dirpath/accession_id/image_id
    
    if image_annotations_dirpath.exists():
        image_annotations = [
            ImageAnnotation.parse_file(fp)
            for fp in image_annotations_dirpath.iterdir()
            if fp.is_file()
        ]
    else:
        image_annotations = []

    return image_annotations
  

def persist_study_annotation(annotation: StudyAnnotation):
    """Save the given annotation to disk."""

    settings = Settings()
    annotation_dirpath = settings.annotations_dirpath/annotation.accession_id
    annotation_dirpath.mkdir(exist_ok=True, parents=True)

    annotation_fpath = annotation_dirpath/f"{annotation.key}.json"

    logger.info(f"Writing study annotation to {annotation_fpath}")
    with open(annotation_fpath, "w") as fh:
        fh.write(annotation.json(indent=2))


def persist_image_annotation(annotation: ImageAnnotation):
    """Save the given image annotation to disk."""

    settings = Settings()
    annotation_dirpath = settings.annotations_dirpath/annotation.accession_id/annotation.image_id
    annotation_dirpath.mkdir(exist_ok=True, parents=True)

    annotation_fpath = annotation_dirpath/f"{annotation.key}.json"

    logger.info(f"Writing image annotation to {annotation_fpath}")
    with open(annotation_fpath, "w") as fh:
        fh.write(annotation.json(indent=2))