import logging
from pydantic import ValidationError
from typing import Optional
from ...cli_logging import (
    log_failed_model_creation,
    log_model_creation_count,
)
from bia_ingest.biostudies.api import Submission
from ...bia_object_creation_utils import filter_model_dictionary
from ...persistence_strategy import PersistenceStrategy
from bia_shared_datamodels import bia_data_model

from ..v4.dataset import generate_dataset_uuid

logger = logging.getLogger("__main__." + __name__)


def get_dataset(
    submission: Submission,
    study: bia_data_model.Study,
    result_summary: dict,
    persister: Optional[PersistenceStrategy] = None,
) -> list[bia_data_model.Dataset]:

    model_dict = {
        "title_id": "Dataset for: " + study.title,
        "description": None,
        "submitted_in_study_uuid": study.uuid,
        "analysis_method": [],
        "correlation_method": [],
        "example_image_uri": [],
        "version": 0,
        "attribute": [],
    }
    model_dict["accession_id"] = submission.accno
    model_dict["uuid"] = generate_dataset_uuid(model_dict)
    model_dict = filter_model_dictionary(model_dict, bia_data_model.Dataset)

    try:

        dataset = bia_data_model.Dataset.model_validate(model_dict)
        log_model_creation_count(
            bia_data_model.Dataset, 1, result_summary[submission.accno]
        )

    except ValidationError:
        log_failed_model_creation(
            bia_data_model.Dataset, result_summary[submission.accno]
        )

    if persister and dataset:
        persister.persist(dataset)

    return [dataset]
