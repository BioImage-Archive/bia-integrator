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
import bia_ingest.conversion.study as study_conversion
from bia_ingest.conversion.image_acquisition import get_image_acquisition
from bia_ingest.conversion.specimen import get_specimen_for_dataset

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

    The bia_data_model.Specimen and ImageAcquisitions associated with the
    dataset are also created here and their UUIDs stored in the
    associations attribute of the dataset. This allows
    ExperimentallyCapturedImages to access them.
    """
    study_components = find_sections_recursive(
        submission.section,
        [
            "Study Component",
        ],
        [],
    )
    analysis_method_dict = get_image_analysis_method(submission, result_summary)

    # Get all image acquisitions in study
    image_acquisitions = get_image_acquisition(
        submission, result_summary, persist_artefacts=persist_artefacts
    )

    experimental_imaging_datasets = []
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

        # TODO: We do not seem to have a function to get correlation methods!
        correlation_method_list = []

        if len(associations) > 0:
            # Image Analysis Method
            analysis_methods_from_associations = {
                a.get("image_analysis") for a in associations
            }
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
            "version": 0,
            "attribute": {"associations": associations},
        }
        model_dict["uuid"] = generate_experimental_imaging_dataset_uuid(model_dict)

        model_dict = filter_model_dictionary(
            model_dict, bia_data_model.ExperimentalImagingDataset
        )

        try:
            experimental_imaging_dataset = (
                bia_data_model.ExperimentalImagingDataset.model_validate(model_dict)
            )
        except ValidationError:
            log_failed_model_creation(
                bia_data_model.ExperimentalImagingDataset,
                result_summary[submission.accno],
            )

        # Create ImageAcquisition and Specimen and add uuids to dataset associations
        image_acquisition_title = [
            association["image_acquisition"]
            for association in experimental_imaging_dataset.attribute["associations"]
        ]
        acquisition_process_uuid = [
            str(ia.uuid)
            for ia in image_acquisitions
            if ia.title_id in image_acquisition_title
        ]
        experimental_imaging_dataset.attribute["acquisition_process_uuid"] = (
            acquisition_process_uuid
        )

        subject = get_specimen_for_dataset(
            submission, experimental_imaging_dataset, result_summary
        )
        experimental_imaging_dataset.attribute["subject_uuid"] = str(subject.uuid)
        experimental_imaging_dataset.attribute["biosample_uuid"] = str(
            subject.sample_of_uuid
        )

        experimental_imaging_datasets.append(experimental_imaging_dataset)

    log_model_creation_count(
        bia_data_model.ExperimentalImagingDataset,
        len(experimental_imaging_datasets),
        result_summary[submission.accno],
    )

    if persist_artefacts and experimental_imaging_datasets:
        persist(
            experimental_imaging_datasets,
            "experimental_imaging_datasets",
            submission.accno,
        )

    return experimental_imaging_datasets


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
