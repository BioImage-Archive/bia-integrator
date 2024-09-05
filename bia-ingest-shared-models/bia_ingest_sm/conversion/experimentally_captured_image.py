import logging
from uuid import UUID
from typing import List, Dict, Any
from .utils import (
    dicts_to_api_models,
    dict_to_uuid,
    find_datasets_with_file_lists,
    get_bia_data_model_by_uuid,
    filter_model_dictionary,
)
from ..image_utils.image_utils import (
    get_image_extension,
    extension_in_bioformats_single_file_formats_list,
)
from bia_ingest_sm.conversion.specimen import get_specimen_for_association
from bia_ingest_sm.conversion.image_acquisition import get_image_acquisition
from bia_ingest_sm.conversion.experimental_imaging_dataset import (
    get_experimental_imaging_dataset,
)
from ..biostudies import (
    Submission,
    flist_from_flist_fname,
)
from bia_shared_datamodels import bia_data_model


logger = logging.getLogger("__main__." + __name__)


def get_all_experimentally_captured_images(
    submission: Submission, result_summary: dict, persist_artefacts=False
) -> List[bia_data_model.ExperimentallyCapturedImage]:
    """Return all experimentally captured images in all experimental imaging datasets"""

    # TODO: Use of API will affect this! Retrieve if exists (Create otherwise?)
    # TODO: Write function to get all objects of Type in accession_id subdir
    image_acquisitions = None

    # TODO: this is not really ingest - do we need result_summary?
    if not image_acquisitions:
        # Get all image acquisitions in study
        image_acquisitions = get_image_acquisition(
            submission, result_summary, persist_artefacts=persist_artefacts
        )

    # Experimental Imaging Datasets in study
    datasets = get_experimental_imaging_dataset(submission, result_summary)
    datasets_with_file_lists = find_datasets_with_file_lists(submission)
    model_dicts = []
    for dataset in datasets:
        # TODO: Revisit this - there may be cases where study components
        # have exactly the same title - and this will be a list greater
        # than length 1!
        dataset_from_submission = datasets_with_file_lists.get(dataset.title_id)[0]
        file_list_fname = (
            dataset_from_submission.get("File List")
            if dataset_from_submission
            else None
        )

        if not file_list_fname:
            message = f"Did not find file list for dataset {dataset.title} no ExperimentallyCapturedImages will be generated for this dataset"
            logger.warning(message)
            continue

        files_in_fl = flist_from_flist_fname(submission.accno, file_list_fname)
        image_acquisition_title = [
            association["image_acquisition"]
            for association in dataset.attribute["associations"]
        ]
        # It would be nice to have a function like below ...
        # image_acquisitions = get_image_acquisition_by_title(submission.accno, image_acquisition_title)
        acquisition_process_uuid = [
            ia.uuid
            for ia in image_acquisitions
            if ia.title_id in image_acquisition_title
        ]

        # TODO: revisit this once API up
        subject_uuid = get_specimen_for_association(
            submission, dataset.attribute["associations"][0], result_summary
        ).uuid

        for file_in_fl in files_in_fl:
            # Currently processing all single files bioformats can convert
            extension = get_image_extension(str(file_in_fl.path))
            if not extension_in_bioformats_single_file_formats_list(extension):
                continue

            model_dict = prepare_experimentally_captured_image_dict(
                file_paths=str(file_in_fl.path),
                acquisition_process_uuid=acquisition_process_uuid,
                dataset_uuid=dataset.uuid,
                subject_uuid=subject_uuid,
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
    file_paths: List[str],
    result_summary: dict,
    persist_artefacts=False,
) -> bia_data_model.ExperimentallyCapturedImage:
    """Get the ExperimentallyCapturedImage corresponding to the dataset/file_reference(s) combination"""

    # Get the dataset
    dataset = get_bia_data_model_by_uuid(
        dataset_uuid, bia_data_model.ExperimentalImagingDataset, submission.accno
    )

    image_acquisition_title = [
        association["image_acquisition"]
        for association in dataset.attribute["associations"]
    ]
    # TODO: Use of API will affect this! Retrieve if exists (Create otherwise?)
    # TODO: Write function to get all objects of Type in accession_id subdir
    image_acquisitions = None

    if not image_acquisitions:
        # Get all image acquisitions in study
        image_acquisitions = get_image_acquisition(
            submission, result_summary, persist_artefacts=persist_artefacts
        )

    acquisition_process_uuid = [
        ia.uuid for ia in image_acquisitions if ia.title_id in image_acquisition_title
    ]
    subject_uuid = get_specimen_for_association(
        submission, dataset.attribute["associations"][0], result_summary
    ).uuid

    model_dict = prepare_experimentally_captured_image_dict(
        file_paths=",".join([fp for fp in file_paths]),
        acquisition_process_uuid=acquisition_process_uuid,
        dataset_uuid=dataset.uuid,
        subject_uuid=subject_uuid,
    )
    return bia_data_model.ExperimentallyCapturedImage.model_validate(model_dict)


def prepare_experimentally_captured_image_dict(
    dataset_uuid: UUID,
    file_paths: str,
    acquisition_process_uuid: List[UUID],
    subject_uuid: UUID,
    attribute: dict = {},
    version: int = 1,
):
    model_dict = {
        # TODO: Are file_reference uuids a better choice here?
        # "file_reference_uuid": ",".join([str(f) for f in file_reference_uuids]),
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
        # TODO: Are file_reference uuids a better choice here?
        # "file_reference_uuid": ",".join([str(f) for f in file_reference_uuids]),
        "path",
        "acquisition_process_uuid",
        "submission_dataset_uuid",
        "subject_uuid",
    ]
    return dict_to_uuid(experimentally_captured_image_dict, attributes_to_consider)
