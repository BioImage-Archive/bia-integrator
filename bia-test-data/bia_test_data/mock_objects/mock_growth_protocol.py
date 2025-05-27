from typing import List
from bia_shared_datamodels import bia_data_model, semantic_models
from bia_shared_datamodels.uuid_creation import create_protocol_uuid
from .mock_object_constants import study_uuid


def get_growth_protocol() -> List[bia_data_model.Protocol]:
    title_id_1 = "Test specimen 1"
    unique_string_1 = "Specimen-1"
    title_id_2 = "Test specimen 2"
    unique_string_2 = "Specimen-2"
    object_dicts = [
        {
            "object_creator": semantic_models.Provenance("bia_ingest"),
            "uuid": create_protocol_uuid(study_uuid, unique_string_1),
            "title": title_id_1,
            "protocol_description": "Test growth protocol 1",
            "version": 0,
            "additional_metadata": [
                {
                    "provenance": semantic_models.Provenance("bia_ingest"),
                    "name": "uuid_unique_input",
                    "value": {
                        "uuid_unique_input": unique_string_1,
                    },
                },
            ],
        },
        {
            "object_creator": semantic_models.Provenance("bia_ingest"),
            "uuid": create_protocol_uuid(study_uuid, unique_string_2),
            "title": title_id_2,
            "protocol_description": "Test growth protocol 2",
            "version": 0,
            "additional_metadata": [
                {
                    "provenance": semantic_models.Provenance("bia_ingest"),
                    "name": "uuid_unique_input",
                    "value": {
                        "uuid_unique_input": unique_string_2,
                    },
                },
            ],
        },
    ]

    bia_objects = [
        bia_data_model.Protocol.model_validate(object_dict)
        for object_dict in object_dicts
    ]
    return bia_objects


def get_growth_protocol_as_map():
    return {obj.title + ".growth_protocol": obj for obj in get_growth_protocol()}
