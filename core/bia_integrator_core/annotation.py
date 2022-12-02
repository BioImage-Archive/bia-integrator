import logging
from typing import List

from bia_integrator_core.models import StudyAnnotation
from bia_integrator_core.config import Settings


logger = logging.getLogger()


def get_study_annotations(accession_id: str) -> List[StudyAnnotation]:

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


def persist_study_annotation(annotation: StudyAnnotation):

    settings = Settings()
    annotation_dirpath = settings.annotations_dirpath/annotation.accession_id
    annotation_dirpath.mkdir(exist_ok=True, parents=True)

    annotation_fpath = annotation_dirpath/f"{annotation.key}.json"

    logger.info(f"Writing study annotation to {annotation_fpath}")
    with open(annotation_fpath, "w") as fh:
        fh.write(annotation.json(indent=2))
