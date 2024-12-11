from typing import List
from bia_shared_datamodels import bia_data_model
from bia_shared_datamodels.uuid_creation import (
    create_specimen_imaging_preparation_protocol_uuid,
)
from .mock_object_constants import study_uuid


def get_specimen_imaging_preparation_protocol() -> (
    List[bia_data_model.SpecimenImagingPreparationProtocol]
):

    title_id_1 = "Test specimen 1"
    title_id_2 = "Test specimen 2"
    object_dicts = [
        {
            "uuid": create_specimen_imaging_preparation_protocol_uuid(
                title_id_1, study_uuid
            ),
            "title_id": title_id_1,
            "protocol_description": "Test sample preparation protocol 1",
            "signal_channel_information": [],
            "version": 0,
        },
        {
            "uuid": create_specimen_imaging_preparation_protocol_uuid(
                title_id_2, study_uuid
            ),
            "title_id": title_id_2,
            "protocol_description": "Test sample preparation protocol 2",
            "signal_channel_information": [],
            "version": 0,
        },
    ]

    bia_objects = [
        bia_data_model.SpecimenImagingPreparationProtocol.model_validate(object_dict)
        for object_dict in object_dicts
    ]
    return bia_objects


def get_specimen_imaging_preparation_protocol_as_map():
    return {obj.title_id: obj for obj in get_specimen_imaging_preparation_protocol()}
