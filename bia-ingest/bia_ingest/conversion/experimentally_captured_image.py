import logging
from uuid import UUID
from typing import List, Dict, Any
from .utils import (
    dict_to_uuid,
    filter_model_dictionary,
    merge_dicts,
)
from ..biostudies import (
    Submission,
)

from bia_ingest.persistence_strategy import PersistenceStrategy

from bia_shared_datamodels import bia_data_model


logger = logging.getLogger("__main__." + __name__)


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
        "acquisition_process_uuid": [str(a) for a in acquisition_process_uuid],
        "submission_dataset_uuid": str(dataset_uuid),
        "subject_uuid": str(subject_uuid),
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
