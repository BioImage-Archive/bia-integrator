from bia_integrator_core.config import Settings
from bia_integrator_core.models import BIAStudy
from bia_integrator_core.annotation import get_study_annotations, get_image_annotations
from bia_integrator_core.representation import get_representations


def load_study(accession_id: str) -> BIAStudy:
    """Return the study object for the given accession identifier."""

    settings = Settings()
    study_fpath = settings.data_dirpath/"studies"/f"{accession_id}.json"
    bia_study = BIAStudy.parse_file(study_fpath)

    return bia_study


def load_and_annotate_study(accession_id: str) -> BIAStudy:
    """Load the study, merge annotations, and return the result."""

    study = load_study(accession_id)

    study_annotations = get_study_annotations(accession_id)
    annotations_dict = {}
    for annotation in study_annotations:
        annotations_dict[annotation.key] = annotation.value
    study.__dict__.update(annotations_dict)

    for image_id, image in study.images.items():
        image_annotations = get_image_annotations(accession_id, image_id)
        for image_annotation in image_annotations:
            study.images[image_id].__dict__[image_annotation.key] = image_annotation.value
        additional_image_reps = get_representations(accession_id, image_id)
        image.representations += additional_image_reps

    return study