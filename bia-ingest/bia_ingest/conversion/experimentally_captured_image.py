import logging
from uuid import UUID
from typing import List, Dict, Any
from .utils import (
    dicts_to_api_models,
    dict_to_uuid,
    filter_model_dictionary,
    merge_dicts,
)
from ..image_utils.image_utils import (
    get_image_extension,
    extension_in_bioformats_single_file_formats_list,
)
from bia_ingest.conversion.experimental_imaging_dataset import (
    get_experimental_imaging_dataset,
)
from bia_ingest.conversion.file_reference import get_file_reference_by_dataset
from ..biostudies import (
    Submission,
)

from bia_ingest.persistence_strategy import PersistenceStrategy

from bia_shared_datamodels import bia_data_model


logger = logging.getLogger("__main__." + __name__)


# TODO: Discuss whether to deprecate this function. We will not need it
#       for our current workflow
def get_all_experimentally_captured_images(
    submission: Submission, result_summary: dict, persist_artefacts=False
) -> List[bia_data_model.ExperimentallyCapturedImage]:
    """Return all experimentally captured images in all experimental imaging datasets"""

    # Experimental Imaging Datasets in study
    datasets = get_experimental_imaging_dataset(submission, result_summary)
    model_dicts = []
    for dataset in datasets:
        # TODO: Revisit this - there may be cases where study components
        # have exactly the same title - and this will be a list greater
        # than length 1!
        file_references_dict = get_file_reference_by_dataset(
            submission,
            [
                dataset,
            ],
            result_summary,
            persist_artefacts,
        )
        file_references = []
        for file_reference_list in file_references_dict.values():
            file_references.extend(file_reference_list)

        if not file_references:
            message = f"Did not find file references for dataset {dataset.title} no ExperimentallyCapturedImages will be generated for this dataset"
            logger.warning(message)
            continue

        subject_uuid = dataset.attribute["subject_uuid"]
        acquisition_process_uuid = dataset.attribute["acquisition_process_uuid"]
        for file_reference in file_references:
            # Currently processing all single files bioformats can convert
            file_in_fl = file_reference.file_path
            extension = get_image_extension(file_in_fl)
            if not extension_in_bioformats_single_file_formats_list(extension):
                continue

            model_dict = prepare_experimentally_captured_image_dict(
                file_paths=file_in_fl,
                acquisition_process_uuid=acquisition_process_uuid,
                dataset_uuid=dataset.uuid,
                subject_uuid=subject_uuid,
                attribute=file_reference.attribute,
            )
            model_dicts.append(model_dict)
    experimentally_captured_images = dicts_to_api_models(
        model_dicts,
        bia_data_model.ExperimentallyCapturedImage,
        result_summary[submission.accno],
    )

    return experimentally_captured_images


def get_experimentally_captured_image(
    submission: Submission,
    dataset_uuid: UUID,
    file_references: List[bia_data_model.FileReference],
    result_summary: dict,
    persister: PersistenceStrategy,
) -> bia_data_model.ExperimentallyCapturedImage:
    """Get the ExperimentallyCapturedImage corresponding to the dataset/file_reference(s) combination"""

    dataset = persister.fetch_by_uuid(
        [
            str(dataset_uuid),
        ],
        bia_data_model.ExperimentalImagingDataset,
    )[0]
    ## Get the dataset
    # dataset = get_bia_data_model_by_uuid(
    #    dataset_uuid, bia_data_model.ExperimentalImagingDataset, submission.accno
    # )

    subject_uuid = dataset.attribute["subject_uuid"]
    acquisition_process_uuid = dataset.attribute["acquisition_process_uuid"]

    file_paths = ",".join([fr.file_path for fr in file_references])
    # Consolidate attributes from multiple file references into one dict
    attributes = merge_dicts([fr.attribute for fr in file_references])
    model_dict = prepare_experimentally_captured_image_dict(
        file_paths=file_paths,
        acquisition_process_uuid=acquisition_process_uuid,
        dataset_uuid=dataset.uuid,
        subject_uuid=subject_uuid,
        attribute=attributes,
    )

    experimentally_captured_image = (
        bia_data_model.ExperimentallyCapturedImage.model_validate(model_dict)
    )
    if experimentally_captured_image:
        persister.persist(
            [
                experimentally_captured_image,
            ],
        )
    return experimentally_captured_image


def prepare_experimentally_captured_image_dict(
    dataset_uuid: UUID,
    file_paths: str,
    acquisition_process_uuid: List[UUID],
    subject_uuid: UUID,
    attribute: dict = {},
    version: int = 0,
):
    model_dict = {
        "path": file_paths,
        "acquisition_process_uuid": acquisition_process_uuid,
        "submission_dataset_uuid": dataset_uuid,
        "subject_uuid": subject_uuid,
        "attribute": attribute,
        "version": version,
    }
    model_dict["uuid"] = generate_experimentally_captured_image_uuid(model_dict)
    return filter_model_dictionary(
        model_dict, bia_data_model.ExperimentallyCapturedImage
    )


def generate_experimentally_captured_image_uuid(
    experimentally_captured_image_dict: Dict[str, Any],
) -> str:
    attributes_to_consider = [
        "path",
        "acquisition_process_uuid",
        "submission_dataset_uuid",
        "subject_uuid",
    ]
    return dict_to_uuid(experimentally_captured_image_dict, attributes_to_consider)
