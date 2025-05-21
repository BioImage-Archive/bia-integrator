from typing import List
from bia_shared_datamodels import bia_data_model, semantic_models
from bia_shared_datamodels.uuid_creation import create_dataset_uuid
from .mock_object_constants import study_uuid, study_uuid_biostudies_default
from .mock_image_analysis_method import get_image_analysis_method
from .mock_image_correlation_method import get_image_correlation_method
from .mock_image_acquisition_protocol import get_image_acquisition_protocol_as_map
from .mock_association import get_association_dicts
from .mock_biosample import get_bio_sample_as_map
from .mock_specimen_imaging_preparation_protocol import (
    get_specimen_imaging_preparation_protocol_as_map,
)
from .mock_annotation_method import get_annotation_method_as_map


def get_dataset() -> List[bia_data_model.Dataset]:
    associations = list(get_association_dicts().values())

    image_acquisition_protocol_uuids = [
        str(iap.uuid) for iap in get_image_acquisition_protocol_as_map().values()
    ]
    bio_sample_uuids = [str(bs.uuid) for bs in get_bio_sample_as_map().values()]
    specimen_imaging_preparation_protocol_uuids = [
        str(sipp.uuid)
        for sipp in get_specimen_imaging_preparation_protocol_as_map().values()
    ]
    annotation_method_uuids = [
        str(am.uuid) for am in get_annotation_method_as_map().values()
    ]

    title_id_1 = "Study Component 1"
    unique_string_1 = "Study Component-1"
    title_id_2 = "Study Component 2"
    unique_string_2 = "Study Component-2"
    title_id_3 = "Segmentation masks"
    unique_string_3 = "Annotations-29"

    object_dicts = [
        {
            "uuid": create_dataset_uuid(study_uuid, unique_string_1),
            "object_creator": "bia_ingest",
            "title": title_id_1,
            "submitted_in_study_uuid": study_uuid,
            "analysis_method": [
                get_image_analysis_method().model_dump(),
            ],
            "correlation_method": [
                get_image_correlation_method().model_dump(),
            ],
            "example_image_uri": [],
            "description": "Description of study component 1",
            "version": 0,
            "additional_metadata": [
                {
                    "provenance": semantic_models.Provenance("bia_ingest"),
                    "name": "associations",
                    "value": {
                        "associations": associations[0],
                    },
                },
                {
                    "provenance": semantic_models.Provenance("bia_ingest"),
                    "name": "image_acquisition_protocol_uuid",
                    "value": {
                        "image_acquisition_protocol_uuid": image_acquisition_protocol_uuids,
                    },
                },
                {
                    "provenance": semantic_models.Provenance("bia_ingest"),
                    "name": "specimen_imaging_preparation_protocol_uuid",
                    "value": {
                        "specimen_imaging_preparation_protocol_uuid": [
                            specimen_imaging_preparation_protocol_uuids[0]
                        ]
                    },
                },
                {
                    "provenance": semantic_models.Provenance("bia_ingest"),
                    "name": "bio_sample_uuid",
                    "value": {
                        "bio_sample_uuid": bio_sample_uuids[0:2],
                    },
                },
                {
                    "provenance": semantic_models.Provenance("bia_ingest"),
                    "name": "uuid_unique_input",
                    "value": {
                      "uuid_unique_input": unique_string_1,
                    }
                },
            ],
        },
        {
            "uuid": create_dataset_uuid(study_uuid, unique_string_2),
            "object_creator": "bia_ingest",
            "title": title_id_2,
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
            "additional_metadata": [
                {
                    "provenance": semantic_models.Provenance("bia_ingest"),
                    "name": "associations",
                    "value": {
                        "associations": associations[1],
                    },
                },
                {
                    "provenance": semantic_models.Provenance("bia_ingest"),
                    "name": "image_acquisition_protocol_uuid",
                    "value": {
                        "image_acquisition_protocol_uuid": [
                            image_acquisition_protocol_uuids[0]
                        ],
                    },
                },
                {
                    "provenance": semantic_models.Provenance("bia_ingest"),
                    "name": "specimen_imaging_preparation_protocol_uuid",
                    "value": {
                        "specimen_imaging_preparation_protocol_uuid": [
                            specimen_imaging_preparation_protocol_uuids[1]
                        ]
                    },
                },
                {
                    "provenance": semantic_models.Provenance("bia_ingest"),
                    "name": "bio_sample_uuid",
                    "value": {
                        "bio_sample_uuid": [bio_sample_uuids[2]],
                    },
                },
                {
                    "provenance": semantic_models.Provenance("bia_ingest"),
                    "name": "uuid_unique_input",
                    "value": {
                      "uuid_unique_input": unique_string_2,
                    }
                },
            ],
        },
        {
            "uuid": create_dataset_uuid(study_uuid, unique_string_3),
            "object_creator": "bia_ingest",
            "title": title_id_3,
            "submitted_in_study_uuid": study_uuid,
            "analysis_method": [],
            "correlation_method": [],
            "example_image_uri": [],
            "description": "Test annotation overview 1",
            "version": 0,
            "additional_metadata": [
                {
                    "provenance": semantic_models.Provenance("bia_ingest"),
                    "name": "annotation_method_uuid",
                    "value": {
                        "annotation_method_uuid": annotation_method_uuids,
                    },
                },
                {
                    "provenance": semantic_models.Provenance("bia_ingest"),
                    "name": "uuid_unique_input",
                    "value": {
                      "uuid_unique_input": unique_string_3,
                    }
                },
            ],
        },
    ]

    bia_objects = [
        bia_data_model.Dataset.model_validate(object_dict)
        for object_dict in object_dicts
    ]
    return bia_objects

def get_dataset_biostudies_default() -> bia_data_model.Dataset:

    study_title = "A default test study section with title greater than 25 characters"
    description = "A study description" 
    unique_string = "Default template. No Study Components"

    dataset_dict = {
        "uuid": create_dataset_uuid(study_uuid_biostudies_default, unique_string),
        "title": study_title,
        "description": description,
        "submitted_in_study_uuid": study_uuid_biostudies_default,
        "analysis_method": [],
        "correlation_method": [],
        "example_image_uri": [],
        "version": 0,
        "object_creator": "bia_ingest",
        "additional_metadata": [
          {
            "provenance": semantic_models.Provenance("bia_ingest"),
            "name": "uuid_unique_input",
            "value": {
              "uuid_unique_input": unique_string,
            }
          }
        ],
    }

    dataset = bia_data_model.Dataset.model_validate(dataset_dict)
    return dataset
