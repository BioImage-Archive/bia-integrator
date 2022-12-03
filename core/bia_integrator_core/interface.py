import logging
from typing import List

from bia_integrator_core.annotation import get_study_annotations, persist_study_annotation
from bia_integrator_core.models import BIAImage, BIAStudy, StudyAnnotation
from bia_integrator_core.config import Settings
from bia_integrator_core.integrator import load_and_annotate_study
from .study import get_study

logger = logging.getLogger(__name__)


def get_all_study_identifiers() -> List[str]:
    """Return a list of all accession identifiers of studies."""

    settings = Settings()

    return [fp.stem for fp in settings.studies_dirpath.iterdir()]


def get_image(accession_id: str, image_id: str) -> BIAImage:
    """Get the given image from the study with the given accession identifier."""

    study = load_and_annotate_study(accession_id)

    return study.images[image_id]


def get_images_for_study(accession_id) -> List[BIAImage]:
    """Get all images from the study with the given accession identifier."""

    study = load_and_annotate_study(accession_id)

    return list(study.images.values())


