from bia_integrator_core.models import BIAStudy
from bia_integrator_core.annotation import get_study_annotations, get_image_annotations
from bia_integrator_core.representation import get_representations
from bia_integrator_core.study import get_study


def load_and_annotate_study(accession_id: str) -> BIAStudy:
    """Load the study, merge annotations, and return the result."""

    study = get_study(accession_id)

    study_annotations = get_study_annotations(accession_id)
    study_field_names = [f.name for f in BIAStudy.__fields__.values()]
    for annotation in study_annotations:
        if annotation.key in study_field_names:
            study.__dict__[annotation.key] = annotation.value
        else:
            study.attributes[annotation.key] = annotation.value

    for image_id, image in study.images.items():
        image_annotations = get_image_annotations(accession_id, image_id)
        for image_annotation in image_annotations:
            study.images[image_id].__dict__[image_annotation.key] = image_annotation.value
        additional_image_reps = get_representations(accession_id, image_id)
        image.representations += additional_image_reps

    return study