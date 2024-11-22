import logging
from typing import List, Any, Dict, Optional
from ..submission_parsing_utils import (
    attributes_to_dict,
    find_sections_recursive,
    case_insensitive_get,
)

from ...bia_object_creation_utils import (
    dict_to_uuid,
    filter_model_dictionary,
    dict_map_to_api_models,
    dicts_to_api_models,
)

from ...cli_logging import log_failed_model_creation, log_model_creation_count
from ..generic_conversion_utils import (
    get_associations_for_section,
    Association,
)
from bia_ingest.biostudies.v4.study import get_study_uuid
from bia_shared_datamodels.bia_data_model import DocumentMixin

from ..api import (
    Submission,
)
from pydantic import ValidationError
from bia_shared_datamodels import bia_data_model, semantic_models
from ...persistence_strategy import PersistenceStrategy


logger = logging.getLogger("__main__." + __name__)


def get_dataset(
    submission: Submission,
    bsst_title_to_bia_object_map: dict,
    result_summary: dict,
    persister: Optional[PersistenceStrategy] = None,
) -> List[bia_data_model.Dataset]:

    bsst_title_to_bia_object_map |= get_image_analysis_method(
        submission, result_summary
    )

    dataset = []
    dataset += get_dataset_dict_from_component(submission, bsst_title_to_bia_object_map)
    dataset += get_dataset_dict_from_annotation(
        submission, bsst_title_to_bia_object_map
    )

    image_annotation_datasets = dicts_to_api_models(
        dataset,
        bia_data_model.Dataset,
        result_summary[submission.accno],
    )

    log_model_creation_count(
        bia_data_model.Dataset,
        len(image_annotation_datasets),
        result_summary[submission.accno],
    )

    if persister and image_annotation_datasets:
        persister.persist(image_annotation_datasets)

    return image_annotation_datasets


def get_dataset_dict_from_component(
    submission: Submission,
    bsst_title_to_bia_object_map: dict,
) -> list[dict]:

    study_components = find_sections_recursive(submission.section, ["Study Component"])

    model_dicts = []
    for section in study_components:
        attr_dict = attributes_to_dict(section.attributes)
        associations = get_associations_for_section(section)

        analysis_method_list = get_image_analysis_method_from_associations(
            associations, bsst_title_to_bia_object_map
        )
        # TODO: write correlation method code
        correlation_method_list = []

        attribute_list = []
        if len(associations) > 0:
            attribute_list.append(
                semantic_models.Attribute.model_validate(
                    {
                        "provenance": semantic_models.AttributeProvenance("bia_ingest"),
                        "name": "associations",
                        "value": {
                            "associations": associations,
                        },
                    }
                )
            )
            attribute_list += get_uuid_attribute_from_associations(
                associations, bsst_title_to_bia_object_map
            )

        model_dict = {
            "title_id": attr_dict["Name"],
            "description": attr_dict["Description"],
            "submitted_in_study_uuid": get_study_uuid(submission),
            "analysis_method": analysis_method_list,
            "correlation_method": correlation_method_list,
            "example_image_uri": [],
            "version": 0,
            "attribute": attribute_list,
        }
        model_dict["uuid"] = generate_dataset_uuid(model_dict)

        model_dict = filter_model_dictionary(model_dict, bia_data_model.Dataset)

        model_dicts.append(model_dict)

    return model_dicts


def get_dataset_dict_from_annotation(
    submission: Submission,
    bsst_title_to_bia_object_map: dict,
) -> list[dict]:
    annotation_sections = find_sections_recursive(
        submission.section, ["Annotations"], []
    )

    model_dicts = []
    for section in annotation_sections:
        attr_dict = attributes_to_dict(section.attributes)

        attribute_list = []
        attribute_list += store_annotation_method_in_attribute(
            attr_dict, bsst_title_to_bia_object_map
        )

        # TODO: there is no "Description" field in the biostudies model.
        # We should probably decide how we want to map the overview between here and the AnotationMethod.
        model_dict = {
            "title_id": attr_dict["Title"],
            "description": attr_dict.get("Description", ""),
            "submitted_in_study_uuid": get_study_uuid(submission),
            "analysis_method": [],
            "correlation_method": [],
            "example_image_uri": [],
            "version": 0,
            "attribute": attribute_list,
        }
        model_dict["accession_id"] = submission.accno
        model_dict["uuid"] = generate_dataset_uuid(model_dict)
        model_dict = filter_model_dictionary(model_dict, bia_data_model.Dataset)
        model_dicts.append(model_dict)

    return model_dicts


def generate_dataset_uuid(
    dataset_dict: Dict[str, Any],
) -> str:
    # TODO: Add 'description' to computation of uuid (Maybe accno?)
    attributes_to_consider = [
        "title_id",
        "submitted_in_study_uuid",
    ]
    return dict_to_uuid(dataset_dict, attributes_to_consider)


def get_uuid_attribute_from_associations(
    associations: List[Association],
    bsst_title_to_bia_object_map: dict[str, DocumentMixin],
):
    attribute_dicts = []

    for association in associations:
        bio_sample_uuids = []
        specimen_prepartion_protocol_uuids = []
        image_acquisition_uuids = []

        if association.biosample:
            biosample_with_gp_key = association.biosample + "." + association.specimen
            if biosample_with_gp_key in bsst_title_to_bia_object_map:
                bio_sample_uuids.append(
                    bsst_title_to_bia_object_map[biosample_with_gp_key].uuid
                )
            elif association.biosample in bsst_title_to_bia_object_map:
                attribute_dicts.append(
                    bsst_title_to_bia_object_map[association.biosample].uuid
                )
            else:
                raise RuntimeError(
                    "Dataset cannot find BioSample that exists in its associations"
                )
        if bio_sample_uuids:
            attribute_dicts.append(
                {
                    "provenance": semantic_models.AttributeProvenance("bia_ingest"),
                    "name": "bio_sample_uuid",
                    "value": {"bio_sample_uuid": bio_sample_uuids},
                }
            )

        if association.image_acquisition:
            if association.image_acquisition in bsst_title_to_bia_object_map:
                image_acquisition_uuids.append(
                    bsst_title_to_bia_object_map[association.image_acquisition].uuid
                )
            else:
                raise RuntimeError(
                    "Dataset cannot find Image Acquisition that exists in its associations"
                )
        if image_acquisition_uuids:
            attribute_dicts.append(
                {
                    "provenance": semantic_models.AttributeProvenance("bia_ingest"),
                    "name": "image_acquisition_protocol_uuid",
                    "value": {
                        "image_acquisition_protocol_uuid": image_acquisition_uuids
                    },
                }
            )

        if association.specimen:
            if association.specimen in bsst_title_to_bia_object_map:
                specimen_prepartion_protocol_uuids.append(
                    bsst_title_to_bia_object_map[association.image_acquisition].uuid
                )
            else:
                raise RuntimeError(
                    "Dataset cannot find Specimen Imaging Prepration Protocol that exists in its associations"
                )
        if specimen_prepartion_protocol_uuids:
            attribute_dicts.append(
                {
                    "provenance": semantic_models.AttributeProvenance("bia_ingest"),
                    "name": "specimen_imaging_prepartion_protocol_uuid",
                    "value": {
                        "specimen_imaging_prepartion_protocol_uuid": specimen_prepartion_protocol_uuids
                    },
                }
            )
    return [semantic_models.Attribute.model_validate(x) for x in attribute_dicts]


def get_image_analysis_method(
    submission: Submission, result_summary: dict
) -> Dict[str, semantic_models.ImageAnalysisMethod]:

    image_analysis_sections = find_sections_recursive(
        submission.section, ["Image analysis"], []
    )

    key_mapping = [
        ("protocol_description", "Title", None),
        ("features_analysed", "Image analysis overview", None),
    ]

    model_dicts_map = {}
    for section in image_analysis_sections:
        attr_dict = attributes_to_dict(section.attributes)

        model_dict = {
            k: case_insensitive_get(attr_dict, v, default)
            for k, v, default in key_mapping
        }

        model_dicts_map[attr_dict["Title"]] = model_dict

    return dict_map_to_api_models(
        model_dicts_map,
        semantic_models.ImageAnalysisMethod,
        result_summary[submission.accno],
    )


def get_image_analysis_method_from_associations(
    associations: List[Association], bsst_title_to_bia_object_map
):
    image_analysis = []
    for association in associations:
        if association.image_analysis:
            image_analysis.append(
                bsst_title_to_bia_object_map[association.image_analysis]
            )
    return image_analysis


def store_annotation_method_in_attribute(
    attr_dict: dict, bsst_title_to_bia_object_map: dict[str, DocumentMixin]
):
    attribute_dicts = []
    if attr_dict["Title"] in bsst_title_to_bia_object_map:
        attribute_dicts.append(
            {
                "provenance": semantic_models.AttributeProvenance("bia_ingest"),
                "name": "annotation_method_uuid",
                "value": {
                    "annotation_method_uuid": bsst_title_to_bia_object_map[
                        attr_dict["Title"]
                    ].uuid
                },
            }
        )
    else:
        raise RuntimeError(
            "Dataset cannot find Annotation Method that should have been created"
        )
    return attribute_dicts
