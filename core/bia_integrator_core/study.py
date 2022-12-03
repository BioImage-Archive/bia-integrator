import logging

from .config import Settings
from .models import BIAStudy


logger = logging.getLogger(__name__)


def persist_study(study: BIAStudy):
    """Persist the given study to disk."""

    settings = Settings()
    studies_dirpath = settings.studies_dirpath
    studies_dirpath.mkdir(exist_ok=True, parents=True)

    study_fpath = studies_dirpath/f"{study.accession_id}.json"
    logger.info(f"Writing collection to {study_fpath}")

    with open(study_fpath, "w") as fh:
        fh.write(study.json(indent=2))
