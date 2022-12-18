import logging
from typing import List, Set

from .models import StudyAnnotation, ImageAnnotation, StudyTag
from .config import settings


logger = logging.getLogger(__name__)


def get_study_annotations(accession_id: str) -> List[StudyAnnotation]:
    """Load study annotations from disk and return."""

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


# FIXME - this is all wrong!
def get_study_tags(accession_id: str) -> Set[str]:
    """Load study tags from disk and return."""

    tags_dirpath = settings.annotations_dirpath/accession_id/"tags"

    if tags_dirpath.exists():
        tags_list = [
                StudyTag.parse_file(fp)
                for fp in tags_dirpath.iterdir()
                if fp.is_file()
        ]
    else:
        tags_list = set([])

    return set([tag.value for tag in tags_list]) #type: ignore


def get_image_annotations(accession_id: str, image_id: str) -> List[ImageAnnotation]:
    """Load image annotations from disk and return."""

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

    annotation_dirpath = settings.annotations_dirpath/annotation.accession_id
    annotation_dirpath.mkdir(exist_ok=True, parents=True)

    annotation_fpath = annotation_dirpath/f"{annotation.key}.json"

    logger.info(f"Writing study annotation to {annotation_fpath}")
    with open(annotation_fpath, "w") as fh:
        fh.write(annotation.json(indent=2))


def persist_image_annotation(annotation: ImageAnnotation):
    """Save the given image annotation to disk."""

    annotation_dirpath = settings.annotations_dirpath/annotation.accession_id/annotation.image_id
    annotation_dirpath.mkdir(exist_ok=True, parents=True)

    annotation_fpath = annotation_dirpath/f"{annotation.key}.json"

    logger.info(f"Writing image annotation to {annotation_fpath}")
    with open(annotation_fpath, "w") as fh:
        fh.write(annotation.json(indent=2))


def persist_study_tag(tag: StudyTag):
    """Save the given study tag to disk."""

    tag_dirpath = settings.annotations_dirpath/tag.accession_id/"tags"
    tag_dirpath.mkdir(exist_ok=True, parents=True)

    tag_fpath = tag_dirpath/f"{tag.value}.json"

    logger.info(f"Writing tag to {tag_fpath}")
    with open(tag_fpath, "w") as fh:
        fh.write(tag.json(indent=2))