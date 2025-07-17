import logging
from typing import List, Dict, Optional
from uuid import UUID

from bia_ingest.persistence_strategy import PersistenceStrategy
from bia_ingest.biostudies.submission_parsing_utils import (
    find_files_and_file_lists_in_default_submission,
    attributes_to_dict,
)
from bia_ingest.bia_object_creation_utils import (
    dicts_to_api_models,
)

from bia_ingest.biostudies.api import (
    Submission,
    file_uri,
    File as BioStudiesAPIFile,
)
from bia_shared_datamodels import bia_data_model, semantic_models
from bia_shared_datamodels.package_specific_uuid_creation.shared import (
    create_file_reference_uuid,
)

logger = logging.getLogger("__main__." + __name__)


def get_file_reference_for_default_template_datasets(
    submission: Submission,
    study_uuid: UUID,
    submission_dataset: bia_data_model.Dataset,
    result_summary: dict,
    persister: Optional[PersistenceStrategy] = None,
) -> Dict[str, List[bia_data_model.FileReference]]:
    """
    Return Dict of list of file references in a default template dataset.
    Assumed one dataset per submission, currently.
    """

    all_files = find_files_and_file_lists_in_default_submission(
        submission, result_summary
    )
    if not all_files:
        logger.warning("No files were found.")
        result_summary[submission.accno].__setattr__(
            "Warning",
            "No files were found in deafult template — check submission",
        )

    file_reference_dicts = get_file_reference_dicts_for_submission_dataset(
        submission.accno, study_uuid, submission_dataset, all_files
    )

    file_references = dicts_to_api_models(
        file_reference_dicts,
        bia_data_model.FileReference,
        result_summary[submission.accno],
    )

    if persister:
        persister.persist(file_references)

    fileref_to_datasets = {submission_dataset.title: file_references}

    return fileref_to_datasets


def get_file_reference_dicts_for_submission_dataset(
    accession_id: str,
    study_uuid: UUID,
    submission_dataset: bia_data_model.Dataset,
    files_in_file_list: List[BioStudiesAPIFile],
) -> list[dict]:
    """
    Return list of file references for particular submission dataset
    """

    file_references = []
    for f in files_in_file_list:
        file_path = str(f.path.as_posix())

        uuid, uuid_attribute = create_file_reference_uuid(study_uuid, file_path, f.size)
        file_dict = {
            "uuid": uuid,
            "object_creator": semantic_models.Provenance.bia_ingest,
            "file_path": file_path,
            "format": f.type,
            "size_in_bytes": int(f.size),
            "uri": file_uri(accession_id, f),
            "submission_dataset_uuid": submission_dataset.uuid,
            "version": 0,
        }

        attributes = attributes_to_dict(f.attributes)

        attributes_as_attr_dict = {
            "provenance": semantic_models.Provenance.bia_ingest,
            "name": "attributes_from_biostudies.File",
            "value": {
                "attributes": attributes,
            },
        }
        file_dict["additional_metadata"] = [
            attributes_as_attr_dict,
            uuid_attribute.model_dump(),
        ]
        file_references.append(file_dict)

    return file_references
