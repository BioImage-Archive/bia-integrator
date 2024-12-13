from typing import List
from uuid import UUID
from bia_shared_datamodels import bia_data_model, uuid_creation


def get_specimen(
    image_uuid: UUID,
    imaging_preparation_protocol_uuid: List[UUID],
    sample_of_uuid: List[UUID],
) -> bia_data_model.Specimen:
    model_dict = {
        "version": 0,
        "uuid": uuid_creation.create_specimen_uuid(image_uuid),
        "imaging_preparation_protocol_uuid": imaging_preparation_protocol_uuid,
        "sample_of_uuid": sample_of_uuid,
    }

    return bia_data_model.Specimen.model_validate(model_dict)
