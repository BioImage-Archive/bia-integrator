import logging
from typing import List, Dict, Any
from .utils import (
    find_sections_recursive,
    get_generic_section_as_list,
    dict_to_uuid,
    get_generic_section_as_dict,
    persist,
    filter_model_dictionary,
    log_failed_model_creation,
    log_model_creation_count,
)
import bia_ingest_sm.conversion.study as study_conversion
from ..biostudies import (
    Submission,
    attributes_to_dict,
)
from pydantic import ValidationError
from bia_shared_datamodels import bia_data_model, semantic_models


logger = logging.getLogger("__main__." + __name__)


def get_experimental_imaging_dataset(
    submission: Submission, result_summary: dict, persist_artefacts=False
) -> List[bia_data_model.ExperimentalImagingDataset]:
    """
    Map biostudies.Submission study components to bia_data_model.ExperimentalImagingDataset
    """
    study_components = find_sections_recursive(
        submission.section,
        [
            "Study Component",
        ],
        [],
    )
    analysis_method_dict = get_image_analysis_method(submission, result_summary)

    experimental_imaging_dataset = []
    for section in study_components:
        attr_dict = attributes_to_dict(section.attributes)
        key_mapping = [
            (
                "image_analysis",
                "Image analysis",
                None,
            ),
            (
                "image_correlation",
                "Image correlation",
                None,
            ),
            (
                "biosample",
                "Biosample",
                None,
            ),
            (
                "image_acquisition",
                "Image acquisition",
                None,
            ),
            (
                "specimen",
                "Specimen",
                None,
            ),
        ]
        associations = get_generic_section_as_list(
            section,
            [
                "Associations",
            ],
            key_mapping,
        )

        analysis_method_list = []
        correlation_method_list = []

        # TODO: move this to main CLI code to make object generation more independent
        if len(associations) > 0:
            # Image Analysis Method
            analysis_methods_from_associations = [
                a.get("image_analysis") for a in associations
            ]
            for analysis_method in analysis_method_dict.values():
                if (
                    analysis_method.protocol_description
                    in analysis_methods_from_associations
                ):
                    analysis_method_list.append(analysis_method)

        section_name = attr_dict["Name"]
        model_dict = {
            "title_id": section_name,
            "description": attr_dict["Description"],
            "submitted_in_study_uuid": study_conversion.get_study_uuid(submission),
            "analysis_method": analysis_method_list,
            "correlation_method": correlation_method_list,
            "example_image_uri": [],
            "version": 1,
            "attribute": {"associations": associations},
        }
        model_dict["uuid"] = generate_experimental_imaging_dataset_uuid(model_dict)

        model_dict = filter_model_dictionary(
            model_dict, bia_data_model.ExperimentalImagingDataset
        )

        try:
            experimental_imaging_dataset.append(
                bia_data_model.ExperimentalImagingDataset.model_validate(model_dict)
            )
        except ValidationError:
            log_failed_model_creation(
                bia_data_model.ExperimentalImagingDataset,
                result_summary[submission.accno],
            )

    log_model_creation_count(
        bia_data_model.ExperimentalImagingDataset,
        len(experimental_imaging_dataset),
        result_summary[submission.accno],
    )

    if persist_artefacts and experimental_imaging_dataset:
        persist(
            experimental_imaging_dataset,
            "experimental_imaging_datasets",
            submission.accno,
        )

    return experimental_imaging_dataset


def get_image_analysis_method(
    submission: Submission, result_summary: dict
) -> Dict[str, semantic_models.ImageAnalysisMethod]:
    key_mapping = [
        (
            "protocol_description",
            "Title",
            None,
        ),
        (
            "features_analysed",
            "Image analysis overview",
            None,
        ),
    ]

    return get_generic_section_as_dict(
        submission,
        [
            "Image analysis",
        ],
        key_mapping,
        semantic_models.ImageAnalysisMethod,
        result_summary[submission.accno],
    )


def generate_experimental_imaging_dataset_uuid(
    experimental_imaging_dataset_dict: Dict[str, Any],
) -> str:
    # TODO: Add 'description' to computation of uuid (Maybe accno?)
    attributes_to_consider = [
        "title_id",
        "submitted_in_study_uuid",
    ]
    return dict_to_uuid(experimental_imaging_dataset_dict, attributes_to_consider)
