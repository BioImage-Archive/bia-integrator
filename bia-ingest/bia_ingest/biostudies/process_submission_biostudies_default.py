from bia_ingest.biostudies.v4.study import get_study
from bia_ingest.biostudies.bsst_default.dataset import get_dataset


import logging

logger = logging.getLogger("__main__." + __name__)


def process_submission_biostudies_default(
    submission, result_summary, process_files, persister
):
    study = get_study(submission, result_summary, persister=persister)

    datasets = get_dataset(
        submission,
        study,
        result_summary,
        persister=persister,
    )
