import logging
from typing import List, Dict, Optional
from uuid import UUID

from bia_ingest.persistence_strategy import PersistenceStrategy
from bia_ingest.biostudies.submission_parsing_utils import (
    find_datasets_with_file_lists,
    attributes_to_dict,
)
from bia_ingest.bia_object_creation_utils import (
    dicts_to_api_models,
)

from bia_ingest.biostudies.api import (
    Submission,
    file_uri,
    flist_from_flist_fname,
    File as BioStudiesAPIFile,
)
from bia_shared_datamodels import bia_data_model, semantic_models
from bia_shared_datamodels.uuid_creation import create_file_reference_uuid

logger = logging.getLogger("__main__." + __name__)


def get_file_reference_by_dataset(
    submission: Submission,
    study_uuid: UUID,
    datasets_in_submission: List[bia_data_model.Dataset],
    result_summary: dict,
    persister: Optional[PersistenceStrategy] = None,
) -> Dict[str, List[bia_data_model.FileReference]]:
    """
    Return Dict of list of file references in datasets.
    """

    titles_from_datasets_in_submission = {
        dataset.title for dataset in datasets_in_submission
    }
    dataset_file_list_map = find_datasets_with_file_lists(submission)

    datasets_to_process = {
        ds.title: ds
        for ds in datasets_in_submission
        if ds.title in dataset_file_list_map.keys()
    }

    if not datasets_to_process:
        message = f"""
            Intersection of titles from datasets in submission ({titles_from_datasets_in_submission}) and file lists in submission ( {dataset_file_list_map.keys()} ) was null - exiting
        """
        logger.warning(message)
        return
    else:
        n_datasets_with_file_lists = len(dataset_file_list_map.keys())
        n_datasets_in_submission = len(datasets_in_submission)
        if n_datasets_with_file_lists != n_datasets_in_submission:
            message = f"""Number of datasets with file lists ({n_datasets_with_file_lists}) is not equal to the number of datasets passed as input to this function ({n_datasets_in_submission}). Was this deliberate?"""
            logger.warning(message)

    fileref_to_datasets = {}
    for dataset_name, dataset in datasets_to_process.items():
        for file_list in dataset_file_list_map[dataset_name]:
            if dataset_name not in fileref_to_datasets:
                fileref_to_datasets[dataset_name] = []

            fname = file_list["File List"]
            files_in_fl = flist_from_flist_fname(submission.accno, fname)

            file_reference_dicts = get_file_reference_dicts_for_submission_dataset(
                submission.accno, study_uuid, dataset, files_in_fl
            )

            file_references = dicts_to_api_models(
                file_reference_dicts,
                bia_data_model.FileReference,
                result_summary[submission.accno],
            )

            if persister:
                persister.persist(file_references)

            fileref_to_datasets[dataset_name].extend(file_references)

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
        size_in_bytes = int(f.size)
        uuid_unique_input = f"{file_path}{size_in_bytes}"
        file_dict = {
            "uuid": create_file_reference_uuid(study_uuid, uuid_unique_input),
            "file_path": file_path,
            "format": f.type,
            "size_in_bytes": size_in_bytes,
            "uri": file_uri(accession_id, f),
            "submission_dataset_uuid": submission_dataset.uuid,
            "version": 0,
            "object_creator": "bia_ingest",
        }

        attributes = attributes_to_dict(f.attributes)

        attributes_as_attr_dict = {
            "provenance": semantic_models.Provenance("bia_ingest"),
            "name": "attributes_from_biostudies.File",
            "value": {
                "attributes": attributes,
            },
        }
        file_dict["additional_metadata"] = [
            attributes_as_attr_dict,
        ]
        file_dict["additional_metadata"].append(
            {
                "provenance": "bia_ingest",
                "name": "uuid_unique_input",
                "value": {"uuid_unique_input": uuid_unique_input},
            }
        )
        file_references.append(file_dict)

    return file_references
