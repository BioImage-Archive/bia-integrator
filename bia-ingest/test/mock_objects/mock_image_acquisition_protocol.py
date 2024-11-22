from typing import List
from bia_shared_datamodels import bia_data_model
from bia_ingest.bia_object_creation_utils import dict_to_uuid
from .utils import accession_id


def get_image_acquisition_protocol() -> List[bia_data_model.ImageAcquisitionProtocol]:
    attributes_to_consider = [
        "accession_id",
        "accno",
        "title_id",
        "protocol_description",
        "imaging_instrument_description",
        "imaging_method_name",
        "fbbi_id",
    ]
    image_acquisition_protocol_info = [
        {
            "accno": "Image acquisition-3",
            "accession_id": accession_id,
            "title_id": "Test Primary Screen Image Acquisition",
            "protocol_description": "Test image acquisition parameters 1",
            "imaging_instrument_description": "Test imaging instrument 1",
            "imaging_method_name": [
                "confocal microscopy",
            ],
            "fbbi_id": [],
            "version": 0,
        },
        {
            "accno": "Image acquisition-7",
            "accession_id": accession_id,
            "title_id": "Test Secondary Screen Image Acquisition",
            "protocol_description": "Test image acquisition parameters 2",
            "imaging_instrument_description": "Test imaging instrument 2",
            "imaging_method_name": [
                "fluorescence microscopy",
            ],
            "fbbi_id": [],
            "version": 0,
        },
    ]
    image_acquisition_protocol = []
    for image_acquisition_protocol_dict in image_acquisition_protocol_info:
        image_acquisition_protocol_dict["uuid"] = dict_to_uuid(
            image_acquisition_protocol_dict, attributes_to_consider
        )
        image_acquisition_protocol_dict.pop("accno")
        image_acquisition_protocol_dict.pop("accession_id")
        image_acquisition_protocol.append(
            bia_data_model.ImageAcquisitionProtocol.model_validate(
                image_acquisition_protocol_dict
            )
        )
    return image_acquisition_protocol

def get_image_acquisition_protocol_as_map():
    return {obj.title_id: obj for obj in get_image_acquisition_protocol()}
