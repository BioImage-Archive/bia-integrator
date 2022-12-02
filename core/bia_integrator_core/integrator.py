from bia_integrator_core.config import Settings
from bia_integrator_core.models import BIAStudy
from bia_integrator_core.interface import get_study_annotations


def load_study(accession_id: str) -> BIAStudy:
    """Return the study object for the given accession identifier."""

    settings = Settings()
    study_fpath = settings.data_dirpath/"studies"/f"{accession_id}.json"
    bia_study = BIAStudy.parse_file(study_fpath)

    return bia_study


def load_and_integrate(accession_id: str) -> BIAStudy:
    """Load the study, merge annotations, and return the result."""

    study = load_study(accession_id)

    study_annotations = get_study_annotations(accession_id)
    annotations_dict = {}
    for annotation in study_annotations:
        annotations_dict[annotation.key] = annotation.value
    study.__dict__.update(annotations_dict)

    return study