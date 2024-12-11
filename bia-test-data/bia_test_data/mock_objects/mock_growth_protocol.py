from typing import List
from bia_shared_datamodels import bia_data_model
from bia_shared_datamodels.uuid_creation import create_protocol_uuid
from .mock_object_constants import study_uuid


def get_growth_protocol() -> List[bia_data_model.Protocol]:

    title_id_1 = "Test specimen 1"
    title_id_2 = "Test specimen 2"
    object_dicts = [
        {
            "uuid": create_protocol_uuid(title_id_1, study_uuid),
            "title_id": title_id_1,
            "protocol_description": "Test growth protocol 1",
            "version": 0,
        },
        {
            "uuid": create_protocol_uuid(title_id_2, study_uuid),
            "title_id": title_id_2,
            "protocol_description": "Test growth protocol 2",
            "version": 0,
        },
    ]

    bia_objects = [
        bia_data_model.Protocol.model_validate(object_dict)
        for object_dict in object_dicts
    ]
    return bia_objects


def get_growth_protocol_as_map():
    return {obj.title_id + ".growth_protocol": obj for obj in get_growth_protocol()}
