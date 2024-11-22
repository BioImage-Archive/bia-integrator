from bia_ingest.biostudies.generic_conversion_utils import attributes_to_dict
from bia_ingest.config import settings, api_client
from bia_ingest.biostudies.v4.study import get_study
from bia_ingest.biostudies.v4.dataset import get_dataset

from bia_ingest.biostudies.file_reference import get_file_reference_by_dataset

from bia_ingest.biostudies.v4.annotation_method import get_annotation_method_as_map

import logging

logger = logging.getLogger("__main__." + __name__)


def process_submission_fallback(submission, result_summary, process_files, persister):
    study = get_study(submission, result_summary, persister=persister)

    association_object_dict = {}

    datasets = get_dataset(
        submission,
        association_object_dict,
        result_summary,
        persister=persister,
    )

    if process_files:
        get_file_reference_by_dataset(
            submission,
            datasets,
            result_summary,
            persister=persister,
        )
    else:
        logger.info("Skipping file reference creation.")
