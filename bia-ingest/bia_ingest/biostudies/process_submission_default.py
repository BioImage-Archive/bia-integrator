from typing import Optional
import logging

from bia_ingest.biostudies.v4.study import get_study
from bia_ingest.biostudies.v4.dataset import get_dataset_overview
from bia_ingest.biostudies.v4.file_reference import get_file_reference_for_default_template_datasets

from bia_ingest.biostudies.api import Submission
from bia_ingest.persistence_strategy import PersistenceStrategy

logger = logging.getLogger("__main__." + __name__)

def process_submission_default(
    submission: Submission, 
    result_summary: dict, 
    process_files: bool, 
    persister: Optional[PersistenceStrategy] = None
):

    study = get_study(submission, result_summary, persister=persister)
    dataset = get_dataset_overview(submission, study.uuid, result_summary, persister)

    if process_files:
        get_file_reference_for_default_template_datasets(
            submission, study.uuid, dataset, result_summary, persister=persister
        )
    else:
        logger.info("Skipping file reference creation.")
