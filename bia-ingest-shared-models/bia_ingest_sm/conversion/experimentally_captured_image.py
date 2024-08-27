import logging
from typing import List
from .utils import dicts_to_api_models, dict_to_uuid
from .experimental_imaging_dataset import get_experimental_imaging_dataset
from bia_ingest_sm.conversion.specimen import get_specimen_for_association
from bia_ingest_sm.conversion.image_acquisition import get_image_acquisition
from ..biostudies import (
    Submission,
)
from bia_shared_datamodels import bia_data_model


logger = logging.getLogger("__main__." + __name__)


def get_all_experimentally_captured_images(
    submission: Submission, result_summary: dict, persist_artefacts=False
) -> List[bia_data_model.ExperimentallyCapturedImage]:
    """Return all experimentally captured images in all experimental imaging datasets"""

    datasets = get_experimental_imaging_dataset(submission, result_summary)
    model_dicts = []
    for dataset in datasets:
        image_acquisition_title = [
            association["image_acquisition"]
            for association in dataset.attribute["associations"]
        ]
        # TODO: Check if ImageAcquisitionMethod already exists. If not create
        # TODO: Move this out of for loop. I.e. get all image acquisitions for study only once!
        # without persisting?
        # image_acquisitions = get_image_acquisition_by_title(submission.accno, image_acquisition_title)
        image_acquisitions = None

        if not image_acquisitions:
            # Get all image acquisitions in study
            image_acquisitions = get_image_acquisition(
                submission, result_summary, persist_artefacts=persist_artefacts
            )

        acquisition_process_uuid = [
            ia.uuid
            for ia in image_acquisitions
            if ia.title_id in image_acquisition_title
        ]
        subject_uuid = get_specimen_for_association(
            submission, dataset.attribute["associations"][0]
        ).uuid

        model_dict = {
            "acquisition_process_uuid": acquisition_process_uuid,
            "submission_dataset_uuid": dataset.uuid,
            "subject_uuid": subject_uuid,
        }
        model_dict["uuid"] = dict_to_uuid(model_dict, list(model_dict.keys()))
        model_dict["attribute"] = {}
        model_dict["version"] = 1
        model_dicts.append(model_dict)
    experimentally_captured_images = dicts_to_api_models(
        model_dicts,
        bia_data_model.ExperimentallyCapturedImage,
        result_summary[submission.accno],
    )

    return experimentally_captured_images


#    submission: Submission, result_summary: dict, persist_artefacts=False
# ) -> List[bia_data_model.ExperimentalImagingDataset]:
#    """
#    Map biostudies.Submission study components to bia_data_model.ExperimentalImagingDataset
#    """
#    study_components = find_sections_recursive(
#        submission.section,
#        [
#            "Study Component",
#        ],
#        [],
#    )
#    analysis_method_dict = get_image_analysis_method(submission, result_summary)
#
#    experimental_imaging_dataset = []
#    for section in study_components:
#        attr_dict = attributes_to_dict(section.attributes)
#        key_mapping = [
#            (
#                "image_analysis",
#                "Image analysis",
#                None,
#            ),
#            (
#                "image_correlation",
#                "Image correlation",
#                None,
#            ),
#            (
#                "biosample",
#                "Biosample",
#                None,
#            ),
#            (
#                "image_acquisition",
#                "Image acquisition",
#                None,
#            ),
#            (
#                "specimen",
#                "Specimen",
#                None,
#            ),
#        ]
#        associations = get_generic_section_as_list(
#            section,
#            [
#                "Associations",
#            ],
#            key_mapping,
#        )
#
#        analysis_method_list = []
#        correlation_method_list = []
#
#        # TODO: move this to main CLI code to make object generation more independent
#        if len(associations) > 0:
#            # Image Analysis Method
#            analysis_methods_from_associations = [
#                a.get("image_analysis") for a in associations
#            ]
#            for analysis_method in analysis_method_dict.values():
#                if (
#                    analysis_method.protocol_description
#                    in analysis_methods_from_associations
#                ):
#                    analysis_method_list.append(analysis_method)
#
#        section_name = attr_dict["Name"]
#        model_dict = {
#            "title_id": section_name,
#            "description": attr_dict["Description"],
#            "submitted_in_study_uuid": study_conversion.get_study_uuid(submission),
#            "analysis_method": analysis_method_list,
#            "correlation_method": correlation_method_list,
#            "example_image_uri": [],
#            "version": 1,
#            "attribute": {"associations": associations},
#        }
#        model_dict["uuid"] = generate_experimental_imaging_dataset_uuid(model_dict)
#
#        model_dict = filter_model_dictionary(
#            model_dict, bia_data_model.ExperimentalImagingDataset
#        )
#
#
#        try:
#            experimental_imaging_dataset.append(
#            bia_data_model.ExperimentalImagingDataset.model_validate(model_dict)
#        )
#        except(ValidationError):
#            log_failed_model_creation(bia_data_model.ExperimentalImagingDataset, result_summary)
#
#
#    logger.info(
#        f"Ingesting: {submission.accno}. Created bia_data_model.ExperimentalImagingDataset. Count: {len(experimental_imaging_dataset)}"
#    )
#
#    if persist_artefacts and experimental_imaging_dataset:
#        persist(
#            experimental_imaging_dataset,
#            "experimental_imaging_datasets",
#            submission.accno,
#        )
#
#    return experimental_imaging_dataset
#
#
# def get_image_analysis_method(
#    submission: Submission,
#    result_summary: dict
# ) -> Dict[str, semantic_models.ImageAnalysisMethod]:
#    key_mapping = [
#        (
#            "protocol_description",
#            "Title",
#            None,
#        ),
#        (
#            "features_analysed",
#            "Image analysis overview",
#            None,
#        ),
#    ]
#
#    return get_generic_section_as_dict(
#        submission,
#        [
#            "Image analysis",
#        ],
#        key_mapping,
#        semantic_models.ImageAnalysisMethod,
#        result_summary[submission.accno],
#    )
#
#
# def generate_experimental_imaging_dataset_uuid(
#    experimental_imaging_dataset_dict: Dict[str, Any],
# ) -> str:
#    # TODO: Add 'description' to computation of uuid (Maybe accno?)
#    attributes_to_consider = [
#        "title_id",
#        "submitted_in_study_uuid",
#    ]
#    return dict_to_uuid(experimental_imaging_dataset_dict, attributes_to_consider)
