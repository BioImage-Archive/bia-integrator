from typing import List
from bia_shared_datamodels import bia_data_model, semantic_models
from bia_ingest.bia_object_creation_utils import dict_to_uuid
from .utils import accession_id
from .mock_image_analysis_method import get_image_analysis_method
from .mock_image_correlation_method import get_test_image_correlation_method
from .mock_image_acquisition_protocol import get_image_acquisition_protocol_as_map
from .mock_association import get_association_dicts
from .mock_biosample import get_bio_sample_as_map
from .mock_specimen_imaging_preparation_protocol import (
    get_specimen_imaging_preparation_protocol_as_map,
)
from .mock_annotation_method import get_annotation_method_as_map


def get_dataset() -> List[bia_data_model.Dataset]:
    study_uuid = dict_to_uuid(
        {
            "accession_id": accession_id,
        },
        attributes_to_consider=[
            "accession_id",
        ],
    )
    associations = list(get_association_dicts().values())

    image_acquisition_protocol_uuids = [
        str(iap.uuid) for iap in get_image_acquisition_protocol_as_map().values()
    ]
    bio_sample_uuids = [str(bs.uuid) for bs in get_bio_sample_as_map().values()]
    specimen_imaging_preparation_protocol_uuids = [
        str(sipp.uuid)
        for sipp in get_specimen_imaging_preparation_protocol_as_map().values()
    ]

    dataset_dict = {
        "title_id": "Study Component 1",
        "submitted_in_study_uuid": study_uuid,
        "analysis_method": [
            get_image_analysis_method().model_dump(),
        ],
        "correlation_method": [
            # get_template_image_correlation_method().model_dump(),
        ],
        "example_image_uri": [],
        "description": "Description of study component 1",
        "version": 0,
        "attribute": [
            {
                "provenance": semantic_models.AttributeProvenance("bia_ingest"),
                "name": "associations",
                "value": {
                    "associations": associations[0],
                },
            },
            {
                "provenance": semantic_models.AttributeProvenance("bia_ingest"),
                "name": "image_acquisition_protocol_uuid",
                "value": {
                    "image_acquisition_protocol_uuid": image_acquisition_protocol_uuids,
                },
            },
            {
                "provenance": semantic_models.AttributeProvenance("bia_ingest"),
                "name": "specimen_imaging_preparation_protocol_uuid",
                "value": {
                    "specimen_imaging_preparation_protocol_uuid": [
                        specimen_imaging_preparation_protocol_uuids[0]
                    ]
                },
            },
            {
                "provenance": semantic_models.AttributeProvenance("bia_ingest"),
                "name": "bio_sample_uuid",
                "value": {
                    "bio_sample_uuid": bio_sample_uuids[0:2],
                },
            },
        ],
    }

    dataset_uuid = dict_to_uuid(
        dataset_dict,
        [
            "title_id",
            "submitted_in_study_uuid",
        ],
    )
    dataset_dict["uuid"] = dataset_uuid
    dataset1 = bia_data_model.Dataset.model_validate(dataset_dict)

    dataset_dict = {
        "title_id": "Study Component 2",
        "submitted_in_study_uuid": study_uuid,
        "analysis_method": [
            get_image_analysis_method().model_dump(),
        ],
        "correlation_method": [
            # get_template_image_correlation_method().model_dump(),
        ],
        "example_image_uri": [],
        "description": "Description of study component 2",
        "version": 0,
        "attribute": [
            {
                "provenance": semantic_models.AttributeProvenance("bia_ingest"),
                "name": "associations",
                "value": {
                    "associations": associations[1],
                },
            },
            {
                "provenance": semantic_models.AttributeProvenance("bia_ingest"),
                "name": "image_acquisition_protocol_uuid",
                "value": {
                    "image_acquisition_protocol_uuid": [
                        image_acquisition_protocol_uuids[0]
                    ],
                },
            },
            {
                "provenance": semantic_models.AttributeProvenance("bia_ingest"),
                "name": "specimen_imaging_preparation_protocol_uuid",
                "value": {
                    "specimen_imaging_preparation_protocol_uuid": [
                        specimen_imaging_preparation_protocol_uuids[1]
                    ]
                },
            },
            {
                "provenance": semantic_models.AttributeProvenance("bia_ingest"),
                "name": "bio_sample_uuid",
                "value": {
                    "bio_sample_uuid": [bio_sample_uuids[2]],
                },
            },
        ],
    }
    dataset_uuid = dict_to_uuid(
        dataset_dict,
        [
            "title_id",
            "submitted_in_study_uuid",
        ],
    )
    dataset_dict["uuid"] = dataset_uuid
    dataset2 = bia_data_model.Dataset.model_validate(dataset_dict)

    annotation_method_uuids = [
        str(am.uuid) for am in get_annotation_method_as_map().values()
    ]

    dataset_dict = {
        "title_id": "Segmentation masks",
        "submitted_in_study_uuid": study_uuid,
        "analysis_method": [],
        "correlation_method": [],
        "example_image_uri": [],
        "description": None,
        "version": 0,
        "attribute": [
            {
                "provenance": semantic_models.AttributeProvenance("bia_ingest"),
                "name": "annotation_method_uuid",
                "value": {
                    "annotation_method_uuid": annotation_method_uuids,
                },
            },
        ],
    }
    dataset_uuid = dict_to_uuid(
        dataset_dict,
        [
            "title_id",
            "submitted_in_study_uuid",
        ],
    )
    dataset_dict["uuid"] = dataset_uuid
    dataset_annotation = bia_data_model.Dataset.model_validate(dataset_dict)
    return [dataset1, dataset2, dataset_annotation]
