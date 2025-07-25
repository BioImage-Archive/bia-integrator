import logging
from typing import Optional
from uuid import UUID

from bia_ingest.bia_object_creation_utils import dict_to_api_model
from bia_ingest.persistence_strategy import PersistenceStrategy

from bia_ingest.biostudies.api import Submission
from bia_ingest.biostudies.submission_parsing_utils import (
    attributes_to_dict,
    find_sections_recursive,
)

from bia_shared_datamodels import bia_data_model, semantic_models
from bia_shared_datamodels.package_specific_uuid_creation.biostudies_ingest_uuid_creation import (
    create_dataset_uuid_for_default_bsst_template_submissions,
)

logger = logging.getLogger("__main__." + __name__)


def get_dataset_overview(
    submission: Submission,
    study_uuid: UUID,
    result_summary: dict,
    persister: Optional[PersistenceStrategy] = None,
) -> bia_data_model.Dataset:
    """
    Returns the overview part of a dataset.
    For use only with default template submissions.
    """

    accno = submission.accno

    # Assumptions about study section: always at least one, and can be more than one
    study_section = find_sections_recursive(submission.section, ["Study"])
    num_studies = len(study_section)
    if num_studies > 1:
        logger.warning(
            f"More than one study section found in deafult template: {study_section}"
        )
        result_summary[accno].__setattr__(
            "Warning",
            f"{len(study_section)} studies found in deafult template",
        )

    # Regardless, study_section is returned as a list
    study_section = study_section[0]

    study_attr_dict = attributes_to_dict(study_section.attributes)
    submission_attr_dict = attributes_to_dict(submission.attributes)

    if (num_studies == 1) & ("Title" in study_attr_dict):
        study_title = study_attr_dict["Title"]
    elif "Title" in submission_attr_dict:
        study_title = submission_attr_dict["Title"]
    else:
        logger.warning(f"No title found for dataset for submission: {submission.accno}")
        result_summary[accno].__setattr__(
            "Warning",
            f"No title found for dataset for submission: {submission.accno}",
        )
        study_title = ""

    if "Description" in study_attr_dict:
        description = study_attr_dict["Description"]
    else:
        description = "No description"

    # This should normally be the unique ID of the corresponding Study Component
    # in the pagetab.json file, which the default template does not have.
    uuid, uuid_attribute = create_dataset_uuid_for_default_bsst_template_submissions(
        study_uuid
    )

    model_dict = {
        "uuid": uuid,
        "object_creator": semantic_models.Provenance.bia_ingest,
        "title": study_title,
        "description": description,
        "submitted_in_study_uuid": study_uuid,
        "analysis_method": [],
        "correlation_method": [],
        "example_image_uri": [],
        "version": 0,
        "additional_metadata": [uuid_attribute.model_dump()],
    }

    dataset = dict_to_api_model(
        model_dict,
        bia_data_model.Dataset,
        result_summary[submission.accno],
    )

    if persister and dataset:
        persister.persist([dataset])

    return dataset
