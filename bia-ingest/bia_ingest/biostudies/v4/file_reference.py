import logging
from typing import List, Optional
from uuid import UUID

from bia_ingest.biostudies.submission_parsing_utils import (
    find_datasets_with_file_lists,
    attributes_to_dict,
)
from bia_ingest.bia_object_creation_utils import dict_to_api_model

from bia_ingest.biostudies.api import (
    Submission,
    file_uri,
    flist_from_flist_fname,
    File as BioStudiesAPIFile,
)
from bia_shared_datamodels import bia_data_model, semantic_models
from bia_shared_datamodels.package_specific_uuid_creation.shared import (
    create_file_reference_uuid,
)

logger = logging.getLogger("__main__." + __name__)


def get_file_reference_by_dataset_as_map(
    file_path_to_file_ref_map: dict[str, dict],
    submission: Submission,
    study_uuid: UUID,
    datasets_in_submission: List[bia_data_model.Dataset],
    result_summary: dict,
) -> dict[str, bia_data_model.FileReference] | None:
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

    for dataset_name, dataset in datasets_to_process.items():
        for file_list in dataset_file_list_map[dataset_name]:
            fname: str | list[str] | None = file_list["File List"]
            files_in_fl = flist_from_flist_fname(submission.accno, fname)

            file_path_to_file_ref_map = get_file_reference_dicts_for_submission_dataset(
                submission.accno,
                study_uuid,
                dataset,
                files_in_fl,
                file_path_to_file_ref_map,
                result_summary,
            )

    return file_path_to_file_ref_map


def get_file_reference_dicts_for_submission_dataset(
    accession_id: str,
    study_uuid: UUID,
    submission_dataset: bia_data_model.Dataset,
    files_in_file_list: list[BioStudiesAPIFile],
    file_path_to_file_ref_map: dict[str, UUID],
    result_summary: dict,
) -> dict[UUID, dict]:
    """
    Return list of file references for particular submission dataset
    """

    for f in files_in_file_list:
        file_path = str(f.path.as_posix())
        size_in_bytes = int(f.size)
        uuid, uuid_attribute = create_file_reference_uuid(
            study_uuid, file_path, size_in_bytes
        )

        attributes = attributes_to_dict(f.attributes)
        additional_metadata = [
            {
                "provenance": semantic_models.Provenance.bia_ingest,
                "name": "attributes_from_biostudies.File",
                "value": {
                    "attributes": attributes,
                },
            },
            uuid_attribute,
        ]

        input_image = get_source_image(attributes, file_path_to_file_ref_map)
        if input_image:
            additional_metadata.append(
                {
                    "provenance": semantic_models.Provenance.bia_ingest,
                    "name": "source_image_uuid",
                    "value": {"source_image_uuid": [str(input_image)]},
                }
            )

        file_dict = {
            "uuid": uuid,
            "file_path": file_path,
            "format": f.type,
            "size_in_bytes": size_in_bytes,
            "uri": file_uri(accession_id, f),
            "submission_dataset_uuid": submission_dataset.uuid,
            "version": 0,
            "object_creator": semantic_models.Provenance.bia_ingest,
            "additional_metadata": additional_metadata,
        }

        file_ref = dict_to_api_model(
            file_dict, bia_data_model.FileReference, result_summary[accession_id]
        )

        if file_dict["file_path"] in file_path_to_file_ref_map.keys():
            file_ref = file_ref_update(
                file_ref, file_path_to_file_ref_map[file_dict["file_path"]]
            )

        file_path_to_file_ref_map[file_dict["file_path"]] = file_ref

    return file_path_to_file_ref_map


def get_source_image(
    attributes_from_filelist: dict[str, str | list[str]],
    file_path_to_file_ref_map: dict[str, dict],
) -> Optional[UUID]:
    input_image_uuid = None

    possible_source_image_column_names = [
        "source image",
        "source_image",
        "source image association",
        "source_image_association",
    ]

    for key in attributes_from_filelist.keys():
        if (
            key.lower() in possible_source_image_column_names
            and attributes_from_filelist[key]
        ):
            if isinstance(attributes_from_filelist[key], list):
                raise TypeError(
                    "Expected a single string, but found list, when trying to get Source Image from row in filelist."
                )

            try:
                input_image_uuid = file_path_to_file_ref_map[
                    attributes_from_filelist[key]
                ].uuid
            except KeyError:
                logger.warning(
                    f"Annotation image could not find source image at path: {attributes_from_filelist[key]}"
                )

    return input_image_uuid


def file_ref_update(
    new_file_ref: bia_data_model.FileReference,
    existing_proposed_file_ref: bia_data_model.FileReference,
) -> bia_data_model.FileReference:
    """
    We assume that studies are ingested such that all non-annotation dataset file references are created first, then annotation file references.
    If a file is referenced multiple times, we assume that the first dataset it was ingest with is correct.
    The additional_metadata field is merged between the two objects.
    """

    new_file_ref.submission_dataset_uuid = (
        existing_proposed_file_ref.submission_dataset_uuid
    )

    combined_additional_metadata = existing_proposed_file_ref.additional_metadata
    api_obj_attribute_names = [
        attr.name for attr in existing_proposed_file_ref.additional_metadata
    ]
    for attribute in new_file_ref.additional_metadata:
        if attribute.name not in api_obj_attribute_names:
            combined_additional_metadata.append(attribute)

    new_file_ref.additional_metadata = combined_additional_metadata

    return new_file_ref
