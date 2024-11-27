import logging
from typing import List, Any, Dict, Optional
from pydantic import BaseModel
from bia_ingest.biostudies.submission_parsing_utils import (
    attributes_to_dict,
    find_sections_recursive,
)

from bia_ingest.bia_object_creation_utils import (
    dict_to_uuid,
    filter_model_dictionary,
    dicts_to_api_models,
)

from bia_ingest.cli_logging import log_model_creation_count
from bia_ingest.biostudies.generic_conversion_utils import (
    get_associations_for_section,
    Association,
)
from bia_ingest.biostudies.v4.study import get_study_uuid

from bia_ingest.biostudies.api import (
    Submission,
)
from bia_shared_datamodels import bia_data_model, semantic_models
from bia_ingest.persistence_strategy import PersistenceStrategy
from uuid import UUID

logger = logging.getLogger("__main__." + __name__)


def get_dataset(
    submission: Submission,
    bsst_title_to_bia_object_map: dict,
    result_summary: dict,
    persister: Optional[PersistenceStrategy] = None,
) -> List[bia_data_model.Dataset]:

    dataset = []
    dataset += get_dataset_dict_from_study_component(
        submission, bsst_title_to_bia_object_map
    )
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


def get_dataset_dict_from_study_component(
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

        correlation_method_list = get_image_correlation_method_from_associations(
            associations, bsst_title_to_bia_object_map
        )

        attribute_list = []
        if len(associations) > 0:
            attribute_list.append(
                semantic_models.Attribute.model_validate(
                    {
                        "provenance": semantic_models.AttributeProvenance("bia_ingest"),
                        "name": "associations",
                        "value": {
                            "associations": [
                                association.model_dump() for association in associations
                            ],
                        },
                    }
                )
            )
            attribute_list += get_uuid_attribute_from_associations(
                associations, bsst_title_to_bia_object_map
            )

        # TODO: Actually use correlation methods?
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
            "description": attr_dict.get("Description", None),
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
    object_map: dict[str, dict[str, bia_data_model.DocumentMixin]],
):

    bio_sample_uuids = []
    specimen_prepartion_protocol_uuids = []
    image_acquisition_uuids = []
    for association in associations:

        if association.biosample:
            biosample_with_gp_key = association.biosample + "." + association.specimen
            if biosample_with_gp_key in object_map["bio_sample"]:
                bio_sample_uuids.append(
                    object_map["bio_sample"][biosample_with_gp_key].uuid
                )
            elif association.biosample in object_map["bio_sample"]:
                bio_sample_uuids.append(
                    object_map["bio_sample"][association.biosample].uuid
                )
            else:
                raise RuntimeError(
                    f"Dataset cannot find BioSample that exists in its associations: {association.biosample}"
                )

        if association.image_acquisition:
            if (
                association.image_acquisition
                in object_map["image_acquisition_protocol"]
            ):
                image_acquisition_uuids.append(
                    object_map["image_acquisition_protocol"][
                        association.image_acquisition
                    ].uuid
                )
            else:
                raise RuntimeError(
                    f"Dataset cannot find Image Acquisition that exists in its associations: {association.image_acquisition}"
                )

        if association.specimen:
            if (
                association.specimen
                in object_map["specimen_imaging_preparation_protocol"]
            ):
                specimen_prepartion_protocol_uuids.append(
                    object_map["specimen_imaging_preparation_protocol"][
                        association.specimen
                    ].uuid
                )
            else:
                raise RuntimeError(
                    f"Dataset cannot find Specimen Imaging Prepration Protocol that exists in its associations: {association.specimen}"
                )

    attribute_dicts = []
    if image_acquisition_uuids:
        attribute_dicts.append(
            {
                "provenance": semantic_models.AttributeProvenance("bia_ingest"),
                "name": "image_acquisition_protocol_uuid",
                "value": {
                    "image_acquisition_protocol_uuid": unique_string_list_uuid(
                        image_acquisition_uuids
                    )
                },
            }
        )
    if specimen_prepartion_protocol_uuids:
        attribute_dicts.append(
            {
                "provenance": semantic_models.AttributeProvenance("bia_ingest"),
                "name": "specimen_imaging_preparation_protocol_uuid",
                "value": {
                    "specimen_imaging_preparation_protocol_uuid": unique_string_list_uuid(
                        specimen_prepartion_protocol_uuids
                    )
                },
            }
        )
    if bio_sample_uuids:
        attribute_dicts.append(
            {
                "provenance": semantic_models.AttributeProvenance("bia_ingest"),
                "name": "bio_sample_uuid",
                "value": {"bio_sample_uuid": unique_string_list_uuid(bio_sample_uuids)},
            }
        )

    return [semantic_models.Attribute.model_validate(x) for x in attribute_dicts]


def store_annotation_method_in_attribute(
    attr_dict: dict,
    object_map: dict[str, dict[str, bia_data_model.DocumentMixin]],
):
    attribute_dicts = []
    if attr_dict["Title"] in object_map["annotation_method"]:
        attribute_dicts.append(
            {
                "provenance": semantic_models.AttributeProvenance("bia_ingest"),
                "name": "annotation_method_uuid",
                "value": {
                    "annotation_method_uuid": [
                        str(object_map["annotation_method"][attr_dict["Title"]].uuid)
                    ]
                },
            }
        )
    else:
        raise RuntimeError(
            "Dataset cannot find Annotation Method that should have been created"
        )
    return attribute_dicts


def get_image_analysis_method_from_associations(
    associations: List[Association], object_map: dict[str, dict]
):

    image_analysis = []
    for ia_key, ia_value in object_map["image_analysis_method"].items():
        add_ia = False
        for association in associations:
            if association.image_analysis and association.image_analysis == ia_key:
                add_ia = True
        if add_ia:
            image_analysis.append(ia_value)

    return image_analysis


def get_image_correlation_method_from_associations(
    associations: List[Association], object_map: dict[str, dict]
):
    image_correlations = []
    for ia_key, ia_value in object_map["image_analysis_method"].items():
        add_ic = False
        for association in associations:
            if (
                association.image_correlation
                and association.image_correlation == ia_key
            ):
                add_ia = True
        if add_ic:
            image_correlations.append(ia_value)

    return image_correlations


def unique_string_list_uuid(uuid_list: list[UUID]):
    out_list = []
    for uuid in uuid_list:
        if str(uuid) not in out_list:
            out_list.append(str(uuid))
    return out_list
