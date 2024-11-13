import logging
from typing import List, Any, Dict, Optional

from .biostudies.submission_parsing_utils import (
    attributes_to_dict,
    find_sections_recursive,
)

from ..bia_object_creation_utils import dict_to_uuid, filter_model_dictionary

from ..cli_logging import log_failed_model_creation, log_model_creation_count
from .generic_conversion_utils import (
    get_associations_for_section,
    get_generic_section_as_dict,
)
import bia_ingest.ingest.study as study_conversion
from bia_ingest.ingest.image_acquisition_protocol import get_image_acquisition_protocol
from bia_ingest.ingest.specimen import get_specimen_for_dataset

from .biostudies.api import (
    Submission,
)
from pydantic import ValidationError
from bia_shared_datamodels import bia_data_model, semantic_models
from ..persistence_strategy import PersistenceStrategy


logger = logging.getLogger("__main__." + __name__)


def get_dataset(
    submission: Submission,
    result_summary: dict,
    persister: Optional[PersistenceStrategy] = None,
) -> List[bia_data_model.Dataset]:
    """
    Map biostudies.Submission study components to bia_data_model.Image

    The bia_data_model.Specimen and ImageAcquisitions associated with the
    dataset are also created here and their UUIDs stored in the
    associations attribute of the dataset. This allows
    bia_data_model.Image objects to access them.
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
    image_acquisition_protocols = get_image_acquisition_protocol(
        submission, result_summary, persister=persister
    )

    datasets = []
    for section in study_components:
        attr_dict = attributes_to_dict(section.attributes)
        associations = get_associations_for_section(section)

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

        associations_as_attribute = {
            "provenance": semantic_models.AttributeProvenance("bia_ingest"),
            "name": "associations",
            "value": {
                "associations": associations,
            },
        }

        section_name = attr_dict["Name"]
        model_dict = {
            "title_id": section_name,
            "description": attr_dict["Description"],
            "submitted_in_study_uuid": study_conversion.get_study_uuid(submission),
            "analysis_method": analysis_method_list,
            "correlation_method": correlation_method_list,
            "example_image_uri": [],
            "version": 0,
            "attribute": [
                associations_as_attribute,
            ],
        }
        model_dict["uuid"] = generate_dataset_uuid(model_dict)

        model_dict = filter_model_dictionary(model_dict, bia_data_model.Dataset)

        try:
            dataset = bia_data_model.Dataset.model_validate(model_dict)
        except ValidationError as validation_error:
            logger.error(f"Error creating dataset. Error was: {validation_error}")
            log_failed_model_creation(
                bia_data_model.Dataset,
                result_summary[submission.accno],
            )

        # Create ImageAcquisition and Specimen and add uuids to dataset associations
        image_acquisition_title = [
            association["image_acquisition"] for association in associations
        ]
        acquisition_process_uuid = [
            str(iap.uuid)
            for iap in image_acquisition_protocols
            if iap.title_id in image_acquisition_title
        ]
        acquisition_process_uuid_attr_dict = {
            "provenance": semantic_models.AttributeProvenance("bia_ingest"),
            "name": "acquisition_process_uuid",
            "value": {"acquisition_process_uuid": acquisition_process_uuid},
        }
        acquisition_process_uuid_as_attr = semantic_models.Attribute.model_validate(
            acquisition_process_uuid_attr_dict
        )
        dataset.attribute.append(acquisition_process_uuid_as_attr)

        subject = get_specimen_for_dataset(submission, dataset, result_summary)
        if subject:
            subject_uuid_attr_dict = {
                "provenance": semantic_models.AttributeProvenance("bia_ingest"),
                "name": "subject_uuid",
                "value": {
                    "subject_uuid": str(subject.uuid),
                },
            }
            dataset.attribute.append(
                semantic_models.Attribute.model_validate(subject_uuid_attr_dict)
            )
            sample_of_uuid_attr_dict = {
                "provenance": semantic_models.AttributeProvenance("bia_ingest"),
                "name": "biosample_uuid",
                "value": {
                    "biosample_uuid": str(subject.sample_of_uuid),
                },
            }
            dataset.attribute.append(
                semantic_models.Attribute.model_validate(sample_of_uuid_attr_dict)
            )

        datasets.append(dataset)

    log_model_creation_count(
        bia_data_model.Dataset,
        len(datasets),
        result_summary[submission.accno],
    )

    if persister and datasets:
        persister.persist(
            datasets,
        )

    return datasets


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


def generate_dataset_uuid(
    dataset_dict: Dict[str, Any],
) -> str:
    # TODO: Add 'description' to computation of uuid (Maybe accno?)
    attributes_to_consider = [
        "title_id",
        "submitted_in_study_uuid",
    ]
    return dict_to_uuid(dataset_dict, attributes_to_consider)
