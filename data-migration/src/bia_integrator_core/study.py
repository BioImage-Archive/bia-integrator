import logging

from .config import settings
from .models import BIAStudy


logger = logging.getLogger(__name__)

def get_study(accession_id: str) -> BIAStudy:
    """Return the study object for the given accession identifier."""

    study_fpath = settings.data_dirpath/"studies"/f"{accession_id}.json"
    bia_study = BIAStudy.parse_file(study_fpath)

    return bia_study


def persist_study(study: BIAStudy):
    """Persist the given study to disk."""

    studies_dirpath = settings.studies_dirpath
    studies_dirpath.mkdir(exist_ok=True, parents=True)

    study_fpath = studies_dirpath/f"{study.accession_id}.json"
    logger.info(f"Writing study to {study_fpath}")

    with open(study_fpath, "w") as fh:
        fh.write(study.json(indent=2))
