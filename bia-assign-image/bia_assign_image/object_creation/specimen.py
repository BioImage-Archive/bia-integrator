from typing import List
from uuid import UUID
from bia_shared_datamodels import (
    bia_data_model,
    uuid_creation,
    semantic_models,
    attribute_models,
)
from bia_shared_datamodels.package_specific_uuid_creation import shared


def get_specimen(
    study_uuid: UUID,
    image_uuid: UUID,
    imaging_preparation_protocol_uuid: List[UUID],
    sample_of_uuid: List[UUID],
) -> bia_data_model.Specimen:

    specimen_uuid, specimen_uuid_attribute = shared.create_specimen_uuid(
        study_uuid,
        image_uuid,
        semantic_models.Provenance.bia_image_assignment,
    )

    model_dict = {
        "version": 0,
        "uuid": specimen_uuid,
        "imaging_preparation_protocol_uuid": imaging_preparation_protocol_uuid,
        "sample_of_uuid": sample_of_uuid,
        "object_creator": semantic_models.Provenance.bia_image_assignment,
        "additional_metadata": [],
    }

    model_dict["additional_metadata"].append(specimen_uuid_attribute.model_dump())

    return bia_data_model.Specimen.model_validate(model_dict)
