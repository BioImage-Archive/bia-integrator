from typing import List
from bia_shared_datamodels import bia_data_model
from bia_shared_datamodels.uuid_creation import (
    create_image_acquisition_protocol_uuid,
)
from .mock_object_constants import study_uuid


def get_image_acquisition_protocol() -> List[bia_data_model.ImageAcquisitionProtocol]:

    title_id_1 = "Test Primary Screen Image Acquisition"
    title_id_2 = "Test Secondary Screen Image Acquisition"
    object_dicts = [
        {
            "uuid": create_image_acquisition_protocol_uuid(
                title_id_1, study_uuid
            ),
            "title_id": title_id_1,
            "protocol_description": "Test image acquisition parameters 1",
            "imaging_instrument_description": "Test imaging instrument 1",
            "imaging_method_name": [
                "confocal microscopy",
            ],
            "fbbi_id": [],
            "version": 0,
        },
        {
            "uuid": create_image_acquisition_protocol_uuid(
                title_id_2, study_uuid
            ),
            "title_id": title_id_2,
            "protocol_description": "Test image acquisition parameters 2",
            "imaging_instrument_description": "Test imaging instrument 2",
            "imaging_method_name": [
                "fluorescence microscopy"
            ],
            "fbbi_id": ["FBbi:00000246"],
            "version": 0,
        },
    ]
    bia_objects = [
        bia_data_model.ImageAcquisitionProtocol.model_validate(object_dict)
        for object_dict in object_dicts
    ]
    return bia_objects


def get_image_acquisition_protocol_as_map():
    return {obj.title_id: obj for obj in get_image_acquisition_protocol()}
