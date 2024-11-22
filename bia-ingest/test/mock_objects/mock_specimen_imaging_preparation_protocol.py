from typing import List
from bia_shared_datamodels import bia_data_model
from bia_ingest.bia_object_creation_utils import dict_to_uuid
from .utils import accession_id


def get_specimen_imaging_preparation_protocol() -> (
    List[bia_data_model.SpecimenImagingPreparationProtocol]
):
    # For UUID
    attributes_to_consider = [
        "accession_id",
        "accno",
        "title_id",
        "protocol_description",
    ]
    protocol_info = [
        {
            "accno": "Specimen-1",
            "accession_id": accession_id,
            "title_id": "Test specimen 1",
            "protocol_description": "Test sample preparation protocol 1",
            "signal_channel_information": [],
            "version": 0,
        },
        {
            "accno": "Specimen-2",
            "accession_id": accession_id,
            "title_id": "Test specimen 2",
            "protocol_description": "Test sample preparation protocol 2",
            "signal_channel_information": [],
            "version": 0,
        },
    ]

    protocol = []
    for protocol_dict in protocol_info:
        protocol_dict["uuid"] = dict_to_uuid(protocol_dict, attributes_to_consider)
        protocol_dict.pop("accno")
        protocol_dict.pop("accession_id")
        protocol.append(
            bia_data_model.SpecimenImagingPreparationProtocol.model_validate(
                protocol_dict
            )
        )
    return protocol


def get_specimen_imaging_preparation_protocol_as_map():
    return {obj.title_id: obj for obj in get_specimen_imaging_preparation_protocol()}
