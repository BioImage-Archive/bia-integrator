import logging
from pydantic import ValidationError
from typing import List, Dict, Optional
from .utils import (
    dict_to_uuid,
    filter_model_dictionary,
    find_datasets_with_file_lists,
)
from ..biostudies import (
    Submission,
    attributes_to_dict,
    flist_from_flist_fname,
    file_uri,
)
from .. import biostudies  # To make reference to biostudies.File explicit
from bia_shared_datamodels import bia_data_model
from ..persistence_strategy import PersistenceStrategy

logger = logging.getLogger("__main__." + __name__)


def get_file_reference_by_dataset(
    submission: Submission,
    datasets_in_submission: List[
        bia_data_model.ExperimentalImagingDataset
        | bia_data_model.ImageAnnotationDataset
    ],
    result_summary: dict,
    persister: Optional[PersistenceStrategy | None] = None,
) -> Dict[str, List[bia_data_model.FileReference]]:
    """
    Return Dict of list of file references in datasets.
    """

    # Get datasets to process
    titles_from_datasets_in_submission = {
        dataset.title_id for dataset in datasets_in_submission
    }

    file_list_dicts = find_datasets_with_file_lists(submission)

    datasets_to_process = {
        ds.title_id: ds
        for ds in datasets_in_submission
        if ds.title_id in file_list_dicts.keys()
    }

    if not datasets_to_process:
        message = f"""
            Intersection of titles from datasets in submission ({titles_from_datasets_in_submission}) and file lists in submission ( {file_list_dicts.keys()} ) was null - exiting
        """
        logger.warning(message)
        return
    else:
        n_datasets_with_file_lists = len(file_list_dicts.keys())
        n_datasets_in_submission = len(datasets_in_submission)
        if n_datasets_with_file_lists != n_datasets_in_submission:
            message = f"""Number of datasets with file lists ({n_datasets_with_file_lists}) is not equal to the number of datasets passed as input to this function ({n_datasets_in_submission}). Was this deliberate?"""
            logger.warning(message)

    fileref_to_datasets = {}
    for dataset_name, dataset in datasets_to_process.items():
        for file_list_dict in file_list_dicts[dataset_name]:
            if dataset_name not in fileref_to_datasets:
                fileref_to_datasets[dataset_name] = []

            fname = file_list_dict["File List"]
            files_in_fl = flist_from_flist_fname(submission.accno, fname)

            file_references = get_file_reference_for_submission_dataset(
                submission.accno, dataset, files_in_fl, result_summary
            )

            if persister:
                persister.persist(file_references)

            fileref_to_datasets[dataset_name].extend(file_references)

    return fileref_to_datasets


def get_file_reference_for_submission_dataset(
    accession_id: str,
    submission_dataset: bia_data_model.ExperimentalImagingDataset
    | bia_data_model.ImageAnnotationDataset,
    files_in_file_list: List[biostudies.File],
    result_summary: dict,
) -> List[bia_data_model.FileReference]:
    """
    Return list of file references for particular submission dataset
    """

    file_references = []
    for f in files_in_file_list:
        file_dict = {
            "accession_id": accession_id,
            "file_path": str(f.path.as_posix()),
            "size_in_bytes": str(f.size),
        }
        fileref_uuid = dict_to_uuid(
            file_dict, ["accession_id", "file_path", "size_in_bytes"]
        )
        file_dict["uuid"] = fileref_uuid
        file_dict["uri"] = file_uri(accession_id, f)
        file_dict["submission_dataset_uuid"] = submission_dataset.uuid
        file_dict["format"] = f.type
        file_dict["attribute"] = attributes_to_dict(f.attributes)
        file_dict["version"] = 0
        file_dict = filter_model_dictionary(file_dict, bia_data_model.FileReference)

        try:
            file_reference = bia_data_model.FileReference.model_validate(file_dict)
            file_references.append(file_reference)
        except ValidationError:
            logger.warn("Failed to create FileReference")
            logger.debug("Pydantic Validation Error:", exc_info=True)
            result_summary[accession_id].FileReference_ValidationErrorCount += 1

    return file_references
