from bia_ingest.biostudies.v4.study import get_study
from bia_ingest.biostudies.v4.dataset import get_dataset_overview

from bia_ingest.biostudies.v4.file_reference import get_file_reference_for_default_template_datasets

from bia_ingest.biostudies.submission_parsing_utils import find_files_in_submission

import logging

logger = logging.getLogger("__main__." + __name__)

def process_submission_default(submission, result_summary, process_files, persister):

    study = get_study(submission, result_summary, persister=persister)
    study_uuid = study.uuid

    dataset = get_dataset_overview(submission, study.uuid, result_summary, persister)

    if process_files:
        get_file_reference_for_default_template_datasets(
            submission, study_uuid, dataset, result_summary, persister=persister
        )
    else:
        logger.info("Skipping file reference creation.")
